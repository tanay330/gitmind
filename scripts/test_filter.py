
from gitmind.indexing.filters import should_include

checks = [
    ("English docs", "docs/en/docs/async.md", True),
    ("Hindi docs", "docs/hi/docs/async.md", False),
    ("Routing source", "fastapi/routing.py", True),
    ("Dependency utils", "fastapi/dependencies/utils.py", True),
    ("Large file", "fastapi/large.py", False, 1_000_001),
]

for check in checks:
    name, path, expected = check[:3]
    size = check[3] if len(check) == 4 else 1000

    actual = should_include(path, size)
    status = "PASS" if actual == expected else "FAIL"

    print(f"{status}: {name} | expected={expected}, actual={actual}")
