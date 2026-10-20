import uuid
from datetime import datetime, timezone
from threading import Lock

ACTIVE = {"queued", "indexing"}

_jobs: dict[str, dict] = {}
_lock = Lock()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def start_job(repo_id: str) -> tuple[dict, bool]:
    with _lock:
        for job in _jobs.values():
            if job["repo_id"] == repo_id and job["status"] in ACTIVE:
                return dict(job), False

        job = {
            "job_id": uuid.uuid4().hex,
            "repo_id": repo_id,
            "status": "queued",
            "detail": None,
            "files_indexed": None,
            "chunks_stored": None,
            "created_at": _now(),
            "finished_at": None,
        }
        _jobs[job["job_id"]] = job
        return dict(job), True


def update_job(job_id: str, **changes) -> None:
    with _lock:
        _jobs[job_id].update(changes)


def finish_job(job_id: str, **changes) -> None:
    update_job(job_id, finished_at=_now(), **changes)


def get_job(job_id: str) -> dict | None:
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None

def is_indexing(repo_id: str) -> bool:
    with _lock:
        return any(
            job["repo_id"] == repo_id and job["status"] in ACTIVE
            for job in _jobs.values()
        )    