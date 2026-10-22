"""List the source files the running app really uses.

Starts at gitmind.api.main and follows every import (including imports written
inside functions) that points into src/gitmind.

Usage:  uv run python scripts/list_used_files.py
"""
import ast
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
ENTRY = "gitmind.api.main"
PACKAGE = "gitmind"


def module_to_file(module: str) -> Path | None:
    base = SRC.joinpath(*module.split("."))
    if base.with_suffix(".py").is_file():
        return base.with_suffix(".py")
    if (base / "__init__.py").is_file():
        return base / "__init__.py"
    return None


def imported_modules(path: Path) -> set[str]:
    found = set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module)
            for alias in node.names:
                found.add(f"{node.module}.{alias.name}")
    return {name for name in found if name.split(".")[0] == PACKAGE}


def with_parent_packages(module: str) -> list[str]:
    parts = module.split(".")
    return [".".join(parts[:i]) for i in range(1, len(parts) + 1)]


def main() -> None:
    used: set[Path] = set()
    queue = deque(with_parent_packages(ENTRY))
    seen_modules: set[str] = set()

    while queue:
        module = queue.popleft()
        if module in seen_modules:
            continue
        seen_modules.add(module)

        file = module_to_file(module)
        if file is None:
            continue
        used.add(file)
        for name in imported_modules(file):
            queue.extend(with_parent_packages(name))

    web_page = SRC / PACKAGE / "web" / "index.html"
    if web_page.is_file():
        used.add(web_page)

    all_python = {p for p in (SRC / PACKAGE).rglob("*.py")}
    unused = sorted(all_python - used)

    print(f"Used by the app ({len(used)} files):")
    for path in sorted(used):
        print("  ", path.relative_to(ROOT).as_posix())

    print(f"\nNot used by the app ({len(unused)} files):")
    for path in unused:
        print("  ", path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()