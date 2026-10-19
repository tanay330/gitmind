import time
from urllib.parse import quote, urlparse

import httpx

from gitmind.config import settings

API = "https://api.github.com"
TIMEOUT = httpx.Timeout(30.0, connect=10.0)


class GitHubError(Exception):
    """A GitHub problem, with a message that is safe to show to a user."""


def _headers(raw: bool = False) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {settings.github_token}"}
    if raw:
        headers["Accept"] = "application/vnd.github.raw+json"
    return headers


def _check(response: httpx.Response) -> None:
    if response.status_code == 404:
        raise GitHubError("Repository not found, or it is private")
    if (
        response.status_code in (403, 429)
        and response.headers.get("x-ratelimit-remaining") == "0"
    ):
        raise GitHubError("GitHub rate limit reached, try again later")
    response.raise_for_status()


def parse_repo_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url.strip())
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        raise ValueError("Invalid GitHub repository URL")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError("GitHub URL must contain owner and repository")

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo


def get_repo_info(owner: str, repo: str) -> dict:
    response = httpx.get(f"{API}/repos/{owner}/{repo}", headers=_headers(), timeout=TIMEOUT)
    _check(response)
    data = response.json()
    return {"default_branch": data["default_branch"], "size": data["size"]}


def list_repo_files(owner: str, repo: str, branch: str) -> list[dict]:
    url = f"{API}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    response = httpx.get(url, headers=_headers(), timeout=TIMEOUT)
    _check(response)
    data = response.json()

    if data.get("truncated"):
        raise GitHubError("Repository is too large for GitHub's file listing")

    return [
        {"path": item["path"], "size": item["size"]}
        for item in data["tree"]
        if item["type"] == "blob"
    ]


def fetch_file(owner: str, repo: str, path: str) -> str | None:
    url = f"{API}/repos/{owner}/{repo}/contents/{quote(path)}"

    for attempt in range(3):
        try:
            response = httpx.get(url, headers=_headers(raw=True), timeout=TIMEOUT)
            if response.status_code == 404:
                return None
            _check(response)
            try:
                return response.content.decode("utf-8")
            except UnicodeDecodeError:
                return None
        except (httpx.TimeoutException, httpx.NetworkError):
            if attempt == 2:
                raise
            time.sleep(2**attempt)

    return None