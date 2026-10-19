from gitmind.indexing.filters import should_include
from gitmind.indexing.github_client import (
    fetch_file,
    get_repo_info,
    list_repo_files,
    parse_repo_url,
)

URLS = [
    "https://github.com/pallets/click",
    "https://github.com/pallets/click/",
    "https://github.com/pallets/click.git",
    "https://github.com/pallets/click/tree/main/src",
    "https://www.github.com/pallets/click",
]
for url in URLS:
    print(parse_repo_url(url))

for bad in ["https://example.com/a/b", "https://github.com/pallets"]:
    try:
        parse_repo_url(bad)
    except ValueError as error:
        print("error:", error)

owner, repo = parse_repo_url("https://github.com/tanay330/gitmind")
info = get_repo_info(owner, repo)
files = list_repo_files(owner, repo, info["default_branch"])
kept = [f for f in files if should_include(f["path"], f["size"])]
dropped = [f["path"] for f in files if not should_include(f["path"], f["size"])]

print(f"\n{len(files)} files in repo, {len(kept)} kept")
print("kept:", [f["path"] for f in kept[:12]])
print("dropped:", dropped[:12])

text = fetch_file(owner, repo, kept[0]["path"])
print("\nfirst file:", kept[0]["path"])
print(text[:200] if text else text)