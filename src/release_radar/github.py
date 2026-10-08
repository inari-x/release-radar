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