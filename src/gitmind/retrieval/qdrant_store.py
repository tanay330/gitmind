from uuid import uuid4
from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from gitmind.config import settings
from gitmind.indexing.chunkers.models import Chunk
from gitmind.indexing.embedder import embed_texts


client = QdrantClient(url=settings.qdrant_url)

sparse_model = SparseTextEmbedding(
    model_name="Qdrant/bm25"
)

COLLECTION_NAME = "gitmind_code"


def create_collection(collection_name: str):
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                    index=SparseIndexParams()
                )
            },
        )



def build_points(chunks: list[Chunk], repo_url: str) -> list[PointStruct]:
    if not chunks:
        return []

    contextual_texts = [
        (
            f"File: {chunk.path}\n"
            f"Chunk type: {chunk.chunk_type}\n\n"
            f"{chunk.text}"
        )
        for chunk in chunks
    ]

    dense_vectors = embed_texts(contextual_texts)

    sparse_embeddings = list(sparse_model.embed(contextual_texts))

    points = []

    for chunk, dense_vector, sparse_embedding in zip(
        chunks, dense_vectors, sparse_embeddings
    ):
        point = PointStruct(
            id=str(uuid4()),
            vector={
                "dense": dense_vector,
                "sparse": SparseVector(
                    indices=sparse_embedding.indices.tolist(),
                    values=sparse_embedding.values.tolist(),
                ),
            },
            payload={
                "text": chunk.text,
                "path": chunk.path,
                "chunk_type": chunk.chunk_type,
                "repo_url": repo_url,
            },
        )

        points.append(point)

    return points



def store_points(points: list[PointStruct]) -> None:
    if not points:
        return

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True,
    )


def delete_repository_chunks(repo_url: str):
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="repo_url",
                    match=MatchValue(value=repo_url),
                )
            ]
        ),
    )

def recreate_collection(collection_name: str):
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)

    create_collection(collection_name)    
   
            
            