from dataclasses import dataclass

from packaging.requirements import Requirement


@dataclass(frozen=True)
class Dependency:
    name: str
    specifier: str
    ecosystem: str


def parse_requirements(text: str) -> list[Dependency]:
    deps = []
    for line in text.splitlines():
        # 1. remove everything after "#"
        line = line.split("#")[0]
        
        # 2. strip whitespace from both ends
        line = line.strip()
        
        # 3. if the line is empty or starts with "-", skip it (continue)
        if not line or line.startswith("-"):
            continue
            
        # 4. req = Requirement(line)
        req = Requirement(line)

        # 5. append Dependency(name=..., specifier=..., ecosystem="pypi")
        deps.append(Dependency(
            name=req.name,
            specifier=str(req.specifier),
            ecosystem="pypi"
        ))
    return deps