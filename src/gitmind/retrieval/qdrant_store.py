from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from gitmind.indexing.chunkers.models import Chunk
from gitmind.config import settings
from uuid import uuid4
from gitmind.indexing.embedder import embed_text

client = QdrantClient(url=settings.qdrant_url)

def create_collection(collection_name: str):
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )

def store_chunk(chunk:Chunk):
    vector_embedding = embed_text(chunk.text)
    point=PointStruct(
        id=str(uuid4()),
        vector=vector_embedding,
        payload={"text":chunk.text,
                 "path":chunk.path,
                 "chunk_type":chunk.chunk_type
                 }
    )
    client.upsert(
    collection_name="gitmind_code",
    points=[point]
)
    return True
    
   
            
            