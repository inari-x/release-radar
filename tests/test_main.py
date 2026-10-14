from release_radar.__main__ import parse_args


def test_publish_is_off_by_default():
    args = parse_args(["requirements.txt"])
    assert args.requirements == "requirements.txt"
    assert args.publish is None


def test_publish_takes_a_repo():
    args = parse_args(["requirements.txt", "--publish", "me/repo"])
    assert args.publish == "me/repo"