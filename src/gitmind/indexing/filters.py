
from pathlib import Path

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "dist",
    "build",
    "scripts",
}

IGNORED_DOC_LANGUAGES = {
    "hi",
    "zh",
    "zh-hant",
    "ja",
    "fr",
    "de",
    "es",
    "it",
    "pt",
    "ru",
    "tr",
    "ko",
}

MAX_FILE_SIZE = 1_000_000

IGNORED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".zip",
    ".exe",
}


def should_include(path: str, size: int) -> bool:
    parts = path.split("/")

    if any(item in IGNORED_DIRS for item in parts):
        return False

    # Exclude translated documentation, but preserve English docs
    if len(parts) >= 3 and parts[0] == "docs":
        if parts[1] in IGNORED_DOC_LANGUAGES:
            return False

    if size > MAX_FILE_SIZE:
        return False

    extension = Path(path).suffix.lower()

    if extension in IGNORED_EXTENSIONS:
        return False

    return True
