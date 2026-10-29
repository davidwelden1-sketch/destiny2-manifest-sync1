"""Audit initial-plug frame *candidates* for every exact-hash weapon.

Bungie singleInitialItemHash identifies an initially inserted plug, not
necessarily the active frame. The 'frames' plugCategoryIdentifier is a
debug/category label and MUST NOT certify an intrinsic Champion frame.
This report is manifest evidence only, never live-instance or roll legality.
"""
import json
import os
from collections import Counter
from pathlib import Path


def audit_initial_frame_candidates(items, version):
    """Return source-labelled frame candidates; fail closed on unknown plugs."""
    by_hash = {item["hash"]: item for item in items
               if isinstance(item, dict)
               and type(item.get("hash")) is int and item["hash"] > 0}
    weapons = [item for item in items
               if isinstance(item, dict) and item.get("itemType") == 3
               and item.get("equippable") is True
               and type(item.get("hash")) is int and item["hash"] > 0]
    candidates = []
    categories = Counter()
    unresolved = []
    for weapon in sorted(weapons, key=lambda row: row["hash"]):
        for index, socket in enumerate(weapon.get("socketEntries") or []):
            if not isinstance(socket, dict):
                continue
            plug_hash = socket.get("singleInitialItemHash")
            if type(plug_hash) is not int or plug_hash <= 0:
                continue
            plug = by_hash.get(plug_hash)
            if plug is None:
                unresolved.append({"item_hash": weapon["hash"],
                                   "socket_index": index,
                                   "initial_plug_hash": plug_hash})
                continue
            category = plug.get("plugCategoryIdentifier")
            category = category if isinstance(category, str) and category else "<missing>"
            categories[category] += 1
            if category != "frames":
                continue
            candidates.append({
                "item_hash": weapon["hash"],
                "weapon_name": weapon.get("name"),
                "weapon_item_subtype": weapon.get("itemSubType"),
                "socket_index": index,
                "socket_type_hash": socket.get("socketTypeHash"),
                "initial_plug_hash": plug_hash,
                "initial_plug_name": plug.get("name"),
                "initial_plug_category": category,
                "default_visible": socket.get("defaultVisible")
                    if type(socket.get("defaultVisible")) is bool else None,
                "evidence": "manifest_initial_plug_frames_category_only",
                "active_frame_verified": False,
                "champion_effect_verified": False,
                "runtime_socket_state": "unverified",
            })
    return {
        "manifest_version": version,
        "equippable_weapon_definitions": len(weapons),
        "initial_plug_category_occurrences": dict(sorted(categories.items())),
        "frames_labelled_initial_plug_occurrences": len(candidates),
        "weapons_with_frames_labelled_initial_plug": len(
            {row["item_hash"] for row in candidates}),
        "unresolved_initial_plug_references": len(unresolved),
        "unresolved_initial_plug_examples": unresolved[:30],
        "frame_candidates": candidates,
        "limitations": (
            "An initial plug with category 'frames' is only a manifest candidate, "
            "not a certified active intrinsic/frame. Exact-hash live state, "
            "frame-specific weapon type, Champion behavior, acquisition, "
            "enhancement and damage remain unverified."
        ),
        "sources": [
            "https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html",
            "https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html",
        ],
    }


def main():
    root = Path(os.environ.get("OUTPUT_DIR", "output"))
    items = json.loads((root / "items_extended.json").read_text())
    metadata = json.loads((root / "manifest_metadata_extended.json").read_text())
    report = audit_initial_frame_candidates(items, metadata["manifest_version"])
    (root / "weapon_initial_frame_candidates.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items()
                      if key not in ("frame_candidates", "initial_plug_category_occurrences",
                                     "unresolved_initial_plug_examples")}, indent=2))


if __name__ == "__main__":
    main()
