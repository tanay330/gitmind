from gitmind.retrieval.router import search

results = search("How does GitMind build APIs?", 3)

for result in results:
    print("Score:", result.score)
    print("Payload:", result.payload)
    print("-" * 50)