import pytest
from fastapi.testclient import TestClient

from gitmind.api import routes_chat, routes_repos
from gitmind.api.jobs import start_job
from gitmind.api.main import app
from gitmind.api.rate_limit import limiter
from gitmind.indexing.github_client import GitHubError

FAKE_ANSWER = {
    "answer": "It uses X [1].",
    "sources": [
        {
            "number": 1,
            "path": "a.py",
            "lines": "1-2",
            "symbol": "f",
            "url": "https://github.com/a/b/blob/HEAD/a.py#L1-L2",
        }
    ],
}


@pytest.fixture()
def client():
    limiter.reset()
    with TestClient(app) as test_client:
        yield test_client


def fake_indexed_repo(monkeypatch, calls=None):
    def fake_answer(question, repo_id):
        if calls is not None:
            calls.append(repo_id)
        return FAKE_ANSWER

    monkeypatch.setattr(routes_chat, "count_repo", lambda repo_id: 5)
    monkeypatch.setattr(routes_chat, "answer_question", fake_answer)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_index_rejects_a_bad_url(client):
    response = client.post("/repos", json={"url": "https://example.com/a/b"})
    assert response.status_code == 400


def test_index_rejects_a_missing_url(client):
    assert client.post("/repos", json={}).status_code == 422


def test_index_runs_in_the_background_and_reports_results(client, monkeypatch):
    monkeypatch.setattr(
        routes_repos, "index_repository",
        lambda url: {"files_indexed": 4, "chunks_stored": 12},
    )

    response = client.post("/repos", json={"url": "https://github.com/psf/requests"})
    assert response.status_code == 202
    assert response.json()["repo_id"] == "psf/requests"

    job = client.get(f"/jobs/{response.json()['job_id']}").json()
    assert (job["status"], job["files_indexed"], job["chunks_stored"]) == ("ready", 4, 12)


def test_expected_errors_are_shown_to_the_user(client, monkeypatch):
    def fail(url):
        raise GitHubError("Repository not found, or it is private")

    monkeypatch.setattr(routes_repos, "index_repository", fail)

    job_id = client.post("/repos", json={"url": "https://github.com/a/b"}).json()["job_id"]
    job = client.get(f"/jobs/{job_id}").json()

    assert job["status"] == "failed"
    assert job["detail"] == "Repository not found, or it is private"


def test_unexpected_errors_are_hidden_from_the_user(client, monkeypatch):
    def fail(url):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(routes_repos, "index_repository", fail)

    job_id = client.post("/repos", json={"url": "https://github.com/a/b"}).json()["job_id"]
    job = client.get(f"/jobs/{job_id}").json()

    assert job["detail"] == "Indexing failed unexpectedly"
    assert "secret" not in str(job)


def test_unknown_job_is_404(client):
    assert client.get("/jobs/nope").status_code == 404


def test_list_repos(client, monkeypatch):
    monkeypatch.setattr(routes_repos, "list_repos", lambda: [{"repo_id": "a/b", "chunks": 3}])
    assert client.get("/repos").json() == [{"repo_id": "a/b", "chunks": 3}]


def test_chat_returns_answer_and_sources_for_a_normalized_repo(client, monkeypatch):
    calls = []
    fake_indexed_repo(monkeypatch, calls)

    response = client.post(
        "/repos/PSF/Requests/chat", json={"question": "How are redirects followed?"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["repo_id"] == "psf/requests"
    assert body["answer"] == "It uses X [1]."
    assert body["sources"][0]["path"] == "a.py"
    assert calls == ["psf/requests"]


def test_chat_on_a_repo_that_is_not_indexed_is_404(client, monkeypatch):
    monkeypatch.setattr(routes_chat, "count_repo", lambda repo_id: 0)
    response = client.post("/repos/a/b/chat", json={"question": "What is this?"})
    assert response.status_code == 404


def test_chat_while_indexing_is_409(client, monkeypatch):
    fake_indexed_repo(monkeypatch)
    start_job("psf/requests")  # stays queued: nothing runs it
    response = client.post("/repos/psf/requests/chat", json={"question": "What is this?"})
    assert response.status_code == 409


def test_chat_rejects_a_too_short_question(client):
    assert client.post("/repos/a/b/chat", json={"question": "hi"}).status_code == 422


def test_chat_hides_model_failures(client, monkeypatch):
    monkeypatch.setattr(routes_chat, "count_repo", lambda repo_id: 5)

    def fail(question, repo_id):
        raise RuntimeError("groq is down")

    monkeypatch.setattr(routes_chat, "answer_question", fail)

    response = client.post("/repos/a/b/chat", json={"question": "What is this?"})

    assert response.status_code == 502
    assert "groq" not in response.text


def test_chat_is_rate_limited(client, monkeypatch):
    fake_indexed_repo(monkeypatch)

    codes = [
        client.post("/repos/a/b/chat", json={"question": "What is this?"}).status_code
        for _ in range(21)
    ]

    assert codes[:20] == [200] * 20
    assert codes[20] == 429

def test_home_page_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "GitMind" in response.text    