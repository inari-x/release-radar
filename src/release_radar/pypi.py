import httpx

PYPI_URL = "https://pypi.org/pypi/{name}/json"


def fetch_latest_version(name: str, client: httpx.Client) -> str | None:
    """Return the latest version of a PyPI package, or None if it doesn't exist."""
    ...