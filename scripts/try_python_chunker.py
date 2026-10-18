from pathlib import Path

from gitmind.indexing.chunkers.python_ast import chunk_python

SAMPLE = '''import os

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
'''


def show(chunks):
    for c in chunks:
        first = c.text.splitlines()[0] if c.text else ""
        print(f"{c.symbol_type:9} {c.symbol_name:22} lines {c.start_line}-{c.end_line}  | {first}")


print("--- SAMPLE")
show(chunk_python(SAMPLE, "sample.py", "me/demo"))

print("\n--- embedder.py")
path = "src/gitmind/indexing/embedder.py"
show(chunk_python(Path(path).read_text(encoding="utf-8"), path, "tanay330/gitmind"))