from types import SimpleNamespace

import pytest

from gitmind.llm import answer as answer_module

POINT = SimpleNamespace(
    payload={"path": "a.py", "start_line": 1, "end_line": 2, "symbol_name": "f", "text": "code"}
)


def fake_groq(replies, calls):
    def create(**kwargs):
        calls.append(kwargs)
        reply = replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=reply))])

    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


@pytest.fixture()
def searched(monkeypatch):
    queries = []

    def fake_search(query, repo_id, top_k=8):
        queries.append(query)
        return [POINT]

    monkeypatch.setattr(answer_module, "search", fake_search)
    return queries


def test_first_question_makes_a_single_model_call(monkeypatch, searched):
    calls = []
    monkeypatch.setattr(answer_module, "groq_client", fake_groq(["It uses X [1]."], calls))

    result = answer_module.answer_question("What does it use?", "me/demo")

    assert len(calls) == 1
    assert searched == ["What does it use?"]
    assert result["search_query"] == "What does it use?"
    assert result["answer"] == "It uses X [1]."
    assert result["sources"][0]["url"] == "https://github.com/me/demo/blob/HEAD/a.py#L1-L2"


def test_follow_up_is_rewritten_before_searching(monkeypatch, searched):
    calls = []
    rewritten = "Why does requests strip the Authorization header on redirects?"
    monkeypatch.setattr(
        answer_module, "groq_client", fake_groq([rewritten, "Because the host changes [1]."], calls)
    )
    history = [{"question": "How are redirects followed?", "answer": "It rebuilds auth [1]."}]

    result = answer_module.answer_question("why?", "me/demo", history)

    assert searched == [rewritten]
    assert result["search_query"] == rewritten
    assert result["answer"] == "Because the host changes [1]."

    final_messages = calls[1]["messages"]
    assert [m["role"] for m in final_messages] == ["system", "user", "assistant", "user"]
    assert "[1]" not in final_messages[2]["content"]
    assert final_messages[3]["content"].endswith(f"Question: {rewritten}")


def test_failed_rewrite_falls_back_to_the_original_question(monkeypatch, searched):
    calls = []
    monkeypatch.setattr(
        answer_module, "groq_client", fake_groq([RuntimeError("boom"), "Answer [1]."], calls)
    )
    history = [{"question": "q1", "answer": "a1"}]

    result = answer_module.answer_question("why?", "me/demo", history)

    assert searched == ["why?"]
    assert result["search_query"] == "why?"
    assert result["answer"] == "Answer [1]."


@pytest.mark.parametrize("bad_rewrite", ["", "ok", "x" * 400])
def test_unusable_rewrites_are_ignored(monkeypatch, searched, bad_rewrite):
    monkeypatch.setattr(answer_module, "groq_client", fake_groq([bad_rewrite, "Answer."], []))
    answer_module.answer_question("why?", "me/demo", [{"question": "q1", "answer": "a1"}])
    assert searched == ["why?"]


def test_only_the_first_line_of_a_rewrite_is_used(monkeypatch, searched):
    monkeypatch.setattr(
        answer_module, "groq_client",
        fake_groq(['"Why is auth stripped?"\nBecause of the host change.', "Answer."], []),
    )
    answer_module.answer_question("why?", "me/demo", [{"question": "q1", "answer": "a1"}])
    assert searched == ["Why is auth stripped?"]