from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from gitmind.api.jobs import fail_stale_jobs
from gitmind.api.rate_limit import limiter
from gitmind.api.routes_chat import router as chat_router
from gitmind.api.routes_repos import router as repos_router
from gitmind.db.session import init_db

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


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


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}