import os
import tempfile
from pathlib import Path

# These must be set BEFORE any gitmind module is imported,
# because settings are read once, when the config module loads.
os.environ.setdefault("GITHUB_TOKEN", "test-token")
os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ["DATABASE_URL"] = "sqlite:///" + Path(tempfile.mkdtemp(), "test.db").as_posix()

import pytest
from sqlalchemy import delete

from gitmind.db.models import Job
from gitmind.db.session import SessionLocal, init_db


@pytest.fixture(autouse=True)
def clean_jobs():
    init_db()
    with SessionLocal() as session:
        session.execute(delete(Job))
        session.commit()
    yield