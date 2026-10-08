import httpx
from dataclasses import dataclass


@dataclass(frozen=True)
class Package:
    latest_version: str
    project_urls: dict[str, str]

PYPI_URL = "https://pypi.org/pypi/{name}/json"


def fetch_package(name: str, client: httpx.Client) -> Package | None:
    """Return the latest version and project URLs of a PyPI package, or None if it doesn't exist."""
    response = client.get(PYPI_URL.format(name=name))
    if response.status_code == 404:
        return None
    response.raise_for_status()
    info = response.json()["info"]
    return Package(
        latest_version=info["version"],
        project_urls=info.get("project_urls") or {},    )

