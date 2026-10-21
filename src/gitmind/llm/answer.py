import logging

from groq import Groq

from gitmind.config import settings
from gitmind.llm.conversation import (
    CONDENSE_PROMPT,
    build_messages,
    clean_citations,
    format_sources,
    format_transcript,
    source_link,
)
from gitmind.retrieval.search import search

logger = logging.getLogger(__name__)

MODEL = "openai/gpt-oss-120b"
TOP_K = 8

groq_client = Groq(api_key=settings.groq_api_key)


def condense_question(question: str, history: list[dict]) -> str:
    if not history:
        return question

    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": CONDENSE_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Conversation so far:\n{format_transcript(history)}\n\n"
                        f"Latest question: {question}"
                    ),
                },
            ],
            temperature=0,
        )
        raw = (response.choices[0].message.content or "").strip()
    except Exception:
        logger.exception("Could not rewrite the follow-up question")
        return question

    rewritten = raw.splitlines()[0].strip().strip('"') if raw else ""
    return rewritten if 3 <= len(rewritten) <= 300 else question


def answer_question(question: str, repo_id: str, history: list[dict] | None = None) -> dict:
    history = history or []
    query = condense_question(question, history)
    points = search(query, repo_id, top_k=TOP_K)

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=build_messages(query, format_sources(points), history),
        temperature=0,
    )

    return {
        "answer": clean_citations(response.choices[0].message.content),
        "search_query": query,
        "sources": [
            {
                "number": number,
                "path": point.payload["path"],
                "lines": f"{point.payload['start_line']}-{point.payload['end_line']}",
                "symbol": point.payload["symbol_name"],
                "url": source_link(repo_id, point.payload),
            }
            for number, point in enumerate(points, start=1)
        ],
    }