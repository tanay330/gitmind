from gitmind.indexing.chunkers.generic import chunk_generic
from gitmind.indexing.chunkers.markdown import chunk_markdown

FENCE = "`" * 3
MARKDOWN = "\n".join(
    [
        "Intro text here.",
        "",
        "# Title",
        "Some description.",
        "",
        "## Install",
        FENCE + "bash",
        "# this is a comment, not a heading",
        "pip install demo",
        FENCE,
        "",
        "## Usage",
        "### Basics",
        "Call run().",
    ]
)

GENERIC = "\n".join(f"line {i}" for i in range(1, 101))


def show(chunks):
    for c in chunks:
        print(f"{c.symbol_type:8} {c.symbol_name:20} lines {c.start_line}-{c.end_line}")


print("--- markdown")
show(chunk_markdown(MARKDOWN, "demo.md", "me/demo"))

print("\n--- generic (100 lines)")
show(chunk_generic(GENERIC, "demo.txt", "me/demo"))