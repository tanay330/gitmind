from dataclasses import dataclass

@dataclass
class Chunk:
    text:str
    path:str
    chunk_type:str
    