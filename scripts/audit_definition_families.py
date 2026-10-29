"""Audit coverage of expected definition families after a sync."""
import json
import sys
from pathlib import Path

def audit(root):
    root = Path(root)
    catalog = json.loads((root / "definition_catalog.json").read_text())
    errors = []
    total = 0
    for family, metadata in catalog["families"].items():
        path = root / metadata["file"]
        if not path.is_file():
            errors.append(f"Missing output for {family}")
            continue
        rows = json.loads(path.read_text())
        if len(rows) != metadata["count"]:
            errors.append(f"Count mismatch for {family}")
        hashes = [row["hash"] for row in rows]
        if hashes != sorted(set(hashes)):
            errors.append(f"Duplicate or unsorted hashes for {family}")
        total += len(rows)
    return {"manifest_version": catalog["manifest_version"],
            "families": len(catalog["families"]), "definitions": total,
            "unavailable_families": catalog["unavailable_families"], "errors": errors}

if __name__ == "__main__":
    result = audit(sys.argv[1] if len(sys.argv) > 1 else "output")
    print(json.dumps(result, indent=2))
    if result["errors"]:
        raise SystemExit(1)
