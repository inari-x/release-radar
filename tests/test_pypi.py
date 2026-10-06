import httpx
import pytest

from release_radar.pypi import fetch_latest_version

def test_raises_on_server_error():
    def handler(request):
        return httpx.Response(500)

    with pytest.raises(httpx.HTTPStatusError):
        fetch_latest_version("requests", make_client(handler))
        
    
    with pytest.raises(httpx.HTTPStatusError):
        fetch_latest_version("requests", httpx.Client(transport=httpx.MockTransport(handler)))


def make_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_returns_latest_version():
    def handler(request):
        assert request.url.path == "/pypi/requests/json"
        return httpx.Response(200, json={"info": {"version": "2.32.3"}})

    assert fetch_latest_version("requests", make_client(handler)) == "2.32.3"


def test_returns_none_for_unknown_package():
    def handler(request):
        return httpx.Response(404)
    

    assert fetch_latest_version("does-not-exist", make_client(handler)) is None