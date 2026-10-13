from gitmind.indexing.chunkers.models import Chunk
import ast

def chunk_python_ast(text:str,path:str):
    tree=ast.parse(text)
    chunks=[]
    
    module_lines = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if module_lines:
                source = "\n".join(module_lines)
                chunks.append(
                    Chunk(
                        text=source,
                        path=path,
                        chunk_type="python_module"
                    )
                )
                
                module_lines = []
            source = ast.get_source_segment(text, node)
            chunk=Chunk(
                 text=source,
                 path=path,
                 chunk_type="python_ast"
            )
            chunks.append(chunk)    
        else:
            # Preserve module-level statements
            source = ast.get_source_segment(text, node)
            if source:
                module_lines.append(source)
     # Save any remaining module-level code
    if module_lines:
        source = "\n".join(module_lines)
        chunks.append(
            Chunk(
                text=source,
                path=path,
                chunk_type="python_module"
            )
        )    
            
    return chunks        

