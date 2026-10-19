from groq import Groq

from gitmind.config import settings
from gitmind.retrieval.search import search

import re
MODEL = "openai/gpt-oss-120b"
TOP_K = 8

SYSTEM_PROMPT = """You are GitMind, an assistant that answers questions about one GitHub repository.

Rules:
1. Use only the numbered sources provided. Do not use outside knowledge, even if you recognize the project.
2. Put a citation like [1] or [2][3] at the END OF EVERY SENTENCE that states a fact about the code. Use plain square brackets only.
3. Read ALL sources before answering. For questions that ask which, what, or list something, include every matching item you find in any source.
4. If the sources do not contain the answer, reply exactly: I don't know based on the indexed code.
5. If the sources contain only part of the answer, give that part and say what is missing.
6. Never invent files, functions, or behavior that the sources do not show.
7. Keep the answer clear and concise, and explain technical terms simply.
8. Do not add details (such as reasons, defaults, or behavior) that no source shows. If you are unsure, leave the detail out.
"""



groq_client = Groq(api_key=settings.groq_api_key)

CITATION_STYLES = re.compile(r"【(\d+)[^】]*】")

def clean_citations(text: str) -> str:
    return CITATION_STYLES.sub(r"[\1]", text)

def format_sources(points) -> str:
    blocks = []
    for number, point in enumerate(points, start=1):
        p = point.payload
        header = f"[{number}] {p['path']}:{p['start_line']}-{p['end_line']} ({p['symbol_name']})"
        blocks.append(f"{header}\n{p['text']}")
    return "\n\n".join(blocks)


def source_link(repo_id: str, payload: dict) -> str:
    return (
        f"https://github.com/{repo_id}/blob/HEAD/{payload['path']}"
        f"#L{payload['start_line']}-L{payload['end_line']}"
    )


def answer_question(question: str, repo_id: str) -> dict:
    points = search(question, repo_id, top_k=TOP_K)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Sources:\n{format_sources(points)}\n\nQuestion: {question}",
        },
    ]
    response = groq_client.chat.completions.create(
        model=MODEL, messages=messages, temperature=0
    )

    return {
            "answer": clean_citations(response.choices[0].message.content),
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