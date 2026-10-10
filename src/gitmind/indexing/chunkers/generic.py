from gitmind.indexing.chunkers.models import Chunk

from gitmind.indexing.chunkers.models import Chunk

Chunk_size = 1000
Chunk_overlap = 200


def chunk_generic(text: str, path: str):

    chunks = []

    for start in range(0, len(text), Chunk_size - Chunk_overlap):

        chunk_text = text[start:start + Chunk_size]

        chunk = Chunk(
            text=chunk_text,
            path=path,
            chunk_type="generic"
        )

        chunks.append(chunk)

    return chunks
