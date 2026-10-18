import uuid
from dataclasses import dataclass


def make_repo_id(owner: str, repo: str) -> str:
    return f"{owner}/{repo}".lower()


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