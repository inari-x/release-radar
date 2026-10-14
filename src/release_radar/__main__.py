import argparse
import os
import sys
from datetime import date

import httpx
from dotenv import load_dotenv
from openai import OpenAI

from release_radar.classify import classify_release
from release_radar.github import fetch_releases, find_github_repo, make_github_client, publish_issue
from release_radar.parsers import parse_requirements
from release_radar.pypi import fetch_package
from release_radar.report import DependencyResult, format_cli_line, format_issue, issue_title
from release_radar.versions import pinned_version, releases_newer_than


def check_dependency(dep, pypi, github, llm, model) -> DependencyResult:
    """Check one dependency and return the result as data."""
    current = pinned_version(dep.specifier)
    if current is None:
        return DependencyResult(name=dep.name, status="skipped")

    package = fetch_package(dep.name, pypi)
    if package is None:
        return DependencyResult(name=dep.name, status="not_found")

    latest = package.latest_version
    github_repo = find_github_repo(package.project_urls)
    if github_repo is None:
        return DependencyResult(name=dep.name, status="no_repo", current=current, latest=latest)

    releases = fetch_releases(github_repo, github)
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="release_radar",
        description="Check pinned dependencies for breaking changes in newer releases.",
    )
    parser.add_argument("requirements", help="path to a requirements.txt file")
    parser.add_argument(
        "--publish", metavar="OWNER/REPO",
        help="also post the weekly report as a GitHub issue in this repo (needs GITHUB_TOKEN)",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args(sys.argv[1:])
    load_dotenv()
    token = os.environ.get("GITHUB_TOKEN")
    if args.publish and not token:
        sys.exit("Error: GITHUB_TOKEN is required when using --publish")

    model = os.environ["OPENAI_MODEL"]
    llm = OpenAI()

    with open(args.requirements, encoding="utf-8") as f:
        deps = parse_requirements(f.read())

    with httpx.Client(timeout=10, follow_redirects=True) as pypi, make_github_client(token) as github:
        results = [check_dependency(dep, pypi, github, llm, model) for dep in deps]
        for result in results:
            print(f"{result.name:35} {format_cli_line(result)}")
        if args.publish:
            title = issue_title(date.today())
            outcome = publish_issue(args.publish, title, format_issue(results), github)
            print(f"\nIssue {outcome}: {title}")


if __name__ == "__main__":
    main()