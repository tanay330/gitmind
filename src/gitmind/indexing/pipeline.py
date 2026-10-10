from gitmind.indexing.github_client import parse_repo_url,get_repo_info,list_repo_files,fetch_file
from gitmind.indexing.filters import should_include

def index_repository(repo_url: str):
    owner,repo=parse_repo_url(repo_url)
    repo_info=get_repo_info(owner,repo)
    default_branch=repo_info["default_branch"]
    size=repo_info["size"]
    files=list_repo_files(owner,repo,default_branch)
    for file in files:
        if should_include(file["path"],file["size"]):
            content=fetch_file(owner,repo,file["path"])
            if content is None:
                continue
    
    