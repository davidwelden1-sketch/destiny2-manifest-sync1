"""Generate a conservative searchable index from extended manifest output."""
import json
import os
from pathlib import Path

def build_index(items, plugsets):
    result = []
    for item in items:
        if not item.get("equippable") or not item.get("name"):
            continue
        sockets = []
        for index, socket in enumerate(item.get("socketEntries", [])):
            candidates = set()
            sources = []
            for field in ("randomizedPlugSetHash", "reusablePlugSetHash"):
                h = socket.get(field)
                if h is not None:
                    sources.append({"field": field, "hash": h})
                    candidates.update(x for x in plugsets.get(str(h), []) if x is not None)
            initial = socket.get("singleInitialItemHash")
            if initial is not None:
                sources.append({"field": "singleInitialItemHash", "hash": initial})
                candidates.add(initial)
            if candidates:
                sockets.append({"socket_index": index, "candidate_plug_hashes": sorted(candidates),
                                "plugset_references": sources})
        if sockets:
            result.append({"item_hash": item["hash"], "name": item["name"],
                           "item_type": item.get("itemType"), "item_subtype": item.get("itemSubType"),
                           "sockets": sockets, "roll_legality": "unverified"})
    return sorted(result, key=lambda x: x["item_hash"])

def main():
    output = Path(os.environ.get("OUTPUT_DIR", "output"))
    items = json.loads((output / "items_extended.json").read_text())
    plugsets = json.loads((output / "plugsets.json").read_text())
    rows = build_index(items, plugsets)
    (output / "item_socket_candidates.json").write_text(json.dumps(rows, separators=(",", ":")))
    print(f"Indexed {len(rows)} equippable items with plug-set references; roll legality unverified")

if __name__ == "__main__":
    main()
