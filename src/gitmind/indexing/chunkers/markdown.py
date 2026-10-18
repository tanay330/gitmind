import re

from gitmind.models import Chunk

HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
INTRO = "<intro>"
MAX_SECTION_LINES = 80


def _find_sections(lines: list[str]) -> list[tuple[str, int, int]]:
    sections = []
    title = INTRO
    start = 1
    body_lines = 0
    in_code = False

    for number, line in enumerate(lines, start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_code = not in_code
            body_lines += 1
            continue

        match = None if in_code else HEADING.match(line)
        if match:
            if body_lines > 0:
                sections.append((title, start, number - 1))
                start = number
            elif title == INTRO:
                start = number
            title = match.group(2)
            body_lines = 0
        elif line.strip():
            body_lines += 1

    sections.append((title, start, len(lines)))
    return sections


def chunk_markdown(content: str, path: str, repo_id: str) -> list[Chunk]:
    lines = content.splitlines()
    chunks = []

    for title, start, end in _find_sections(lines):
        length = end - start + 1
        for index, part_start in enumerate(range(start, end + 1, MAX_SECTION_LINES), start=1):
            part_end = min(part_start + MAX_SECTION_LINES - 1, end)
            text = "\n".join(lines[part_start - 1 : part_end])
            if not text.strip():
                continue
            name = title if length <= MAX_SECTION_LINES else f"{title} (part {index})"
            chunks.append(
                Chunk(
                    repo_id=repo_id,
                    path=path,
                    symbol_name=name,
                    symbol_type="section",
                    start_line=part_start,
                    end_line=part_end,
                    language="markdown",
                    text=text,
                )
            )
    return chunks