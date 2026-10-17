
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> list[float]:
    return model.encode(text).tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
    )

    return embeddings.tolist()
