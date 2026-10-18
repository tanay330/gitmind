
from gitmind.retrieval.router import search

TOP_K = 8

test_questions = [
    {
        "question": "Which SentenceTransformer model is initialized in embedder.py?",
        "expected_file": "src/gitmind/indexing/embedder.py",
    },
    {
        "question": "How does chunk_file choose between Python AST, Markdown, and generic chunking?",
        "expected_file": "src/gitmind/indexing/chunkers/__init__.py",
    },
    {
        "question": "How does GitMind fetch files from the GitHub API?",
        "expected_file": "src/gitmind/indexing/github_client.py",
    },
    {
        "question": "How are code chunks stored in Qdrant?",
        "expected_file": "src/gitmind/retrieval/qdrant_store.py",
    },
    {
        "question": "How does GitMind generate an answer using the retrieved context?",
        "expected_file": "src/gitmind/llm/client.py",
    },
]

successful = 0

for test in test_questions:
    question = test["question"]
    expected_file = test["expected_file"]

    results = search(question, top_k=TOP_K)

    retrieved_files = [
        (result.payload or {}).get("path", "")
        for result in results
    ]

    # Find the rank of the first chunk from the expected file.
    expected_rank = next(
        (
            rank
            for rank, path in enumerate(retrieved_files, start=1)
            if path == expected_file
        ),
        None,
    )

    found = expected_rank is not None

    if found:
        successful += 1

    print("\n" + "=" * 70)
    print("Question:", question)
    print("Expected file:", expected_file)

    if found:
        print(f"Expected file found at rank: {expected_rank}")
    else:
        print(f"Expected file not found in top {TOP_K}")

    for rank, result in enumerate(results, start=1):
        payload = result.payload or {}

        print(
            f"{rank}. Score: {result.score:.4f} | "
            f"File: {payload.get('path')} | "
            f"Type: {payload.get('chunk_type')}"
        )

print("\n" + "=" * 70)
print("RETRIEVAL EVALUATION SUMMARY")
print("Total questions:", len(test_questions))
print("Expected files retrieved:", successful)
print(f"Recall@{TOP_K}: {successful / len(test_questions) * 100:.2f}%")
