"""Small text helpers shared across DTO serialization and cache ingest."""

SHORT_DESCRIPTION_MAX = 120


def shorten_description(value: str | None, max_length: int = SHORT_DESCRIPTION_MAX) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if len(stripped) <= max_length:
        return stripped
    return stripped[: max_length - 1].rstrip() + "…"
