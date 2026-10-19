from gitmind.indexing.chunkers.python_ast import chunk_python

body = "\n".join(f"    x{i} = {i}" for i in range(100))
source = "def long_function():\n" + body + "\n"

for c in chunk_python(source, "demo.py", "me/demo"):
    print(f"{c.symbol_type:9} {c.symbol_name:30} lines {c.start_line}-{c.end_line}")