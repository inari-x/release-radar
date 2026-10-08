import logging
from dataclasses import dataclass

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Dependency:
    name: str
    specifier: str
    ecosystem: str


def parse_requirements(text: str) -> list[Dependency]:
    """Parse requirements.txt content into dependencies, skipping comments, options and invalid lines."""
    deps = []
    for line in text.splitlines():
        line = line.split("#")[0].strip()
        if not line or line.startswith("-"):
            continue

        try:
            req = Requirement(line)
        except InvalidRequirement:
            logger.warning("Invalid requirement: %s", line)
            continue

        deps.append(Dependency(
            name=canonicalize_name(req.name),
            specifier=str(req.specifier),
            ecosystem="pypi",
        ))
    return deps

