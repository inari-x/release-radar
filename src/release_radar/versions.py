def pinned_version(specifier: str) -> str | None:
    """Return the exact version from an '==' pin, or None if the specifier is a range or missing."""
    if specifier.startswith("=="):
        if len(specifier) > 2 and "*" not in specifier and "," not in specifier:
            return specifier[2:]
    return None