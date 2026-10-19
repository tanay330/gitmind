import sys

from gitmind.retrieval.search import search

repo_id = sys.argv[1]
question = " ".join(sys.argv[2:])

for rank, point in enumerate(search(question, repo_id), start=1):
    p = point.payload
    text = " ".join(p["text"].split())[:80]
    print(f"{rank}. {p['path']}:{p['start_line']}-{p['end_line']} [{p['symbol_name']}] {text!r}")