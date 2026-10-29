"""Generate a conservative searchable index from extended manifest output.

A plug present in a reusable socket is NOT evidence that it can randomly roll.
Keep each socket's candidate sources separate so downstream pair queries can
require two distinct randomized sockets without inventing enhanced legality.
"""
import json
import os
from pathlib import Path


def classify_roll_flags(plugs, records):
    """Classify explicit Bungie flags; missing or conflicting entries are unknown."""
    current, noncurrent, unknown = set(), set(), set()
    for plug in plugs:
        statuses = set()
        for row in (records or []):
            if not isinstance(row, dict) or type(row.get("plugItemHash")) is not int:
                continue
            if row["plugItemHash"] == plug:
                status = row.get("currentlyCanRoll")
                # Malformed or missing statuses must contaminate confidence,
                # not be ignored beside an otherwise explicit True record.
                statuses.add(status if type(status) is bool else None)
        if statuses == {True}:
            current.add(plug)
        elif statuses == {False}:
            noncurrent.add(plug)
        else:
            unknown.add(plug)
    return current, noncurrent, unknown


def build_index(items, plugsets, roll_flags=None):
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
                                           if type(x) is int and x > 0)
            initial = socket.get("singleInitialItemHash")
            if initial is not None:
                sources.append({"field": "singleInitialItemHash", "hash": initial})
                if type(initial) is int and initial > 0:
                    by_source["singleInitialItemHash"] = {initial}
            randomized = by_source.get("randomizedPlugSetHash", set())
            randomized_set = socket.get("randomizedPlugSetHash")
            records = (roll_flags or {}).get(str(randomized_set))
            current, noncurrent, unknown = classify_roll_flags(randomized, records)
            candidates = set().union(*by_source.values()) if by_source else set()
            if candidates:
                sockets.append({
                    "socket_index": index,
                    "socket_type_hash": socket.get("socketTypeHash"),
                    # Definition visibility is only a default; live instance state can override it.
                    "default_visible": (socket.get("defaultVisible")
                                        if isinstance(socket.get("defaultVisible"), bool) else None),
                    "plug_sources": (socket.get("plugSources")
                                     if isinstance(socket.get("plugSources"), int)
                                     and not isinstance(socket.get("plugSources"), bool)
                                     and socket.get("plugSources") >= 0 else None),
                    "vendor_purchase_initialization_blocked": (
                        socket.get("preventInitializationOnVendorPurchase")
                        if isinstance(socket.get("preventInitializationOnVendorPurchase"), bool)
                        else None),
                    "candidate_plug_hashes": sorted(candidates),
                    "randomized_candidate_plug_hashes": sorted(randomized),
                    "currently_rollable_randomized_candidate_plug_hashes": sorted(current),
                    "noncurrent_randomized_candidate_plug_hashes": sorted(noncurrent),
                    "unknown_current_roll_randomized_candidate_plug_hashes": sorted(unknown),
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
    flags_path = output / "plugset_roll_flags.json"
    roll_flags = json.loads(flags_path.read_text()) if flags_path.is_file() else None
    rows = build_index(items, plugsets, roll_flags)
    (output / "item_socket_candidates.json").write_text(json.dumps(rows, separators=(",", ":")))
    print(f"Indexed {len(rows)} equippable items with source-separated sockets and explicit current-roll flags; acquisition/enhancement legality unverified")


if __name__ == "__main__":
    main()
