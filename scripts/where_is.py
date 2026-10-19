import sys

from gitmind.retrieval.search import CANDIDATES, reciprocal_rank_fusion, strip_repo_name
from gitmind.retrieval.store import search_dense, search_sparse

repo_id, path, *words = sys.argv[1:]
question = " ".join(words)
query = strip_repo_name(question, repo_id)

LIMIT = 50
dense = search_dense(query, repo_id, limit=LIMIT)
sparse = search_sparse(query, repo_id, limit=LIMIT)
fused = [
    point
    for point, _ in reciprocal_rank_fusion([dense[:CANDIDATES], sparse[:CANDIDATES]])
]


def ranks(points):
    return [
        (rank, p.payload["symbol_name"], p.payload["end_line"] - p.payload["start_line"] + 1)
        for rank, p in enumerate(points, start=1)
        if p.payload["path"] == path
    ]


print("query used:", query)
print("dense  ranks:", ranks(dense) or f"not in top {LIMIT}")
print("sparse ranks:", ranks(sparse) or f"not in top {LIMIT}")
print("fused  ranks:", ranks(fused) or f"not in the {len(fused)} fused results")