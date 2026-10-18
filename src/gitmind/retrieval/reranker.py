
from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(query: str, results: list, top_k: int = 5):
    if not results:
        return []

    pairs = []

    for result in results:
        payload = result.payload or {}

        candidate_text = (
            f"File path: {payload.get('path', 'unknown')}\n"
            f"Chunk type: {payload.get('chunk_type', 'unknown')}\n\n"
            f"{payload.get('text', '')}"
        )

        pairs.append((query, candidate_text))

    scores = model.predict(pairs)

    ranked_results = sorted(
        zip(results, scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )

    print("\nRERANKER TOP RESULTS")
    for rank, (result, score) in enumerate(
        ranked_results[:top_k], start=1
    ):
        print(
            f"{rank}. {result.payload.get('path')} "
            f"| Reranker score: {float(score):.4f} "
            f"| RRF score: {result.score:.4f}"
        )

    return [result for result, _ in ranked_results[:top_k]]
