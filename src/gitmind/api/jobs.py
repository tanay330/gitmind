import uuid
from datetime import datetime, timezone
from threading import Lock

from sqlalchemy import select

from gitmind.db.models import Job
from gitmind.db.session import SessionLocal

ACTIVE = ("queued", "indexing")
FIELDS = (
    "job_id", "repo_id", "status", "detail",
    "files_indexed", "chunks_stored", "created_at", "finished_at",
)

_lock = Lock()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _to_dict(job: Job) -> dict:
    return {field: getattr(job, field) for field in FIELDS}


def start_job(repo_id: str) -> tuple[dict, bool]:
    with _lock, SessionLocal() as session:
        active = session.scalars(
            select(Job).where(Job.repo_id == repo_id, Job.status.in_(ACTIVE))
        ).first()
        if active:
            return _to_dict(active), False

        job = Job(
            job_id=uuid.uuid4().hex,
            repo_id=repo_id,
            status="queued",
            created_at=_now(),
        )
        session.add(job)
        session.commit()
        return _to_dict(job), True


def update_job(job_id: str, **changes) -> None:
    with SessionLocal() as session:
        job = session.get(Job, job_id)
        for key, value in changes.items():
            setattr(job, key, value)
        session.commit()


def finish_job(job_id: str, **changes) -> None:
    update_job(job_id, finished_at=_now(), **changes)


def get_job(job_id: str) -> dict | None:
    with SessionLocal() as session:
        job = session.get(Job, job_id)
        return _to_dict(job) if job else None


def is_indexing(repo_id: str) -> bool:
    with SessionLocal() as session:
        found = session.scalars(
            select(Job.job_id).where(Job.repo_id == repo_id, Job.status.in_(ACTIVE))
        ).first()
        return found is not None


def fail_stale_jobs() -> int:
    with SessionLocal() as session:
        stale = session.scalars(select(Job).where(Job.status.in_(ACTIVE))).all()
        for job in stale:
            job.status = "failed"
            job.detail = "Server restarted while this job was running"
            job.finished_at = _now()
        session.commit()
        return len(stale)