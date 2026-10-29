"""Create a compact name/hash lookup across exported definition families."""
import json
import sys
from pathlib import Path

def build_lookup(catalog, root):
    rows = []
    for family, info in sorted(catalog["families"].items()):
        for item in json.loads((Path(root) / info["file"]).read_text()):
            if not item.get("name"):
                continue
            rows.append({"family": family, "hash": item["hash"],
                         "name": item["name"], "description": item.get("description", "")})
    return sorted(rows, key=lambda r: (r["name"].casefold(), r["family"], r["hash"]))

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "output")
    catalog = json.loads((root / "definition_catalog.json").read_text())
    rows = build_lookup(catalog, root)
    (root / "definition_lookup.json").write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")))
    print(f"Indexed {len(rows)} named definitions from {len(catalog['families'])} families")

if __name__ == "__main__":
    main()
