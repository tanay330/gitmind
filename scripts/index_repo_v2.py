import sys

from gitmind.indexing.pipeline import index_repository

url = sys.argv[1] if len(sys.argv) > 1 else input("GitHub repository URL: ").strip()
print(index_repository(url))