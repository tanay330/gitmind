from gitmind.indexing.chunkers import chunk_file

# 1. Test Python AST chunker
python_code = """def greet():
    print("Hello")

class User:
    pass
"""

python_chunks = chunk_file(python_code, "main.py")

print("=== Python Chunks ===")
for chunk in python_chunks:
    print(chunk)


# 2. Test Markdown chunker
markdown_text = """# Introduction

GitMind is a repository RAG system.

## Installation

Install the dependencies.
"""

markdown_chunks = chunk_file(markdown_text, "README.md")

print("\n=== Markdown Chunks ===")
for chunk in markdown_chunks:
    print(chunk)


# 3. Test Generic chunker
plain_text = "This is a sample text file used to test the generic chunker."

generic_chunks = chunk_file(plain_text, "notes.txt")

print("\n=== Generic Chunks ===")
for chunk in generic_chunks:
    print(chunk)