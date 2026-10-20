import pytest

from gitmind.indexing.filters import should_include


@pytest.mark.parametrize(
    "path, size, expected",
    [
        ("src/app.py", 1_000, True),
        ("README.md", 500, True),
        ("Dockerfile", 200, True),
        ("docs/index.md", 1_000, True),
        ("build_utils.py", 1_000, True),
        ("src/app.py", 0, False),
        ("src/big.py", 300_000, False),
        ("node_modules/lib/index.js", 1_000, False),
        ("src/build/output.py", 1_000, False),
        ("logo.png", 1_000, False),
        ("uv.lock", 1_000, False),
        ("package-lock.json", 1_000, False),
        ("static/app.min.js", 1_000, False),
        (".gitignore", 100, False),
        ("HISTORY.md", 1_000, False),
        ("docs/fr/index.md", 1_000, False),
        ("scripts/tool.py", 500, False),
        ("eval/run_eval.py", 500, False),
    ],
)
def test_should_include(path, size, expected):
    assert should_include(path, size) is expected