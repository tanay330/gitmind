import pytest

from gitmind.indexing.github_client import parse_repo_url


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/pallets/click",
        "https://github.com/pallets/click/",
        "https://github.com/pallets/click.git",
        "https://github.com/pallets/click/tree/main/src",
        "https://www.github.com/pallets/click",
        "  https://github.com/pallets/click  ",
    ],
)
def test_parse_repo_url_accepts_common_forms(url):
    assert parse_repo_url(url) == ("pallets", "click")


@pytest.mark.parametrize(
    "url",
    ["https://example.com/a/b", "https://github.com/pallets", "not a url", ""],
)
def test_parse_repo_url_rejects_bad_input(url):
    with pytest.raises(ValueError):
        parse_repo_url(url)