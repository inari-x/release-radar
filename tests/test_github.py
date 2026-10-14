import httpx
import json
import pytest

from release_radar.github import Release, fetch_releases, find_github_repo, fetch_release, make_github_client, find_issue, publish_issue

TITLE = "Release Radar: week of 2026-10-12"


def issues_client(existing, calls):
    """Fake GitHub: GET returns `existing`, POST/PATCH succeed. Every request is recorded in `calls`."""
    def handler(request):
        calls.append(request)
        if request.method == "GET":
            return httpx.Response(200, json=existing)
        if request.method == "POST":
            return httpx.Response(201, json={"number": 99})
        return httpx.Response(200, json={"number": 7})
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_find_issue_returns_number_for_exact_title():
    existing = [{"number": 3, "title": "Something else"}, {"number": 7, "title": TITLE}]
    assert find_issue("me/repo", TITLE, issues_client(existing, [])) == 7


def test_find_issue_ignores_last_weeks_issue():
    existing = [{"number": 5, "title": "Release Radar: week of 2026-10-05"}]
    assert find_issue("me/repo", TITLE, issues_client(existing, [])) is None


def test_publish_creates_issue_when_none_exists():
    calls = []
    assert publish_issue("me/repo", TITLE, "body", issues_client([], calls)) == "created"
    assert calls[-1].method == "POST"


def test_publish_updates_existing_issue():
    calls = []
    existing = [{"number": 7, "title": TITLE}]
    assert publish_issue("me/repo", TITLE, "new body", issues_client(existing, calls)) == "updated"
    assert calls[-1].method == "PATCH"
    assert calls[-1].url.path.endswith("/issues/7")
    assert json.loads(calls[-1].content) == {"body": "new body"}

def test_github_client_sends_token():
    with make_github_client("abc") as client:
        assert client.headers["Authorization"] == "Bearer abc"


def test_github_client_without_token_sends_no_auth():
    with make_github_client(None) as client:
        assert "Authorization" not in client.headers


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

def test_fetch_release_by_tag():
    def handler(request):
        assert request.url.path == "/repos/pallets/flask/releases/tags/3.0.0"
        return httpx.Response(200, json={"tag_name": "3.0.0", "body": "- Removed old code"})

    assert fetch_release("pallets/flask", "3.0.0", make_client(handler)) == Release(
        tag="3.0.0", notes="- Removed old code"
    )


def test_fetch_release_unknown_tag_returns_none():
    def handler(request):
        return httpx.Response(404)

    assert fetch_release("pallets/flask", "99.0.0", make_client(handler)) is None