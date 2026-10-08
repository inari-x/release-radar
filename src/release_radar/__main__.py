import sys

import httpx

from release_radar.parsers import parse_requirements
from release_radar.pypi import fetch_latest_version
from release_radar.pypi import fetch_package


def main() -> None:
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        deps = parse_requirements(f.read())

    with httpx.Client(timeout=10) as client:
        for dep in deps:
            package = fetch_package(dep.name, client)
            latest = package.latest_version if package else None
            print(f"{dep.name:35} {dep.specifier or '(any)':10} latest: {latest}")


if __name__ == "__main__":
    main()