from dataclasses import dataclass, field
from typing import Literal

from release_radar.classify import ClassifiedChange

Status = Literal["checked", "skipped", "not_found", "no_repo", "repo_not_found"]


@dataclass(frozen=True)
class DependencyResult:
    name: str
    status: Status
    current: str | None = None
    latest: str | None = None
    new_releases: int = 0
    breaking: list[ClassifiedChange] = field(default_factory=list)
    deprecations: list[ClassifiedChange] = field(default_factory=list)


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