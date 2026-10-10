from gitmind.indexing.chunkers.models import Chunk
import ast

def chunk_python_ast(text:str,path:str):
    tree=ast.parse(text)
    chunks=[]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            source = ast.get_source_segment(text, node)
            chunk=Chunk(
                 text=source,
                 path=path,
                 chunk_type="python_ast"
            )
            chunks.append(chunk)
            
    return chunks        

chunk_python_ast(
    """def greet():
    print("Hello")

class User:
    pass
""",
    "example.py"
)