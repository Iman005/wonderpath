"""Parse Place.details_json into a dict the destination DTOs can expose."""
from __future__ import annotations

import json


def parse_place_catalog(raw: object) -> dict | None:
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def dump_place_catalog(catalog: dict | None) -> str | None:
    if not catalog:
        return None
    return json.dumps(catalog, ensure_ascii=False)
