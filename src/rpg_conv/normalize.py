import re


_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_marker(value: str) -> str:
    """
    Normalize marker text for robust lookup.

    - trims whitespace
    - case-insensitive (lowercased)
    - removes punctuation and separators (e.g. ki--67, ki 67 -> ki67)
    """
    lowered = value.strip().lower()
    return _NON_ALNUM.sub("", lowered)

__all__ = ["normalize_marker"]
