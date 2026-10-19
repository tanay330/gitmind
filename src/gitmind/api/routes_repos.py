import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from gitmind.api.jobs import finish_job, get_job, start_job, update_job
from gitmind.api.schemas import IndexRequest, JobStatus
from gitmind.indexing.github_client import GitHubError, parse_repo_url
from gitmind.indexing.pipeline import index_repository
from gitmind.models import make_repo_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["repos"])


def run_indexing(job_id: str, url: str) -> None:
    update_job(job_id, status="indexing")
    try:
        summary = index_repository(url)
    except GitHubError as error:
        finish_job(job_id, status="failed", detail=str(error))
    except Exception:
        logger.exception("Indexing job %s failed", job_id)
        finish_job(job_id, status="failed", detail="Indexing failed unexpectedly")
    else:
        finish_job(
            job_id,
            status="ready",
            files_indexed=summary["files_indexed"],
            chunks_stored=summary["chunks_stored"],
        )


@router.post("/repos", response_model=JobStatus, status_code=202)
def start_indexing(request: IndexRequest, background_tasks: BackgroundTasks):
    try:
        owner, repo = parse_repo_url(request.url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    job, created = start_job(make_repo_id(owner, repo))
    if created:
        background_tasks.add_task(run_indexing, job["job_id"], request.url)
    return job


@router.get("/jobs/{job_id}", response_model=JobStatus)
def read_job(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job