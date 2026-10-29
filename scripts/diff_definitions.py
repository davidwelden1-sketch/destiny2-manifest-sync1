"""Compare consecutive Bungie definition snapshots without inventing sandbox changes."""
import json
import sys
from pathlib import Path

def compare_snapshots(previous, current):
    old = {str(row["hash"]): row for row in previous}
    new = {str(row["hash"]): row for row in current}
    added = sorted(set(new) - set(old), key=int)
    removed = sorted(set(old) - set(new), key=int)
    changed = sorted((key for key in old.keys() & new.keys()
                      if old[key] != new[key]), key=int)
    return {"added_hashes": added, "removed_hashes": removed,
            "modified_hashes": changed, "added": len(added),
            "removed": len(removed), "modified": len(changed),
            "interpretation": "Definition changes only; gameplay changes require verification."}

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python scripts/diff_definitions.py previous.json current.json")
    previous = json.loads(Path(sys.argv[1]).read_text())
    current = json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(compare_snapshots(previous, current), indent=2))

if __name__ == "__main__":
    main()
