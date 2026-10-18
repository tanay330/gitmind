from dataclasses import dataclass

from gitmind.indexing.embedder import embed_text
from gitmind.retrieval.qdrant_store import client
from fastembed import SparseTextEmbedding
from qdrant_client.models import SparseVector

from gitmind.retrieval.reranker import rerank

sparse_model = SparseTextEmbedding(
    model_name="Qdrant/bm25"
)

def reciprocal_rank_fusion(dense_results, sparse_results, k=60):
    scores = {}
    points = {}

    for results in [dense_results, sparse_results]:
        for rank, point in enumerate(results, start=1):
            point_id = point.id

            if point_id not in scores:
                scores[point_id] = 0.0
                points[point_id] = point

            scores[point_id] += 1 / (k + rank)

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    return [
        FusedResult(
            point=points[point_id],
            score=scores[point_id],
        )
        for point_id in ranked_ids
    ]

def search(query: str, top_k: int = 5, candidate_k: int = 20):
    query_vector = embed_text(query)
    sparse_embedding = list(sparse_model.embed([query]))[0]

    sparse_vector = SparseVector(
        indices=sparse_embedding.indices.tolist(),
        values=sparse_embedding.values.tolist(),
    )

    # Retrieve more candidates from sparse search
    sparse_results = client.query_points(
        collection_name="gitmind_code",
        query=sparse_vector,
        using="sparse",
        limit=candidate_k,
        with_payload=True,
    ).points

    # Retrieve more candidates from dense search
    dense_results = client.query_points(
        collection_name="gitmind_code",
        query=query_vector,
        using="dense",
        limit=candidate_k,
        with_payload=True,
    ).points

    # Temporary diagnostics
    for name, results in [
        ("DENSE", dense_results),
        ("SPARSE", sparse_results),
    ]:
        print(f"\n--- {name} RESULTS ---")

        for rank, point in enumerate(results, start=1):
            payload = point.payload or {}
            print(
                f"{rank}. Score: {point.score:.4f} | "
                f"File: {payload.get('path')} | "
                f"Text: {payload.get('text', '')[:100]!r}"
            )

    # Fuse both candidate lists
    fused_results = reciprocal_rank_fusion(
    dense_results,
    sparse_results,
)

    print("\n--- RRF TOP 5: BEFORE RERANKING ---")

    for rank, result in enumerate(fused_results[:5], start=1):
        payload = result.payload or {}
        text_preview = payload.get("text", "").replace("\n", " ")[:150]

        print(
            f"{rank}. RRF: {result.score:.4f} | "
            f"File: {payload.get('path')}"
        )
        print(f"   Text: {text_preview!r}")

    # Apply reranking to all fused candidates
    reranked_results = rerank(
        query=query,
        results=fused_results,
        top_k=top_k,
    )

    return reranked_results

@dataclass
class FusedResult:
    point: object
    score: float

    @property
    def id(self):
        return self.point.id

    @property
    def payload(self):
        return self.point.payload
    