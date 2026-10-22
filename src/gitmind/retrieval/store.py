from dataclasses import asdict
from gitmind.models import Chunk, split_identifiers
from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    Modifier,
    PayloadSchemaType,
    PointStruct,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from gitmind.config import settings
from gitmind.indexing.embedder import embed_text, embed_texts
from gitmind.models import Chunk

COLLECTION = settings.qdrant_collection
DENSE_SIZE = 384  # output size of all-MiniLM-L6-v2

client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key if settings.qdrant_url.startswith("https") else None,
)

sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")


def ensure_collection() -> None:
    if client.collection_exists(COLLECTION):
        return

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config={
            "dense": VectorParams(size=DENSE_SIZE, distance=Distance.COSINE)
        },
        sparse_vectors_config={
            "sparse": SparseVectorParams(
                index=SparseIndexParams(),
                modifier=Modifier.IDF,
            )
        },
    )

    for field in ("repo_id", "path"):
        client.create_payload_index(
            collection_name=COLLECTION,
            field_name=field,
            field_schema=PayloadSchemaType.KEYWORD,
        )


def _repo_filter(repo_id: str) -> Filter:
    return Filter(
        must=[FieldCondition(key="repo_id", match=MatchValue(value=repo_id))]
    )


def upsert_chunks(chunks: list[Chunk]) -> None:
    if not chunks:
        return

    texts = [chunk.embedding_text() for chunk in chunks]
    dense_vectors = embed_texts(texts)
    sparse_vectors = list(sparse_model.embed([chunk.keyword_text() for chunk in chunks]))

    points = []
    for chunk, dense, sparse in zip(chunks, dense_vectors, sparse_vectors):
        points.append(
            PointStruct(
                id=chunk.id,
                vector={
                    "dense": dense,
                    "sparse": SparseVector(
                        indices=sparse.indices.tolist(),
                        values=sparse.values.tolist(),
                    ),
                },
                payload=asdict(chunk),
            )
        )

    client.upsert(collection_name=COLLECTION, points=points, wait=True)


def search_dense(query: str, repo_id: str, limit: int = 20):
    return client.query_points(
        collection_name=COLLECTION,
        query=embed_text(query),
        using="dense",
        query_filter=_repo_filter(repo_id),
        limit=limit,
        with_payload=True,
    ).points


def search_sparse(query: str, repo_id: str, limit: int = 20):
    
    query_text = f"{query} {split_identifiers(query)}".strip()
    embedding = list(sparse_model.query_embed(query_text))[0]
    vector = SparseVector(
        indices=embedding.indices.tolist(),
        values=embedding.values.tolist(),
    )
    return client.query_points(
        collection_name=COLLECTION,
        query=vector,
        using="sparse",
        query_filter=_repo_filter(repo_id),
        limit=limit,
        with_payload=True,
    ).points


def count_repo(repo_id: str) -> int:
    return client.count(
        collection_name=COLLECTION,
        count_filter=_repo_filter(repo_id),
        exact=True,
    ).count


def delete_repo(repo_id: str) -> None:
    client.delete(
        collection_name=COLLECTION,
        points_selector=_repo_filter(repo_id),
    )

def list_repos() -> list[dict]:
    if not client.collection_exists(COLLECTION):
        return []

    counts: dict[str, int] = {}
    try:
        response = client.facet(
            collection_name=COLLECTION, key="repo_id", limit=1000, exact=True
        )
        for hit in response.hits:
            counts[hit.value] = hit.count
    except Exception:
        # Older Qdrant versions have no facet API: count by scrolling instead.
        offset = None
        while True:
            points, offset = client.scroll(
                collection_name=COLLECTION,
                limit=1000,
                offset=offset,
                with_payload=["repo_id"],
                with_vectors=False,
            )
            for point in points:
                repo_id = point.payload["repo_id"]
                counts[repo_id] = counts.get(repo_id, 0) + 1
            if offset is None:
                break

    return [{"repo_id": name, "chunks": number} for name, number in sorted(counts.items())]    