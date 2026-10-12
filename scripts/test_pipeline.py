from gitmind.indexing.pipeline import index_repository

if __name__ == "__main__":
    repo_url = input("Enter GitHub repository URL: ").strip()
    index_repository(repo_url)