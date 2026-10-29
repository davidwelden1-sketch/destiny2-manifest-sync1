"""Load explicitly scoped, sourced official patch-note values.

Patch-note values are not repeated gameplay measurements or current-game certification.
"""
import json
from datetime import date
from math import isfinite
from urllib.parse import urlparse

def load_patch_notes(path):
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or payload.get("provenance") != "official_patch_notes":
        raise ValueError("official patch-note provenance required")
    url = payload.get("source_url")
    if not isinstance(url, str) or urlparse(url).scheme != "https" or not urlparse(url).hostname:
        raise ValueError("valid source URL required")
    date.fromisoformat(payload["published_on"])
    if not isinstance(payload.get("game_version"), str) or not payload["game_version"]:
        raise ValueError("game version required")
    observations = payload.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("observations required")
    for row in observations:
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k]
            for k in ("id", "category", "archetype", "activity", "metric", "unit", "qualification")):
            raise ValueError("incomplete observation")
        for key in ("old_value", "new_value"):
            if type(row.get(key)) not in (int, float) or not isfinite(row[key]):
                raise ValueError("invalid patch-note value")
    return payload
