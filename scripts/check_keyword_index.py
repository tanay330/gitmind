from qdrant_client.models import FieldCondition, Filter, MatchValue

from gitmind.retrieval.store import COLLECTION, client, sparse_model

repo_id = "psf/requests"
path = "src/requests/__version__.py"

points, _ = client.scroll(
    collection_name=COLLECTION,
    scroll_filter=Filter(
        must=[
            FieldCondition(key="repo_id", match=MatchValue(value=repo_id)),
            FieldCondition(key="path", match=MatchValue(value=path)),
        ]
    ),
    limit=1,
    with_payload=True,
    with_vectors=["sparse"],
)

stored = set(points[0].vector["sparse"].indices)
version_token = set(next(iter(sparse_model.embed(["version"]))).indices.tolist())

print("tokens stored for this chunk:", len(stored))
print("'version' is in the stored keyword vector:", bool(version_token & stored))