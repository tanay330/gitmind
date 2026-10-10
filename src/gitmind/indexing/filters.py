from pathlib import Path

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "dist",
    "build",
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
def should_include(path:str,size:int)-> bool:
    parts=path.split("/")
    has_ignored=any(item in IGNORED_DIRS for item in parts)
    if has_ignored:
        return False
    if size>MAX_FILE_SIZE:
        return False
    extension=Path(path).suffix
    if extension in IGNORED_EXTENSIONS:
        return False
    return True
    
    
    