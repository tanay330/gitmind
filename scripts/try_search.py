
from gitmind.retrieval.router import search

test_cases = [
    {
        "original": "Which embedding model does GitMind use?",
        "rewritten": (
            "GitMind embedding model SentenceTransformer "
            "all-MiniLM-L6-v2"
        ),
        "expected_file": "src/gitmind/indexing/embedder.py",
    },
    {
        "original": (
            "How does chunk_file choose between Python AST, "
            "Markdown, and generic chunking?"
        ),
        "rewritten": (
            "chunk_file dispatch by file extension .py .md "
            "Python AST Markdown generic chunker"
        ),
        "expected_file": "src/gitmind/indexing/chunkers/__init__.py",
    },
    {
        "original": "How does GitMind fetch files from the GitHub API?",
        "rewritten": (
            "GitHub REST API get_repo_info list_repo_files "
            "fetch_file owner repo default_branch"
        ),
        "expected_file": "src/gitmind/indexing/github_client.py",
    },
    {
        "original": "How are code chunks stored in Qdrant?",
        "rewritten": (
            "Qdrant store_chunk PointStruct client.upsert "
            "vector payload chunk text path repo_url"
        ),
        "expected_file": "src/gitmind/retrieval/qdrant_store.py",
    },
    {
        "original": (
            "How does GitMind generate an answer using "
            "the retrieved context?"
        ),
        "rewritten": (
            "generate_answer Groq chat completions "
            "SYSTEM_PROMPT question context response"
        ),
        "expected_file": "src/gitmind/llm/client.py",
    },
]

TOP_K = 8

for case in test_cases:
    print("\n" + "=" * 75)
    print("Expected file:", case["expected_file"])

    for label in ("original", "rewritten"):
        question = case[label]
        results = search(question, top_k=TOP_K)

        paths = [
            (result.payload or {}).get("path", "")
            for result in results
        ]

        rank = next(
            (
                i
                for i, path in enumerate(paths, start=1)
                if path == case["expected_file"]
            ),
            None,
        )

        print(f"\n{label.title()} query: {question}")
        print("Expected file rank:", rank or "Not in top 8")

        for i, result in enumerate(results, start=1):
            payload = result.payload or {}
            print(
                f"{i}. {result.score:.4f} | "
                f"{payload.get('path')} | "
                f"{payload.get('chunk_type')}"
            )
