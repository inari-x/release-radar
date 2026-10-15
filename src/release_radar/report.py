from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal

Status = Literal["checked", "skipped", "not_found", "no_repo", "repo_not_found"]


@dataclass(frozen=True)
class Change:
    version: str
    summary: str


@dataclass(frozen=True)
class DependencyResult:
    name: str
    status: Status
    current: str | None = None
    latest: str | None = None
    new_releases: int = 0
    breaking: list[Change] = field(default_factory=list)
    deprecations: list[Change] = field(default_factory=list)


def format_cli_line(result: DependencyResult) -> str:
    """Return the one-line terminal status for a dependency (without the name)."""
    versions = f"{result.current} → {result.latest}"
    return {
        "checked": (
            f"{versions}   {result.new_releases} new releases"
            f" · {len(result.breaking)} breaking · {len(result.deprecations)} deprecation(s)"
        ),
        "skipped": "skipped (not pinned)",
        "not_found": "not found on PyPI",
        "no_repo": f"{versions}   no GitHub repo found",
        "repo_not_found": f"{versions}   GitHub repo not found",
    }[result.status]

def group_changes(changes: list[Change]) -> list[str]:
    """One line per distinct summary, listing every version it appeared in."""
    versions: dict[str, list[str]] = {}
    for change in changes:
        if change.summary not in versions:
            versions[change.summary] = []
        versions[change.summary].append(change.version)
    return [f"{summary} ({', '.join(tags)})" for summary, tags in versions.items()]

def issue_title(today: date) -> str:
    """Title of the weekly issue, named after the Monday of today's week."""
    monday = today - timedelta(days=today.weekday())
    return f"Release Radar: week of {monday.isoformat()}"


def format_issue(results: list[DependencyResult]) -> str:
    """Render the weekly report as GitHub Markdown."""
    attention = [r for r in results if r.status == "checked" and (r.breaking or r.deprecations)]
    calm = [r for r in results if r.status == "checked" and not (r.breaking or r.deprecations)]
    not_checked = [r for r in results if r.status != "checked"]

    lines = ["## Needs attention"]
    if not attention:
        lines.append("No breaking changes or deprecations found this week.")
    for r in attention:
        lines.append(f"### {r.name} {r.current} → {r.latest}")
        lines.append(f"{r.new_releases} new releases")
        if r.breaking:
            lines.append("**Breaking**")
            lines.extend(f"- {line}" for line in group_changes(r.breaking))
        if r.deprecations:
            lines.append("**Deprecations**")
            lines.extend(f"- {line}" for line in group_changes(r.deprecations))
    if calm:
        lines.append("## No action needed")
        lines.extend(f"- {r.name}: {format_cli_line(r)}" for r in calm)

    if not_checked:
        lines.append("## Not checked")
        lines.extend(f"- {r.name}: {format_cli_line(r)}" for r in not_checked)  

    return "\n\n".join(lines)