import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from gitmind.api.jobs import finish_job, get_job, start_job, update_job
from gitmind.api.rate_limit import INDEX_LIMIT, limiter
from gitmind.api.schemas import IndexRequest, JobStatus, RepoItem
from gitmind.indexing.github_client import GitHubError, parse_repo_url
from gitmind.indexing.pipeline import index_repository
from gitmind.models import make_repo_id
from gitmind.retrieval.store import list_repos
from gitmind.config import settings

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
@limiter.limit(INDEX_LIMIT)

def start_indexing(
    payload: IndexRequest, request: Request, background_tasks: BackgroundTasks
):
    if not settings.allow_indexing:
        raise HTTPException(
        status_code=403, detail="Indexing is turned off on this deployment"
        )
    try:
        owner, repo = parse_repo_url(payload.url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    job, created = start_job(make_repo_id(owner, repo))
    if created:
        background_tasks.add_task(run_indexing, job["job_id"], payload.url)
    return job


@router.get("/jobs/{job_id}", response_model=JobStatus)
def read_job(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/repos", response_model=list[RepoItem])
def read_repos():
    return list_repos()