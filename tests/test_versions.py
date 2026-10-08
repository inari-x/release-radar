from release_radar.github import Release
from release_radar.versions import pinned_version, releases_newer_than


def test_exact_pin_returns_version():
    assert pinned_version("==2.2.0") == "2.2.0"


def test_range_is_not_pinned():
    assert pinned_version(">=0.100") is None


def test_no_specifier_is_not_pinned():
    assert pinned_version("") is None


def test_wildcard_is_not_pinned():
    assert pinned_version("==2.*") is None


def test_multiple_conditions_are_not_pinned():
    assert pinned_version("<2,>=1.0") is None

def test_pin_with_extra_condition_is_not_pinned():
    assert pinned_version("==1.0,<2") is None

def test_keeps_only_newer_releases():
    releases = [Release("3.1.3", "a"), Release("3.0.0", "b"), Release("2.2.0", "c"), Release("2.1.0", "d")]
    assert releases_newer_than(releases, "2.2.0") == [Release("3.1.3", "a"), Release("3.0.0", "b")]


def test_understands_v_prefix():
    releases = [Release("v0.28.0", "x"), Release("v0.27.0", "y")]
    assert releases_newer_than(releases, "0.27.0") == [Release("v0.28.0", "x")]


def test_skips_tags_that_are_not_versions():
    releases = [Release("flask-3.1.3", "x"), Release("3.1.2", "y")]
    assert releases_newer_than(releases, "3.0.0") == [Release("3.1.2", "y")]


def test_skips_prereleases():
    releases = [Release("4.0.0rc1", "x"), Release("3.1.3", "y")]
    assert releases_newer_than(releases, "3.0.0") == [Release("3.1.3", "y")]


def test_compares_versions_not_text():
    releases = [Release("2.10.0", "x")]
    assert releases_newer_than(releases, "2.9.0") == [Release("2.10.0", "x")]