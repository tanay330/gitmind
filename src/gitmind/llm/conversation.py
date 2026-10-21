import re

MAX_HISTORY_TURNS = 3
MAX_HISTORY_ANSWER_CHARS = 800

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
9. Earlier messages in this conversation are only background for understanding follow-up questions. Never use them as evidence and never cite them: cite only the numbered sources in the latest message.
"""

CONDENSE_PROMPT = """Rewrite the user's latest question as one standalone question that can be understood without the conversation.
Use the earlier turns only to resolve references such as "it", "that", "why" or "the second one".
Keep the names of files, functions and libraries exactly as written.
If the latest question is already standalone, return it unchanged.
Return only the question, with no explanation."""

ODD_CITATIONS = re.compile(r"【(\d+)[^】]*】")
CITATION = re.compile(r"\s*\[\d{1,2}\]")


def clean_citations(text: str) -> str:
    return ODD_CITATIONS.sub(r"[\1]", text)


def strip_citations(text: str) -> str:
    return CITATION.sub("", text)


def trim_history(history: list[dict]) -> list[dict]:
    trimmed = []
    for turn in history[-MAX_HISTORY_TURNS:]:
        answer = strip_citations(turn["answer"]).strip()
        if len(answer) > MAX_HISTORY_ANSWER_CHARS:
            answer = answer[:MAX_HISTORY_ANSWER_CHARS].rstrip() + "..."
        trimmed.append({"question": turn["question"], "answer": answer})
    return trimmed


def format_transcript(history: list[dict]) -> str:
    return "\n\n".join(
        f"User: {turn['question']}\nAssistant: {turn['answer']}"
        for turn in trim_history(history)
    )


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


def build_messages(question: str, sources_text: str, history: list[dict]) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in trim_history(history):
        messages.append({"role": "user", "content": turn["question"]})
        messages.append({"role": "assistant", "content": turn["answer"]})
    messages.append(
        {"role": "user", "content": f"Sources:\n{sources_text}\n\nQuestion: {question}"}
    )
    return messages