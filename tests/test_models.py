from gitmind.models import Chunk, make_repo_id, split_identifiers


def make_chunk(**overrides):
    values = dict(
        repo_id="me/demo",
        path="a.py",
        symbol_name="f",
        symbol_type="function",
        start_line=1,
        end_line=3,
        language="python",
        text="def f(): pass",
    )
    values.update(overrides)
    return Chunk(**values)


def test_repo_id_is_lowercase():
    assert make_repo_id("Tanay330", "GitMind") == "tanay330/gitmind"


def test_chunk_id_is_stable():
    assert make_chunk().id == make_chunk().id


def test_chunk_id_changes_with_position():
    assert make_chunk().id != make_chunk(start_line=2).id


def test_embedding_text_contains_path_symbol_description_and_code():
    text = make_chunk(description="Does a thing").embedding_text()
    assert "File: a.py" in text
    assert "Symbol: f (function)" in text
    assert "Does a thing" in text
    assert "def f(): pass" in text


def test_split_identifiers():
    result = split_identifiers("resolve_redirects HTTPServer __version__ getNetrcAuth Session")
    assert result == "resolve redirects http server version get netrc auth"


def test_keyword_text_adds_words_from_the_path():
    chunk = make_chunk(path="src/requests/__version__.py", text="x = 1")
    assert "version" in chunk.keyword_text().split()