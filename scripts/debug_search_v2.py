import sys

from gitmind.retrieval.store import search_dense, search_sparse
from gitmind.retrieval.search import strip_repo_name
repo_id = sys.argv[1]
question = " ".join(sys.argv[2:])


def show(title, points):
    print(f"\n--- {title}")
    for rank, point in enumerate(points[:8], start=1):
        p = point.payload
        print(
            f"{rank}. {p['path']}:{p['start_line']}-{p['end_line']} "
            f"[{p['symbol_name']}] score={point.score:.3f}"
        )
query = strip_repo_name(question, repo_id)
print("query used:", query)
show("DENSE", search_dense(query, repo_id))
show("SPARSE (keyword)", search_sparse(query, repo_id))