"""Phase 2 measurement aggregation with explicit provenance and uncertainty.

Records represent user-provided observations, not independently verified data.
No source or number is invented by this module.
"""
from math import isfinite, sqrt
from statistics import mean, stdev

def summarize_measurements(records, *, minimum_samples=3):
    if type(minimum_samples) is not int or minimum_samples < 2:
        raise ValueError("minimum_samples must be at least 2")
    if not isinstance(records, (list, tuple)) or len(records) < minimum_samples:
        raise ValueError("insufficient measurement records")
    keys = ("metric", "game_version", "activity", "scenario", "unit")
    first = records[0]
    if not isinstance(first, dict):
        raise ValueError("malformed measurement record")
    context = {key: first.get(key) for key in keys}
    if any(not isinstance(value, str) or not value.strip() for value in context.values()):
        raise ValueError("measurement context incomplete")
    values, sources = [], []
    for record in records:
        if not isinstance(record, dict) or any(record.get(key) != context[key] for key in keys):
            raise ValueError("incompatible measurement contexts")
        value = record.get("value")
        if type(value) not in (int, float) or not isfinite(value):
            raise ValueError("measurement must be a finite number")
        url = record.get("source_url")
        if not isinstance(url, str) or not url.startswith("https://"):
            raise ValueError("measurement source URL required")
        values.append(value)
        sources.append(url)
    count = len(values)
    deviation = stdev(values)
    return {"context": context, "count": count, "mean": mean(values),
            "sample_stdev": deviation,
            "standard_error": deviation / sqrt(count),
            "min": min(values), "max": max(values),
            "source_urls": sorted(set(sources)),
            "verified_in_game": False,
            "status": "reported_measurements_not_independently_verified"}
