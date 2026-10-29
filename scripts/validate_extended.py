#!/usr/bin/env python3
"""Validate manifest relationships without asserting current roll obtainability."""
import json
import os
from pathlib import Path

root = Path(os.environ.get("OUTPUT_DIR", "output"))
items = json.loads((root / "items_extended.json").read_text(encoding="utf-8"))
plugsets = json.loads((root / "plugsets.json").read_text(encoding="utf-8"))
meta = json.loads((root / "manifest_metadata_extended.json").read_text(encoding="utf-8"))
assert meta.get("manifest_version"), "Missing manifest version"
assert len(items) > 10000, "Unexpectedly small inventory definition"
assert len(plugsets) > 1000, "Unexpectedly small plug-set definition"
hashes = [row["hash"] for row in items]
assert len(hashes) == len(set(hashes)), "Duplicate item hashes"
assert all(isinstance(row["socketEntries"], list) for row in items)
lookup = {row["hash"]: row for row in items}
edges = []
missing_sets = set()
for row in items:
    for index, socket in enumerate(row["socketEntries"]):
        for field in ("randomizedPlugSetHash", "reusablePlugSetHash"):
            h = socket.get(field)
            if h is None:
                continue
            plugs = plugsets.get(str(h))
            if plugs is None:
                missing_sets.add(h)
                continue
            for plug in plugs:
                edges.append({"itemHash": row["hash"], "socketIndex": index,
                              "plugSetHash": h, "plugHash": plug,
                              "relationship": field,
                              "plugDefinedInInventory": plug in lookup})
edges.sort(key=lambda e: (e["itemHash"], e["socketIndex"], e["plugSetHash"], e["plugHash"] or 0))
(root / "item_plug_edges.json").write_text(json.dumps(edges, separators=(",", ":")), encoding="utf-8")
report = {
    "manifest_version": meta["manifest_version"],
    "item_count": len(items),
    "plugset_count": len(plugsets),
    "item_plug_edges": len(edges),
    "unresolved_plugset_hashes": sorted(missing_sets),
    "undefined_plug_references": sum(not edge["plugDefinedInInventory"] for edge in edges),
    "interpretation": "Socket/plug-set structural references only; not proof of live availability, random-roll legality, or enhanced-perk equivalence."
}
(root / "validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if k != "unresolved_plugset_hashes"}, indent=2))
if missing_sets:
    raise RuntimeError(f"Unresolved plug-set references: {len(missing_sets)}")

if __name__ == "__main__":
    main()
