"""Generate a conservative searchable index from extended manifest output.

A plug present in a reusable socket is NOT evidence that it can randomly roll.
Keep each socket's candidate sources separate so downstream pair queries can
require two distinct randomized sockets without inventing enhanced legality.
"""
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
            sources = []
            by_source = {}
            for field in ("randomizedPlugSetHash", "reusablePlugSetHash"):
                h = socket.get(field)
                if h is not None:
                    sources.append({"field": field, "hash": h})
                    by_source[field] = set(x for x in plugsets.get(str(h), [])
                                           if isinstance(x, int) and x > 0)
            initial = socket.get("singleInitialItemHash")
            if initial is not None:
                sources.append({"field": "singleInitialItemHash", "hash": initial})
                if isinstance(initial, int) and initial > 0:
                    by_source["singleInitialItemHash"] = {initial}
            candidates = set().union(*by_source.values()) if by_source else set()
            if candidates:
                sockets.append({
                    "socket_index": index,
                    "socket_type_hash": socket.get("socketTypeHash"),
                    "candidate_plug_hashes": sorted(candidates),
                    "randomized_candidate_plug_hashes": sorted(by_source.get("randomizedPlugSetHash", set())),
                    "reusable_candidate_plug_hashes": sorted(by_source.get("reusablePlugSetHash", set())),
                    "initial_candidate_plug_hashes": sorted(by_source.get("singleInitialItemHash", set())),
                    "plugset_references": sources,
                })
        if sockets:
            result.append({"item_hash": item["hash"], "name": item["name"],
                           "item_type": item.get("itemType"), "item_subtype": item.get("itemSubType"),
                           "sockets": sockets, "roll_legality": "unverified",
                           "enhanced_perk_legality": "unverified"})
    return sorted(result, key=lambda x: x["item_hash"])


def main():
    output = Path(os.environ.get("OUTPUT_DIR", "output"))
    items = json.loads((output / "items_extended.json").read_text())
    plugsets = json.loads((output / "plugsets.json").read_text())
    rows = build_index(items, plugsets)
    (output / "item_socket_candidates.json").write_text(json.dumps(rows, separators=(",", ":")))
    print(f"Indexed {len(rows)} equippable items with source-separated socket candidates; roll/enhancement legality unverified")


if __name__ == "__main__":
    main()
