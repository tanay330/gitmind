from gitmind.retrieval.router import search

results = search(
    "How does GitMind fetch and process GitHub repository files?",
    top_k=5
)

for result in results:
    print(f"Score: {result.score}")
    print(f"File: {result.payload['path']}")
    print(f"Content: {result.payload['text'][:300]}")
    print("-" * 50)