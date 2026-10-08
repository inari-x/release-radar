import httpx
import pytest

from release_radar.github import Release, fetch_releases, find_github_repo


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

def make_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_returns_releases_with_tag_and_notes():
    def handler(request):
        assert request.url.path == "/repos/pallets/flask/releases"
        return httpx.Response(200, json=[
            {"tag_name": "3.1.3", "name": "3.1.3", "body": "- Fix a bug"},
            {"tag_name": "3.1.2", "name": "3.1.2", "body": "- Another fix"},
        ])

    assert fetch_releases("pallets/flask", make_client(handler)) == [
        Release(tag="3.1.3", notes="- Fix a bug"),
        Release(tag="3.1.2", notes="- Another fix"),
    ]


def test_missing_notes_become_empty_string():
    def handler(request):
        return httpx.Response(200, json=[{"tag_name": "1.0", "body": None}])

    assert fetch_releases("a/b", make_client(handler))[0].notes == ""


def test_returns_none_for_unknown_repo():
    def handler(request):
        return httpx.Response(404)

    assert fetch_releases("sponsors/someone", make_client(handler)) is None


def test_raises_on_server_error():
    def handler(request):
        return httpx.Response(500)

    with pytest.raises(httpx.HTTPStatusError):
        fetch_releases("pallets/flask", make_client(handler))