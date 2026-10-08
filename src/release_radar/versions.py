import logging

from packaging.version import InvalidVersion, Version
from release_radar.github import Release

logger = logging.getLogger(__name__)


def pinned_version(specifier: str) -> str | None:
    """Return the exact version from an '==' pin, or None if the specifier is a range or missing."""
    if specifier.startswith("=="):
        if len(specifier) > 2 and "*" not in specifier and "," not in specifier:
            return specifier[2:]
    return None

def releases_newer_than(releases: list[Release], current: str) -> list[Release]:
    """Return releases newer than `current`, skipping pre-releases and tags that aren't versions."""
    try:
        current_version = Version(current)
    except InvalidVersion:
        logger.warning(f"Invalid version format: {current}")
        return []

    newer_releases = []
    for release in releases:
        try:
            release_version = Version(release.tag)
        except InvalidVersion:
            logger.warning(f"Skipping invalid version format: {release.tag}")
            continue

        if release_version.is_prerelease:
            continue

        if release_version > current_version:
            newer_releases.append(release)

    return newer_releases