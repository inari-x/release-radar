from types import SimpleNamespace

import httpx

from release_radar.__main__ import check_dependency, parse_args
from release_radar.classify import ClassifiedChange, ReleaseClassification
from release_radar.parsers import Dependency
from release_radar.report import Change


def fake_http():
    """One fake server for both PyPI and GitHub: one package, one newer release."""
    def handler(request):
        if request.url.host == "pypi.org":
            return httpx.Response(200, json={"info": {
                "version": "2.0.0",
                "project_urls": {"Source": "https://github.com/me/pkg"},
            }})
        return httpx.Response(200, json=[{"tag_name": "2.0.0", "body": "Removed foo"}])
    return httpx.Client(transport=httpx.MockTransport(handler))


def fake_llm(*changes):
    """Fake OpenAI client: every classify call returns these changes."""
    result = SimpleNamespace(output_parsed=ReleaseClassification(changes=list(changes)))
    return SimpleNamespace(responses=SimpleNamespace(parse=lambda **kwargs: result))


def test_check_dependency_attaches_release_version_to_changes():
    dep = Dependency(name="pkg", specifier="==1.0.0", ecosystem="pypi")
    llm = fake_llm(ClassifiedChange(summary="Removed foo", category="breaking", reason="API removed"))
    http = fake_http()

    result = check_dependency(dep, http, http, llm, "fake-model")

    assert result.status == "checked"
    assert result.breaking == [Change(version="2.0.0", summary="Removed foo")]


def test_publish_is_off_by_default():
    args = parse_args(["requirements.txt"])
    assert args.requirements == "requirements.txt"
    assert args.publish is None


def test_publish_takes_a_repo():
    args = parse_args(["requirements.txt", "--publish", "me/repo"])
    assert args.publish == "me/repo"