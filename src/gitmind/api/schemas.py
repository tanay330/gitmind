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