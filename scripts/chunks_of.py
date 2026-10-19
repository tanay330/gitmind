import sys

from qdrant_client.models import FieldCondition, Filter, MatchValue

from gitmind.retrieval.store import COLLECTION, client

repo_id, path = sys.argv[1], sys.argv[2]

points, _ = client.scroll(
    collection_name=COLLECTION,
    scroll_filter=Filter(
        must=[
            FieldCondition(key="repo_id", match=MatchValue(value=repo_id)),
            FieldCondition(key="path", match=MatchValue(value=path)),
        ]
    ),
    limit=20,
    with_payload=True,
)

print(f"{len(points)} chunk(s) for {path}")
for point in points:
    p = point.payload
    print(f"- {p['symbol_name']} lines {p['start_line']}-{p['end_line']}")
    print(p["text"][:400])