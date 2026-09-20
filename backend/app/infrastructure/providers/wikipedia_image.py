"""Fetch a thumbnail or page summary from the Persian Wikipedia REST API."""
import logging
from dataclasses import dataclass
from urllib.parse import quote

import httpx

logger = logging.getLogger("wanderpath.providers.wikipedia")

_TIMEOUT_SECONDS = 3.0
_USER_AGENT = "WanderPath/1.0 (domestic trip planner; https://github.com/wanderpath)"


@dataclass(frozen=True)
class WikipediaSummary:
    extract: str | None
    thumbnail: str | None
    original_image: str | None


def wikipedia_page_summary(title: str) -> WikipediaSummary | None:
    if not title or len(title) < 3:
        return None
    url = f"https://fa.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
    try:
        with httpx.Client(timeout=_TIMEOUT_SECONDS, headers={"User-Agent": _USER_AGENT}) as client:
            response = client.get(url)
            if response.status_code != 200:
                return None
            data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.debug("Wikipedia summary lookup failed for %s: %s", title, exc)
        return None

    thumbnail = data.get("thumbnail") or {}
    original = data.get("originalimage") or {}
    extract = data.get("extract")
    return WikipediaSummary(
        extract=extract if isinstance(extract, str) and extract.strip() else None,
        thumbnail=thumbnail.get("source") if isinstance(thumbnail.get("source"), str) else None,
        original_image=original.get("source") if isinstance(original.get("source"), str) else None,
    )


def wikipedia_thumbnail(title: str) -> str | None:
    summary = wikipedia_page_summary(title)
    if not summary:
        return None
    return summary.thumbnail or summary.original_image
