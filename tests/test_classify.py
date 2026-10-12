import pytest
from pydantic import ValidationError

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
