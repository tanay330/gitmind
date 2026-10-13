
from gitmind.retrieval.router import search
from gitmind.llm.client import generate_answer


def test_rag():
    question = input("\nEnter your question: ")

    # Step 1: Retrieve relevant chunks from Qdrant
    top_k = 8
    results = search(question, top_k=top_k)

    print("\n" + "=" * 60)
    print("RETRIEVED CHUNKS")
    print("=" * 60)

    if not results:
        print("No relevant chunks found.")
        return

    # Step 2: Display each retrieved chunk
    for index, result in enumerate(results, start=1):
        payload = result.payload or {}

        print(f"\nChunk #{index}")
        print(f"File path: {payload.get('path', 'Unknown')}")
        print(f"Chunk type: {payload.get('chunk_type', 'Unknown')}")
        print(f"Similarity score: {result.score:.4f}")
        print("-" * 40)
        print(payload.get("text", "No text available"))

    # Step 3: Build context for the LLM
    context_parts = []

    for result in results:
        payload = result.payload or {}
        text = payload.get("text", "")
        path = payload.get("path", "Unknown")

        if text:
            context_parts.append(
                f"File: {path}\nContent:\n{text}"
            )

    context = "\n\n".join(context_parts)

    # Step 4: Generate the final answer
    answer = generate_answer(question, context)

    print("\n" + "=" * 60)
    print("FINAL RAG ANSWER")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    test_rag()
