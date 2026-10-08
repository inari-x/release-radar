import httpx
import pytest

from release_radar.pypi import Package, fetch_package

def test_raises_on_server_error():
    def handler(request):
        return httpx.Response(500)

    with pytest.raises(httpx.HTTPStatusError):
        fetch_package("requests", make_client(handler))


def make_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_returns_latest_version_and_project_urls():
    def handler(request):
        assert request.url.path == "/pypi/requests/json"
        return httpx.Response(200, json={"info": {
            "version": "2.32.3",
            "project_urls": {"Source": "https://github.com/psf/requests"},
        }})

    assert fetch_package("requests", make_client(handler)) == Package(
        latest_version="2.32.3",
        project_urls={"Source": "https://github.com/psf/requests"},
    )


def test_missing_project_urls_become_empty_dict():
    def handler(request):
        return httpx.Response(200, json={"info": {"version": "1.0", "project_urls": None}})

    assert fetch_package("x", make_client(handler)).project_urls == {}


def test_returns_none_for_unknown_package():
    def handler(request):
        return httpx.Response(404)
    

    assert fetch_package("does-not-exist", make_client(handler)) is None