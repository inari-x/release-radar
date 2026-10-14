from dataclasses import dataclass
import httpx
from urllib.parse import urlparse

GITHUB_ISSUES_URL = "https://api.github.com/repos/{repo}/issues"


def find_issue(repo: str, title: str, client: httpx.Client) -> int | None:
    """Return the number of the open issue with exactly this title, or None."""
    response = client.get(GITHUB_ISSUES_URL.format(repo=repo), params={"state": "open", "per_page": 100})
    response.raise_for_status()
    # TODO (you): loop over response.json(); return the issue's "number" if its "title" == title
    for issue in response.json():
        if issue["title"] == title:
            return issue["number"]
    return None


def publish_issue(repo: str, title: str, body: str, client: httpx.Client) -> str:
    """Create this week's issue, or update it if it already exists. Returns "created" or "updated"."""
    url = GITHUB_ISSUES_URL.format(repo=repo)
    number = find_issue(repo, title, client)
    if number is None:
        client.post(url, json={"title": title, "body": body}).raise_for_status()
        return "created"
    client.patch(f"{url}/{number}", json={"body": body}).raise_for_status()
    return "updated"


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
    response.raise_for_status()
    return [
        Release(tag=release["tag_name"], notes=release.get("body", "") or "")
        for release in response.json()
    ]

GITHUB_RELEASE_BY_TAG_URL = "https://api.github.com/repos/{repo}/releases/tags/{tag}"


def fetch_release(repo: str, tag: str, client: httpx.Client) -> Release | None:
    """Return one release by its tag, or None if it doesn't exist."""
    response = client.get(GITHUB_RELEASE_BY_TAG_URL.format(repo=repo, tag=tag))
    if response.status_code == 404:
        return None
    response.raise_for_status()
    release = response.json()
    return Release(tag=release["tag_name"], notes=release.get("body", "") or "")

def make_github_client(token: str | None) -> httpx.Client:
    """HTTP client for api.github.com. Only this client ever carries the token."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.Client(timeout=10, follow_redirects=True, headers=headers)