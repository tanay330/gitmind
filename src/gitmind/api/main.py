from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from gitmind.api.jobs import fail_stale_jobs
from gitmind.api.rate_limit import limiter
from gitmind.api.routes_chat import router as chat_router
from gitmind.api.routes_repos import router as repos_router
from gitmind.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    fail_stale_jobs()
    yield


app = FastAPI(
    title="GitMind",
    version="0.1.0",
    description="Ask questions about any public GitHub repository.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(repos_router)
app.include_router(chat_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}