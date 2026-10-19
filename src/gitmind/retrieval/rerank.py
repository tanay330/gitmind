from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_model = None


def _get_model() -> CrossEncoder:
    global _model
    if _model is None:
        _model = CrossEncoder(MODEL_NAME)
    return _model


def rerank(question: str, points: list, top_k: int = 8) -> list:
    if not points:
        return []

    pairs = []
    for point in points:
        p = point.payload
        candidate = f"{p['path']} | {p['symbol_name']}\n{p['text']}"
        pairs.append((question, candidate))

    scores = _get_model().predict(pairs)
    ranked = sorted(zip(points, scores), key=lambda item: float(item[1]), reverse=True)
    return [point for point, _ in ranked[:top_k]]