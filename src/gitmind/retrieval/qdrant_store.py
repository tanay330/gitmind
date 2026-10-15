from uuid import uuid4
from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from gitmind.config import settings
from gitmind.indexing.chunkers.models import Chunk
from gitmind.indexing.embedder import embed_text


client = QdrantClient(url=settings.qdrant_url)

sparse_model = SparseTextEmbedding(
    model_name="Qdrant/bm25"
)

COLLECTION_NAME = "gitmind_code"


def create_collection(collection_name: str):
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                    index=SparseIndexParams()
                )
            },
        )


def store_chunk(chunk: Chunk, repo_url: str):
    dense_vector = embed_text(chunk.text)

    sparse_embedding = list(
        sparse_model.embed([chunk.text])
    )[0]

    point = PointStruct(
        id=str(uuid4()),
        vector={
            "dense": dense_vector,
            "sparse": SparseVector(
                indices=sparse_embedding.indices.tolist(),
                values=sparse_embedding.values.tolist(),
            ),
        },
        payload={
            "text": chunk.text,
            "path": chunk.path,
            "chunk_type": chunk.chunk_type,
            "repo_url": repo_url,
        },
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point],
    )

    return True


def delete_repository_chunks(repo_url: str):
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="repo_url",
                    match=MatchValue(value=repo_url),
                )
            ]
        ),
    )

def recreate_collection(collection_name: str):
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)

    create_collection(collection_name)    
   
            
            