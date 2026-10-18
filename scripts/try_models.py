from gitmind.models import Chunk, make_repo_id

chunk = Chunk(
    repo_id=make_repo_id("tanay330", "GitMind"),
    path="src/gitmind/indexing/embedder.py",
    symbol_name="embed_text",
    symbol_type="function",
    start_line=5,
    end_line=9,
    language="python",
    text="def embed_text(text):\n    return model.encode(text)",
)

print(chunk.repo_id)
print(chunk.id)
print(chunk.embedding_text())