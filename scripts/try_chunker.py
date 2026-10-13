from gitmind.indexing.chunkers.python_ast import chunk_python_ast

text = """
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str):
    return model.encode(text).tolist()
"""

chunks = chunk_python_ast(text, "embedder.py")

for chunk in chunks:
    print("---- CHUNK ----")
    print(chunk.text)