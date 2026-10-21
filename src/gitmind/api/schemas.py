from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    url: str = Field(
        min_length=1,
        max_length=300,
        examples=["https://github.com/psf/requests"],
    )


class JobStatus(BaseModel):
    job_id: str
    repo_id: str
    status: Literal["queued", "indexing", "ready", "failed"]
    detail: str | None = None
    files_indexed: int | None = None
    chunks_stored: int | None = None
    created_at: datetime
    finished_at: datetime | None = None


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class SourceItem(BaseModel):
    number: int
    path: str
    lines: str
    symbol: str
    url: str


class ChatResponse(BaseModel):
    repo_id: str
    question: str
    answer: str
    search_query: str | None = None
    sources: list[SourceItem]


class RepoItem(BaseModel):
    repo_id: str
    chunks: int    
    
class ChatTurn(BaseModel):
    question: str = Field(max_length=500)
    answer: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    history: list[ChatTurn] = Field(default_factory=list, max_length=6)    