from gitmind.indexing.github_client import parse_repo_url,get_repo_info,list_repo_files,fetch_file
from gitmind.indexing.filters import should_include
from gitmind.indexing.chunkers import chunk_file
from gitmind.retrieval.qdrant_store import create_collection, build_points,store_points,delete_repository_chunks



def index_repository(repo_url: str):
    owner, repo = parse_repo_url(repo_url)
    repo_info = get_repo_info(owner, repo)
    default_branch = repo_info["default_branch"]

    files = list_repo_files(owner, repo, default_branch)

    create_collection("gitmind_code")
    delete_repository_chunks(repo_url)

    indexed_files = 0
    indexed_chunks = 0

    batch = []
    BATCH_SIZE = 100

    for file in files:
        if not should_include(file["path"], file["size"]):
            continue

        content = fetch_file(owner, repo, file["path"])

        if content is None:
            continue

        indexed_files += 1
        chunks = chunk_file(content, file["path"])

        for chunk in chunks:
            batch.append(chunk)
            indexed_chunks += 1

            if len(batch) >= BATCH_SIZE:
                points = build_points(batch, repo_url)
                store_points(points)
                batch = []

    # Process any remaining chunks
    if batch:
        points = build_points(batch, repo_url)
        store_points(points)

    print(f"Indexed files: {indexed_files}")
    print(f"Indexed chunks: {indexed_chunks}")
