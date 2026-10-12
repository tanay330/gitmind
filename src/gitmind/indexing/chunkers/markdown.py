from gitmind.indexing.chunkers.models import Chunk

def chunk_markdown(text:str,path:str):
    lines=text.splitlines()
    current_section=[]
    chunks=[]
    for line in lines:
        if line.startswith("#"):
            if current_section:
                chunk=Chunk(
                    text="\n".join(current_section),
                    path=path,
                    chunk_type="markdown"
                )
                
                chunks.append(chunk)
                current_section.clear()
            current_section.append(line)    
            
        else:
            current_section.append(line)
    if current_section:
        chunk = Chunk(
        text="\n".join(current_section),
        path=path,
        chunk_type="markdown"
    )
        chunks.append(chunk)      
    return chunks        
       

            
    