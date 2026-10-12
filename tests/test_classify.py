import pytest
from pydantic import ValidationError

from release_radar.classify import (
    MAX_NOTES_CHARS,
    ClassifiedChange,
    ReleaseClassification,
    classify_release,
)

from release_radar.classify import ClassifiedChange


def test_accepts_known_category():
    change = ClassifiedChange(summary="Removed flask.escape", category="breaking", reason="Public function removed")
    assert change.category == "breaking"


def test_rejects_unknown_category():
    with pytest.raises(ValidationError):
        ClassifiedChange(summary="x", category="probably-fine", reason="y")

def test_rejects_missing_reason():
    with pytest.raises(ValidationError):
        ClassifiedChange(summary="x", category="feature")

class FakeResult:
    def __init__(self, parsed):
        self.output_parsed = parsed


class FakeResponses:
    def __init__(self, answer):
        self.answer = answer
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResult(self.answer)


class FakeClient:
    def __init__(self, answer=None):
        self.responses = FakeResponses(answer)


def test_returns_classification_from_model():
    answer = ReleaseClassification(changes=[
        ClassifiedChange(summary="Removed flask.escape", category="breaking", reason="Public function removed"),
    ])
    client = FakeClient(answer)
    assert classify_release("- Removed flask.escape", client, "test-model") == answer


def test_sends_notes_model_and_schema():
    client = FakeClient(ReleaseClassification(changes=[]))
    classify_release("- Fixed a bug", client, "test-model")

    call = client.responses.calls[0]
    assert call["model"] == "test-model"
    assert "- Fixed a bug" in call["input"][1]["content"]
    assert call["text_format"] is ReleaseClassification


def test_empty_notes_skip_the_api():
    client = FakeClient()
    assert classify_release("   ", client, "test-model") == ReleaseClassification(changes=[])
    assert client.responses.calls == []


def test_long_notes_are_truncated():
    client = FakeClient(ReleaseClassification(changes=[]))
    classify_release("x" * 50_000, client, "test-model")
    assert len(client.responses.calls[0]["input"][1]["content"]) <= MAX_NOTES_CHARS