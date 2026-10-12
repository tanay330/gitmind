from gitmind.retrieval.qdrant_store import client

collection_name = "gitmind_code"

info = client.get_collection(collection_name)

print(f"Points in Qdrant: {info.points_count}")