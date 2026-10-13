import os
import sys

import httpx
from dotenv import load_dotenv
from openai import OpenAI

from release_radar.classify import classify_release, count_category
from release_radar.github import fetch_releases, find_github_repo
from release_radar.parsers import Dependency, parse_requirements
from release_radar.pypi import fetch_package
from release_radar.versions import pinned_version, releases_newer_than
from release_radar.report import DependencyResult


def check_dependency(dep: Dependency, http: httpx.Client, llm: OpenAI, model: str) -> DependencyResult:
    """Check one dependency and return the result as data."""
    current = pinned_version(dep.specifier)
    if current is None:
        return DependencyResult(name=dep.name, status="skipped")

    package = fetch_package(dep.name, http)
    if package is None:
        return DependencyResult(name=dep.name, status="not_found")

    latest = package.latest_version
    github_repo = find_github_repo(package.project_urls)
    if github_repo is None:
        return DependencyResult(name=dep.name, status="no_repo", current=current, latest=latest)

    releases = fetch_releases(github_repo, http)
    if releases is None:
        return DependencyResult(name=dep.name, status="repo_not_found", current=current, latest=latest)

    newer = releases_newer_than(releases, current)
    changes = [
        change
        for release in newer
        for change in classify_release(release.notes, llm, model).changes
    ]
    return DependencyResult(
        name=dep.name,
        status="checked",
        current=current,
        latest=latest,
        new_releases=len(newer),
        breaking=[c for c in changes if c.category == "breaking"],
        deprecations=[c for c in changes if c.category == "deprecation"],
    )


def main() -> None:
    load_dotenv()
    model = os.environ["OPENAI_MODEL"]
    llm = OpenAI()

    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        deps = parse_requirements(f.read())

    with httpx.Client(timeout=10, follow_redirects=True) as http:
        results = [check_dependency(dep, http, llm, model) for dep in deps]

    for result in results:
        print(f"{result.name:35} {format_cli_line(result)}")


if __name__ == "__main__":
    main()