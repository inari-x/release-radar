import sys

import httpx

from release_radar.github import fetch_releases, find_github_repo
from release_radar.parsers import Dependency, parse_requirements
from release_radar.pypi import fetch_package
from release_radar.versions import pinned_version, releases_newer_than


def check_dependency(dep: Dependency, client: httpx.Client) -> str:
    """Return a one-line status for a single dependency."""
    current = pinned_version(dep.specifier)
    if current is None:
        return "skipped (not pinned)"


    package = fetch_package(dep.name, client)
    if package is None:
        return "not found on PyPI"


    github_repo = find_github_repo(package.project_urls)
    if github_repo is None:
        return f"{current} → {package.latest_version}   no GitHub repo found"


    releases = fetch_releases(github_repo, client)
    if releases is None:
        return f"{current} → {package.latest_version}   GitHub repo not found"


    newer_releases = releases_newer_than(releases, current)
    return f"{current} → {package.latest_version}   {len(newer_releases)} new releases"


def main() -> None:
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        deps = parse_requirements(f.read())

    with httpx.Client(timeout=10, follow_redirects=True) as client:
        for dep in deps:
            print(f"{dep.name:35} {check_dependency(dep, client)}")


if __name__ == "__main__":
    main()