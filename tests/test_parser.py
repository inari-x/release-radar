from release_radar.parsers import Dependency, parse_requirements


def test_parses_pinned_and_ranged_versions():
    text = "requests==2.31.0\nhttpx>=0.27\n"
    assert parse_requirements(text) == [
        Dependency(name="requests", specifier="==2.31.0", ecosystem="pypi"),
        Dependency(name="httpx", specifier=">=0.27", ecosystem="pypi"),
    ]


def test_ignores_comments_blank_lines_and_options():
    text = "# web stuff\n\n-r base.txt\nflask==3.0.0  # pinned\n"
    assert [d.name for d in parse_requirements(text)] == ["flask"]


def test_handles_extras_and_markers():
    text = 'fastapi[standard]==0.115.0 ; python_version >= "3.10"\n'
    assert parse_requirements(text)[0].name == "fastapi"