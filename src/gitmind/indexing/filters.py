from pathlib import PurePosixPath

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs",
    ".c", ".h", ".cpp",
    ".md", ".markdown", ".rst", ".txt",
    ".yaml", ".yml", ".toml", ".json",
}

ALLOWED_FILENAMES = {"dockerfile", "makefile", "go.mod"}

IGNORED_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    "vendor", ".next", "target", ".tox", ".idea", ".vscode","scripts","eval",
}

IGNORED_FILENAMES = {"package-lock.json", "pnpm-lock.yaml"}
IGNORED_SUFFIXES = (".min.js",)

IGNORED_DOC_LANGUAGES = {
    "hi", "zh", "zh-hant", "ja", "fr", "de", "es", "it", "pt", "ru", "tr", "ko",
}

MAX_FILE_SIZE = 200_000


def should_include(path: str, size: int) -> bool:
    if size == 0 or size > MAX_FILE_SIZE:
        return False

    p = PurePosixPath(path)
    parts = p.parts
    name = p.name.lower()

    if any(folder.lower() in IGNORED_DIRS for folder in parts[:-1]):
        return False

    if len(parts) >= 3 and parts[0] == "docs" and parts[1] in IGNORED_DOC_LANGUAGES:
        return False

    if name in IGNORED_FILENAMES or name.endswith(IGNORED_SUFFIXES):
        return False

    return p.suffix.lower() in ALLOWED_EXTENSIONS or name in ALLOWED_FILENAMES