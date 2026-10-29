"""Audit catalog coverage without assuming all Bungie definition families are present."""
import json
import sys
from pathlib import Path

def summarize(root):
    root = Path(root)
    files = ("manifest_metadata_extended.json", "definition_catalog.json")
    result = {"catalogs": {}, "missing_catalogs": []}
    for filename in files:
        path = root / filename
        if not path.exists():
            result["missing_catalogs"].append(filename)
            continue
        data = json.loads(path.read_text())
        result["catalogs"][filename] = {
            "manifest_version": data.get("manifest_version"),
            "source_families": sorted(data.get("sources", data.get("families", {}))),
            "unavailable_families": data.get("unavailable_families", []),
        }
    versions = {x["manifest_version"] for x in result["catalogs"].values()
                if x["manifest_version"]}
    result["consistent_manifest_version"] = len(versions) <= 1
    return result

if __name__ == "__main__":
    report = summarize(sys.argv[1] if len(sys.argv) > 1 else "output")
    print(json.dumps(report, indent=2))
    if not report["consistent_manifest_version"]:
        raise SystemExit("Manifest versions differ across catalogs")
