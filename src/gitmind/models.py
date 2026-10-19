import uuid
from dataclasses import dataclass
import re

def make_repo_id(owner: str, repo: str) -> str:
    return f"{owner}/{repo}".lower()

IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def split_identifiers(text: str) -> str:
    words = []
    seen = set()

    for identifier in IDENTIFIER.findall(text):
        pieces = []
        for part in identifier.split("_"):
            if part:
                pieces.extend(CAMEL_BOUNDARY.split(part))

        if len(pieces) == 1 and pieces[0] == identifier:
            continue  # an ordinary word, nothing to split

        for piece in pieces:
            word = piece.lower()
            if len(word) > 1 and word not in seen:
                seen.add(word)
                words.append(word)

    return " ".join(words)
@dataclass
class Chunk:
    repo_id: str
    path: str
    symbol_name: str
    symbol_type: str
    start_line: int
    end_line: int
    language: str
    text: str
    description: str = ""

    @property
    def id(self) -> str:
        key = f"{self.repo_id}|{self.path}|{self.symbol_name}|{self.start_line}"
        return str(uuid.uuid5(uuid.NAMESPACE_URL, key))

    def embedding_text(self) -> str:
        parts = [f"File: {self.path}\nSymbol: {self.symbol_name} ({self.symbol_type})"]
        if self.description:
            parts.append(self.description)
        parts.append(self.text)
        return "\n\n".join(parts)
    
    def keyword_text(self) -> str:
        extra = split_identifiers(f"{self.path} {self.symbol_name} {self.text}")
        base = self.embedding_text()
        return f"{base}\n\n{extra}" if extra else base