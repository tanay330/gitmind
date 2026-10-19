from gitmind.retrieval.store import sparse_model


def token_ids(text: str) -> set[int]:
    embedding = next(iter(sparse_model.embed([text])))
    return set(embedding.indices.tolist())


pairs = [
    ("version", "__version__"),
    ("redirects", "resolve_redirects"),
    ("netrc auth", "get_netrc_auth"),
    ("session", "Session"),
]

for words, identifier in pairs:
    shared = token_ids(words) & token_ids(identifier)
    print(f"{words!r:14} vs {identifier!r:20} shared tokens: {len(shared)}")