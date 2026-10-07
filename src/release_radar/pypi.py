import httpx

PYPI_URL = "https://pypi.org/pypi/{name}/json"


def fetch_latest_version(name: str, client: httpx.Client) -> str | None:
    """Return the latest version of a PyPI package, or None if it doesn't exist."""
    response = client.get(PYPI_URL.format(name=name))
    if response.status_code == 200:
        return response.json()["info"]["version"]
    return None

def fetch_latest_version(name: str, client: httpx.Client) -> str | None:
    """Return the latest version of a PyPI package, or None if it doesn't exist."""
    response = client.get(PYPI_URL.format(name=name))
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()["info"]["version"]