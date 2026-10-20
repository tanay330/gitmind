from gitmind.retrieval.ranking import (
    merge_with_guarantee,
    reciprocal_rank_fusion,
    strip_repo_name,
)
from gitmind.retrieval.store import search_dense, search_sparse

CANDIDATES = 20
RERANK_CANDIDATES = 50
RERANK_POOL = 40


def search(
    question: str,
    repo_id: str,
    top_k: int = 8,
    use_rerank: bool = False,
    guarantee: int = 2,
):
    query = strip_repo_name(question, repo_id)
    pool = RERANK_CANDIDATES if use_rerank else CANDIDATES

    dense = search_dense(query, repo_id, limit=pool)
    sparse = search_sparse(query, repo_id, limit=pool)
    fused = [point for point, _ in reciprocal_rank_fusion([dense, sparse])]

    if use_rerank:
        from gitmind.retrieval.rerank import rerank

        return rerank(question, fused[:RERANK_POOL], top_k=top_k)

    return merge_with_guarantee(fused, dense, sparse, top_k, guarantee)