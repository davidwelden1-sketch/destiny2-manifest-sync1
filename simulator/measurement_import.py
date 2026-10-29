"""Import documented gameplay observations from an exported CSV file.

Only measured rows with sufficient context are accepted. This tool never
scrapes protected sheets or treats community claims as independent verification.

Usage:
  python -m simulator.measurement_import measurements.csv
"""
import csv
import json
import sys
from collections import defaultdict
from datetime import date
from math import isfinite
from pathlib import Path
from urllib.parse import urlparse

from simulator.measurement_aggregation import summarize_measurements

REQUIRED = (
    "metric", "game_version", "activity", "scenario", "unit",
    "value", "source_url", "measured_on", "method", "sample_id",
)

def _validate_row(row):
    if any(not isinstance(row.get(k), str) or not row[k].strip() for k in REQUIRED):
        raise ValueError("missing measurement field")
    parsed = urlparse(row["source_url"])
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("invalid measurement source URL")
    date.fromisoformat(row["measured_on"])
    value = float(row["value"])
    if not isfinite(value):
        raise ValueError("nonfinite observation")
    return {**row, "value": value}

def import_measurements(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(REQUIRED).issubset(reader.fieldnames):
            raise ValueError("missing required CSV columns")
        rows = [_validate_row(row) for row in reader]
    if not rows:
        raise ValueError("empty measurement CSV")
    groups = defaultdict(list)
    for row in rows:
        key = tuple(row[k] for k in ("metric", "game_version", "activity", "scenario", "unit"))
        groups[key].append(row)
    reports = []
    for key, group in sorted(groups.items()):
        unique_ids = {row["sample_id"] for row in group}
        if len(unique_ids) != len(group):
            raise ValueError("duplicate sample ID in a measurement group")
        if len(group) < 3:
            reports.append({"context": dict(zip(("metric", "game_version", "activity", "scenario", "unit"), key)),
                            "count": len(group), "status": "insufficient_samples",
                            "verified_in_game": False})
        else:
            reports.append(summarize_measurements(group))
    return {"total_rows": len(rows), "groups": reports,
            "status": "unreviewed_import", "verified_in_game": False}

def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        raise SystemExit("usage: python -m simulator.measurement_import measurements.csv")
    print(json.dumps(import_measurements(Path(args[0])), indent=2))

if __name__ == "__main__":
    main()
