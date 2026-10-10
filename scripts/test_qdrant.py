from gitmind.retrieval.qdrant_store import client,create_collection,store_chunk
from gitmind.indexing.chunkers.models import Chunk
try:
    collections = client.get_collections()
    print("Connected to Qdrant successfully!")
    print("Existing collections:", collections.collections)

except Exception as e:
    print("Could not connect to Qdrant.")
    print("Error:", e)
    
COLLECTION_NAME = "gitmind_code"

try:
    create_collection(COLLECTION_NAME)

    print(f"Collection '{COLLECTION_NAME}' is ready!")

    info = client.get_collection(COLLECTION_NAME)
    print("Vector size:", info.config.params.vectors.size)
    print("Distance:", info.config.params.vectors.distance)

except Exception as e:
    print("Error:", e)

chunk = Chunk(
    text="GitMind uses FastAPI to build APIs.",
    path="README.md",
    chunk_type="generic"
)

store_chunk(chunk)

print("Chunk stored successfully!")

result = client.scroll(
    collection_name="gitmind_code",
    limit=5,
    with_payload=True,
    with_vectors=False
)

for point in result[0]:
    print("ID:", point.id)
    print("Payload:", point.payload)    