from sqlalchemy import select

from gitmind.db.models import Job
from gitmind.db.session import SessionLocal

with SessionLocal() as session:
    for job in session.scalars(select(Job).order_by(Job.created_at)):
        print(job.job_id[:8], job.repo_id, job.status, job.chunks_stored, job.detail)