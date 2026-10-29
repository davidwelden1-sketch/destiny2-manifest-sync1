"""Audit official manifest definition-family coverage without calling partial data complete.

A successful download of all *available* family files is not the same as
complete coverage of the expected family list. Missing Bungie content paths
are reported as an explicit partial-evidence blocker, not silently ignored.
"""
import json
import sys
from pathlib import Path


def audit(root):
    root = Path(root)
    catalog = json.loads((root / "definition_catalog.json").read_text())
    families = catalog.get("families", {})
    unavailable = catalog.get("unavailable_families", [])
    expected = catalog.get("expected_families")
    errors = []
    if not isinstance(families, dict) or not isinstance(unavailable, list):
        raise ValueError("Malformed definition catalog")
    if expected is None:  # backwards compatibility with older catalogs
        expected = sorted(set(families) | set(unavailable))
    if (not isinstance(expected, list) or not expected
            or any(not isinstance(x, str) or not x for x in expected)
            or len(expected) != len(set(expected))):
        errors.append("Expected family list is missing, empty, or duplicated")
        expected = []
    if any(not isinstance(x, str) or not x for x in unavailable) or len(unavailable) != len(set(unavailable)):
        errors.append("Unavailable family list is malformed or duplicated")
        unavailable = []
    available_set, unavailable_set, expected_set = set(families), set(unavailable), set(expected)
    if available_set & unavailable_set:
        errors.append("Family listed as both available and unavailable")
    if expected_set != available_set | unavailable_set:
        errors.append("Expected families do not match available plus unavailable families")
    if not families:
        errors.append("No downloaded definition families")
    total = 0
    for family, metadata in families.items():
        if not isinstance(metadata, dict) or not isinstance(metadata.get("file"), str):
            errors.append(f"Invalid metadata for {family}")
            continue
        # The downloader uses a fixed basename; do not follow arbitrary paths.
        filename = "definitions_" + family + ".json"
        if metadata["file"] != filename:
            errors.append(f"Unexpected output filename for {family}")
            continue
        path = root / filename
        if not path.is_file():
            errors.append(f"Missing output for {family}")
            continue
        try:
            rows = json.loads(path.read_text())
        except (ValueError, OSError):
            errors.append(f"Unreadable JSON for {family}")
            continue
        if not isinstance(rows, list):
            errors.append(f"Non-list definitions for {family}")
            continue
        if len(rows) != metadata.get("count"):
            errors.append(f"Count mismatch for {family}")
        hashes = [row.get("hash") if isinstance(row, dict) else None for row in rows]
        if (any(not isinstance(h, int) or isinstance(h, bool) or h < 0 for h in hashes)
                or hashes != sorted(set(hashes))):
            errors.append(f"Duplicate, invalid or unsorted hashes for {family}")
        total += len(rows)
    state = "invalid" if errors else "partial" if unavailable else "complete"
    return {
        "manifest_version": catalog.get("manifest_version"),
        "expected_families": len(expected),
        "families": len(families),
        "definitions": total,
        "unavailable_families": sorted(unavailable),
        "coverage_complete": state == "complete",
        "coverage_state": state,
        "interpretation": "Coverage of the explicitly requested family list only; not complete game data or measured gameplay.",
        "errors": errors,
    }


if __name__ == "__main__":
    result = audit(sys.argv[1] if len(sys.argv) > 1 else "output")
    print(json.dumps(result, indent=2))
    if result["errors"]:
        raise SystemExit(1)
