from release_radar.versions import pinned_version


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