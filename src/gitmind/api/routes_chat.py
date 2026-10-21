import logging

from fastapi import APIRouter, HTTPException, Request

from gitmind.api.jobs import is_indexing
from gitmind.api.rate_limit import CHAT_LIMIT, limiter
from gitmind.api.schemas import ChatRequest, ChatResponse
from gitmind.llm.answer import answer_question
from gitmind.models import make_repo_id
from gitmind.retrieval.store import count_repo

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


@router.post("/repos/{owner}/{repo}/chat", response_model=ChatResponse)
@limiter.limit(CHAT_LIMIT)
def chat(owner: str, repo: str, payload: ChatRequest, request: Request):
    repo_id = make_repo_id(owner, repo)

    if is_indexing(repo_id):
        raise HTTPException(
            status_code=409,
            detail="Repository is still being indexed, try again shortly",
        )
    if count_repo(repo_id) == 0:
        raise HTTPException(
            status_code=404,
            detail="Repository is not indexed. Index it first with POST /repos",
        )

    try:
        history = [turn.model_dump() for turn in payload.history]
        result = answer_question(payload.question, repo_id, history)
    
    except Exception:
        logger.exception("Answering failed for %s", repo_id)
        raise HTTPException(
            status_code=502,
            detail="Could not generate an answer right now, please try again",
        )

    return {"repo_id": repo_id, "question": payload.question, **result}