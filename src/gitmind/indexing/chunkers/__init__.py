from gitmind.indexing.chunkers.python_ast import chunk_python_ast
from gitmind.indexing.chunkers.markdown import chunk_markdown
from gitmind.indexing.chunkers.generic import chunk_generic
from pathlib import Path

def chunk_file(text:str,path:str):
    extension = Path(path).suffix.lower()
    if extension==".py":
        return chunk_python_ast(text,path)
    elif extension==".md":
        return chunk_markdown(text,path)
    else:
        return chunk_generic(text,path)        