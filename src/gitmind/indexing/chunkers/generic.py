from gitmind.models import Chunk

WINDOW_LINES = 40
OVERLAP_LINES = 8


def chunk_generic(content: str, path: str, repo_id: str, language: str = "text") -> list[Chunk]:
    lines = content.splitlines()
    step = WINDOW_LINES - OVERLAP_LINES
    chunks = []
    start = 0

    while start < len(lines):
        end = min(start + WINDOW_LINES, len(lines))
        text = "\n".join(lines[start:end])

        if text.strip():
            chunks.append(
                Chunk(
                    repo_id=repo_id,
                    path=path,
                    symbol_name=f"lines {start + 1}-{end}",
                    symbol_type="block",
                    start_line=start + 1,
                    end_line=end,
                    language=language,
                    text=text,
                )
            )

        if end == len(lines):
            break
        start += step

    return chunks