from datetime import date

from release_radar.report import Change, DependencyResult, format_cli_line, format_issue, group_changes, issue_title

def breaking_change(summary):
    return Change(version="1.0.0", summary=summary)


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


def test_issue_title_uses_monday_of_the_week():
    assert issue_title(date(2026, 10, 15)) == "Release Radar: week of 2026-10-12"   # a Thursday


def test_issue_title_on_a_monday():
    assert issue_title(date(2026, 10, 12)) == "Release Radar: week of 2026-10-12"


def test_issue_lists_breaking_changes_under_package():
    flask = DependencyResult(
        name="flask", status="checked", current="2.2.0", latest="3.1.3",
        new_releases=17, breaking=[breaking_change("Removed escape")],
    )
    body = format_issue([flask])
    assert "### flask 2.2.0 → 3.1.3" in body
    assert "- Removed escape" in body


def test_issue_says_when_nothing_needs_attention():
    calm = DependencyResult(name="requests", status="checked", current="2.32.0", latest="2.32.1", new_releases=1)
    assert "No breaking changes or deprecations found this week." in format_issue([calm])


def test_issue_lists_packages_that_were_not_checked():
    skipped = DependencyResult(name="fastapi", status="skipped")
    assert "- fastapi: skipped (not pinned)" in format_issue([skipped])

def test_group_changes_adds_version():
    assert group_changes([Change("3.0.0", "Removed x")]) == ["Removed x (3.0.0)"]


def test_group_changes_merges_same_summary():
    changes = [Change("3.0.0", "Removed x"), Change("2.3.0", "Removed x")]
    assert group_changes(changes) == ["Removed x (3.0.0, 2.3.0)"]


def test_group_changes_keeps_order():
    changes = [Change("3.0.0", "B"), Change("2.3.0", "A")]
    assert group_changes(changes) == ["B (3.0.0)", "A (2.3.0)"]