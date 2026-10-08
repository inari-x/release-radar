from dataclasses import dataclass
from urllib import response

import httpx
from urllib.parse import urlparse


def find_github_repo(project_urls: dict[str, str] | None) -> str | None:
    """Return 'owner/repo' from the first GitHub link in a package's project URLs, or None."""
    if not project_urls:
        return None

    for url in project_urls.values():
        parsed = urlparse(url)
        if parsed.netloc == "github.com":
            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) >= 2:
                return "/".join(path_parts[:2])

    return None

GITHUB_RELEASES_URL = "https://api.github.com/repos/{repo}/releases"


@dataclass(frozen=True)
class Release:
    tag: str
    notes: str


def fetch_releases(repo: str, client: httpx.Client) -> list[Release] | None:
    """Return a repo's releases, newest first, or None if the repo doesn't exist."""
    response = client.get(GITHUB_RELEASES_URL.format(repo=repo))
    if response.status_code == 404:
        return None
    if response.status_code == 404:
       return None
    response.raise_for_status()
    return [
        Release(tag=release["tag_name"], notes=release.get("body", "") or "")
        for release in response.json()
    ]