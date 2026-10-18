from pathlib import Path

from gitmind.indexing.chunkers.generic import chunk_generic
from gitmind.indexing.chunkers.markdown import chunk_markdown
from gitmind.indexing.chunkers.python_ast import chunk_python
from gitmind.models import Chunk

LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".md": "markdown",
    ".rst": "rst",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".json": "json",
    ".txt": "text",
}

MARKDOWN_EXTENSIONS = {".md", ".markdown"}


def chunk_file(content: str, path: str, repo_id: str) -> list[Chunk]:
    extension = Path(path).suffix.lower()
    language = LANGUAGES.get(extension, "text")

    if extension == ".py":
        try:
            return chunk_python(content, path, repo_id)
        except (SyntaxError, ValueError):
            pass  # not valid Python: fall through to generic chunking below

    if extension in MARKDOWN_EXTENSIONS:
        return chunk_markdown(content, path, repo_id)

    return chunk_generic(content, path, repo_id, language)