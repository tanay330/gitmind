from fastapi import FastAPI

from gitmind.api.routes_repos import router as repos_router

app = FastAPI(
    title="GitMind",
    version="0.1.0",
    description="Ask questions about any public GitHub repository.",
)

app.include_router(repos_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}