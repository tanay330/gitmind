from gitmind.indexing.chunkers import chunk_file
from gitmind.indexing.chunkers.generic import chunk_generic
from gitmind.indexing.chunkers.markdown import chunk_markdown
from gitmind.indexing.chunkers.python_ast import chunk_python

REPO = "me/demo"
FENCE = "`" * 3

PYTHON_SAMPLE = """import os

@decorator
def greet(name):
    return f"hi {name}"

async def fetch():
    pass

class Box:
    def open(self):
        pass

if __name__ == "__main__":
    greet("x")
"""


def by_name(chunks):
    return {chunk.symbol_name: chunk for chunk in chunks}


def test_python_functions_classes_and_module_chunk():
    chunks = by_name(chunk_python(PYTHON_SAMPLE, "a.py", REPO))

    assert (chunks["greet"].start_line, chunks["greet"].end_line) == (3, 5)  # decorator included
    assert (chunks["fetch"].start_line, chunks["fetch"].end_line) == (7, 8)  # async def handled
    assert chunks["Box"].symbol_type == "class"
    assert (chunks["<module>"].start_line, chunks["<module>"].end_line) == (1, 15)
    assert "import os" in chunks["<module>"].text
    assert 'greet("x")' in chunks["<module>"].text


def test_python_long_function_is_split_into_consecutive_parts():
    body = "\n".join(f"    x{i} = {i}" for i in range(100))
    source = "def long_function():\n" + body + "\n"

    chunks = chunk_python(source, "a.py", REPO)

    assert [(c.symbol_name, c.start_line, c.end_line) for c in chunks] == [
        ("long_function (part 1/3)", 1, 34),
        ("long_function (part 2/3)", 35, 68),
        ("long_function (part 3/3)", 69, 101),
    ]


def test_python_big_class_is_split_into_header_and_methods():
    methods = "\n".join(
        f"    def m{i}(self):\n" + "\n".join(f"        x{j} = {j}" for j in range(24))
        for i in range(3)
    )
    source = "class Big:\n    '''Doc'''\n" + methods + "\n"

    chunks = chunk_python(source, "a.py", REPO)

    assert [c.symbol_name for c in chunks] == ["Big", "Big.m0", "Big.m1", "Big.m2"]
    assert chunks[0].symbol_type == "class"
    assert all(c.symbol_type == "method" for c in chunks[1:])


def test_markdown_sections_ignore_comments_inside_code_blocks():
    markdown = "\n".join(
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

    chunks = chunk_markdown(markdown, "a.md", REPO)

    assert [(c.symbol_name, c.start_line, c.end_line) for c in chunks] == [
        ("<intro>", 1, 2),
        ("Title", 3, 5),
        ("Install", 6, 11),
        ("Basics", 12, 14),  # "Usage" has no text of its own, so it merges into "Basics"
    ]
    assert "# this is a comment" in chunks[2].text


def test_generic_windows_overlap_and_cover_the_file():
    content = "\n".join(f"line {i}" for i in range(1, 101))

    chunks = chunk_generic(content, "a.txt", REPO)

    assert [(c.start_line, c.end_line) for c in chunks] == [(1, 40), (33, 72), (65, 100)]


def test_dispatcher_chooses_chunker_by_extension():
    assert chunk_file("def f():\n    pass\n", "a.py", REPO)[0].symbol_type == "function"
    assert chunk_file("# Title\nHello\n", "a.md", REPO)[0].symbol_type == "section"

    js = chunk_file("function f() {}\n", "app.js", REPO)[0]
    assert (js.symbol_type, js.language) == ("block", "javascript")

    assert chunk_file("FROM python:3.11\n", "Dockerfile", REPO)[0].language == "text"


def test_dispatcher_falls_back_when_python_is_invalid():
    chunks = chunk_file("def oops(:\n    pass\n", "broken.py", REPO)

    assert len(chunks) == 1
    assert (chunks[0].symbol_type, chunks[0].language) == ("block", "python")