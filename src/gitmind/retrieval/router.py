from gitmind.indexing.embedder import embed_text
from gitmind.retrieval.qdrant_store import client

def search(query:str,top_k:int):
    query_vector=embed_text(query)
    results = client.query_points(
            collection_name="gitmind_code",
            query=query_vector,
            limit=top_k,
            with_payload=True,
        ).points
    return results
    