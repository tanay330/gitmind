from gitmind.indexing.embedder import embed_text
from gitmind.retrieval.qdrant_store import client
from fastembed import SparseTextEmbedding
from qdrant_client.models import SparseVector


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
                scores[point_id] = 0
                points[point_id] = point

            scores[point_id] += 1 / (k + rank)

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    return [points[point_id] for point_id in ranked_ids]

def search(query:str,top_k:int):
    query_vector=embed_text(query)
    sparse_embedding = list(sparse_model.embed([query]))[0]

    sparse_vector = SparseVector(
    indices=sparse_embedding.indices.tolist(),
    values=sparse_embedding.values.tolist(),
    )
    sparse_results = client.query_points(
    collection_name="gitmind_code",
    query=sparse_vector,
    using="sparse",
    limit=top_k,
    with_payload=True,
    ).points
    dense_results = client.query_points(
            collection_name="gitmind_code",
            query=query_vector,
            using="dense",
            limit=top_k,
            with_payload=True,
        ).points
    
    fused_results = reciprocal_rank_fusion(
    dense_results,
    sparse_results,
)

    return fused_results[:top_k] 



    