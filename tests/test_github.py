from release_radar.github import find_github_repo


def test_finds_repo_from_source_url():
    urls = {
        "Documentation": "https://requests.readthedocs.io",
        "Source": "https://github.com/psf/requests",
    }
    assert find_github_repo(urls) == "psf/requests"


def test_ignores_trailing_slash():
    assert find_github_repo({"Source": "https://github.com/pallets/flask/"}) == "pallets/flask"


def test_strips_extra_path():
    urls = {"Changelog": "https://github.com/encode/httpx/blob/master/CHANGELOG.md"}
    assert find_github_repo(urls) == "encode/httpx"


def test_returns_none_without_github_link():
    assert find_github_repo({"Documentation": "https://example.com"}) is None


def test_returns_none_when_no_urls():
    assert find_github_repo(None) is None