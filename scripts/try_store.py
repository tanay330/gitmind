import sys

from gitmind.models import Chunk
from gitmind.retrieval.store import (
    count_repo,
    delete_repo,
    ensure_collection,
    search_dense,
    search_sparse,
    upsert_chunks,
)

A = "tanay330/gitmind"
B = "psf/requests"


def make_chunk(repo_id, path, symbol, text, start=1):
    return Chunk(
        repo_id=repo_id,
        path=path,
        symbol_name=symbol,
        symbol_type="function",
        start_line=start,
        end_line=start + 2,
        language="python",
        text=text,
    )


ensure_collection()
upsert_chunks(
    [
        make_chunk(A, "src/gitmind/indexing/embedder.py", "<module>",
                   'from sentence_transformers import SentenceTransformer\n'
                   'model = SentenceTransformer("all-MiniLM-L6-v2")'),
        make_chunk(A, "src/gitmind/llm/client.py", "generate_answer",
                   'def generate_answer(question):\n'
                   '    return client.chat(model="openai/gpt-oss-120b")'),
        make_chunk(B, "src/requests/models.py", "Response",
                   'class Response:\n    """The Response object holds a server response."""'),
        make_chunk(B, "src/requests/sessions.py", "Session",
                   'class Session:\n    """Provides cookie persistence and connection pooling."""'),
    ]
)

print("gitmind chunks:", count_repo(A))
print("requests chunks:", count_repo(B))

query = "which model does it use"
for repo in (A, B):
    print(f"\n--- dense, filtered to {repo}")
    for p in search_dense(query, repo):
        print(p.payload["repo_id"], "|", p.payload["path"], "|", round(p.score, 3))
    print(f"--- sparse, filtered to {repo}")
    for p in search_sparse(query, repo):
        print(p.payload["repo_id"], "|", p.payload["path"], "|", round(p.score, 3))

if "--cleanup" in sys.argv:
    delete_repo(A)
    delete_repo(B)
    print("\ncleaned up")