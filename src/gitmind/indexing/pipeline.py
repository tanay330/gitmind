import httpx

from gitmind.indexing.chunkers import chunk_file
from gitmind.indexing.filters import should_include
from gitmind.indexing.github_client import (
    GitHubError,
    fetch_file,
    get_repo_info,
    list_repo_files,
    parse_repo_url,
)
from gitmind.models import make_repo_id
from gitmind.retrieval.store import count_repo, delete_repo, ensure_collection, upsert_chunks

MAX_REPO_SIZE_KB = 100_000  # GitHub reports repository size in kilobytes
MAX_FILES = 1500
BATCH_SIZE = 64
MIN_MODULE_CHARS = 60

def _is_imports_only(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return bool(lines) and all(
        line.startswith(("import ", "from ", "#")) for line in lines
    )
def index_repository(repo_url: str) -> dict:
    owner, repo = parse_repo_url(repo_url)
    repo_id = make_repo_id(owner, repo)

    info = get_repo_info(owner, repo)
    if info["size"] > MAX_REPO_SIZE_KB:
        raise GitHubError("Repository is too large to index")

    all_files = list_repo_files(owner, repo, info["default_branch"])
    files = [f for f in all_files if should_include(f["path"], f["size"])]
    if len(files) > MAX_FILES:
        raise GitHubError(f"Repository has too many indexable files ({len(files)})")

    ensure_collection()
    delete_repo(repo_id)

    batch = []
    indexed_files = 0
    failed_files = 0
    created_chunks = 0

    for number, file in enumerate(files, start=1):
        try:
            content = fetch_file(owner, repo, file["path"])
        except httpx.HTTPError:
            failed_files += 1
            continue

        if content is None:
            continue

        chunks = [
            chunk
            for chunk in chunk_file(content, file["path"], repo_id)
            if not (chunk.symbol_type == "module" and  _is_imports_only(chunk.text))
        ]

        indexed_files += 1
        for chunk in chunks:
            batch.append(chunk)
            created_chunks += 1
            if len(batch) >= BATCH_SIZE:
                upsert_chunks(batch)
                batch = []

        if number % 25 == 0:
            print(f"  processed {number}/{len(files)} files")

    if batch:
        upsert_chunks(batch)

    return {
        "repo_id": repo_id,
        "files_in_repo": len(all_files),
        "files_indexed": indexed_files,
        "files_failed": failed_files,
        "chunks_created": created_chunks,
        "chunks_stored": count_repo(repo_id),
    }