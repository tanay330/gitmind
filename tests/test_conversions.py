from types import SimpleNamespace

from gitmind.llm.conversation import (
    MAX_HISTORY_ANSWER_CHARS,
    MAX_HISTORY_TURNS,
    build_messages,
    clean_citations,
    format_sources,
    format_transcript,
    source_link,
    strip_citations,
    trim_history,
)


def turn(number, answer=None):
    return {"question": f"question {number}", "answer": answer or f"answer {number}"}


def test_strip_citations_removes_all_markers():
    assert strip_citations("Uses X [1][2]. Also Y [3].") == "Uses X. Also Y."


def test_clean_citations_converts_unusual_brackets():
    assert clean_citations("Uses X \u30101\u3011 and Y \u30102\u2020L5\u3011.") == "Uses X [1] and Y [2]."


def test_trim_history_keeps_only_the_most_recent_turns():
    history = [turn(i) for i in range(1, 8)]
    trimmed = trim_history(history)
    assert [t["question"] for t in trimmed] == ["question 5", "question 6", "question 7"]
    assert len(trimmed) == MAX_HISTORY_TURNS


def test_trim_history_removes_citations_and_shortens_long_answers():
    trimmed = trim_history([turn(1, "short answer [1]."), turn(2, "x" * 5000)])
    assert trimmed[0]["answer"] == "short answer."
    assert len(trimmed[1]["answer"]) == MAX_HISTORY_ANSWER_CHARS + 3
    assert trimmed[1]["answer"].endswith("...")


def test_format_transcript():
    text = format_transcript([turn(1), turn(2)])
    assert text == "User: question 1\nAssistant: answer 1\n\nUser: question 2\nAssistant: answer 2"


def test_format_sources_numbers_each_chunk():
    points = [
        SimpleNamespace(payload={"path": "a.py", "start_line": 1, "end_line": 2, "symbol_name": "f", "text": "code a"}),
        SimpleNamespace(payload={"path": "b.py", "start_line": 5, "end_line": 9, "symbol_name": "g", "text": "code b"}),
    ]
    assert format_sources(points) == "[1] a.py:1-2 (f)\ncode a\n\n[2] b.py:5-9 (g)\ncode b"


def test_source_link_points_at_the_lines():
    payload = {"path": "src/a.py", "start_line": 10, "end_line": 20}
    assert source_link("me/demo", payload) == "https://github.com/me/demo/blob/HEAD/src/a.py#L10-L20"


def test_build_messages_without_history():
    messages = build_messages("What is this?", "[1] a.py:1-2 (f)\ncode", [])
    assert [m["role"] for m in messages] == ["system", "user"]
    assert messages[1]["content"] == "Sources:\n[1] a.py:1-2 (f)\ncode\n\nQuestion: What is this?"


def test_build_messages_with_history_keeps_old_citations_out():
    history = [turn(1, "It rebuilds auth [1][2].")]
    messages = build_messages("Why?", "[1] a.py:1-2 (f)\ncode", history)

    assert [m["role"] for m in messages] == ["system", "user", "assistant", "user"]
    assert messages[1]["content"] == "question 1"
    assert messages[2]["content"] == "It rebuilds auth."
    assert messages[3]["content"].endswith("Question: Why?")