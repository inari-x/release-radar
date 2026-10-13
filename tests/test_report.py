from release_radar.classify import ClassifiedChange
from release_radar.report import DependencyResult, format_cli_line


def breaking_change(summary):
    return ClassifiedChange(summary=summary, category="breaking", reason="r")


def test_skipped_line():
    result = DependencyResult(name="fastapi", status="skipped")
    assert format_cli_line(result) == "skipped (not pinned)"


def test_not_found_line():
    result = DependencyResult(name="nope", status="not_found")
    assert format_cli_line(result) == "not found on PyPI"


def test_checked_line_counts_changes():
    result = DependencyResult(
        name="flask",
        status="checked",
        current="2.2.0",
        latest="3.1.3",
        new_releases=17,
        breaking=[breaking_change("Removed escape"), breaking_change("Dropped Python 3.8")],
    )
    assert format_cli_line(result) == "2.2.0 → 3.1.3   17 new releases · 2 breaking · 0 deprecation(s)"


def test_no_repo_line():
    result = DependencyResult(name="x", status="no_repo", current="1.0", latest="2.0")
    assert format_cli_line(result) == "1.0 → 2.0   no GitHub repo found"