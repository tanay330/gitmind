from gitmind.indexing.chunkers import chunk_file

SAMPLES = {
    "a.py": "def hi():\n    return 1\n",
    "broken.py": "def oops(:\n    pass\n",
    "readme.md": "# Title\nHello\n",
    "app.js": "function f() {\n  return 1;\n}\n",
    "Dockerfile": "FROM python:3.11\nRUN echo hi\n",
}

for path, content in SAMPLES.items():
    print(path)
    for c in chunk_file(content, path, "me/demo"):
        print(f"   {c.symbol_type:8} {c.symbol_name:14} {c.language:10} lines {c.start_line}-{c.end_line}")