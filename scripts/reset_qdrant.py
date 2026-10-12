from gitmind.retrieval.qdrant_store import client

collection_name = "gitmind_code"

if client.collection_exists(collection_name):
    client.delete_collection(collection_name)
    print(f"Deleted collection: {collection_name}")
else:
    print(f"Collection does not exist: {collection_name}")