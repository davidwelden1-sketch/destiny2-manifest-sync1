"""Cross-index frame-labelled initial plugs against randomized weapon sockets.

Bungie's plug category identifier and singleInitialItemHash are definition
metadata. Reuse across exact hashes, weapon subtypes, or randomized sockets
signals classification ambiguity, NEVER an active intrinsic or obtainable roll.
"""
import json
import os
from collections import defaultdict
from pathlib import Path


def audit_frame_plug_reuse(items, index, version):
    by_hash = {row["hash"]: row for row in items
               if isinstance(row, dict) and type(row.get("hash")) is int
               and row["hash"] > 0}
    weapons = [row for row in items if isinstance(row, dict)
               and row.get("itemType") == 3 and row.get("equippable") is True
               and type(row.get("hash")) is int and row["hash"] > 0]
    occurrences = defaultdict(list)
    for weapon in weapons:
        for socket_index, socket in enumerate(weapon.get("socketEntries") or []):
            if not isinstance(socket, dict):
                continue
            plug_hash = socket.get("singleInitialItemHash")
            if type(plug_hash) is not int or plug_hash <= 0:
                continue
            plug = by_hash.get(plug_hash)
            if plug is None or plug.get("plugCategoryIdentifier") != "frames":
                continue
            occurrences[plug_hash].append({
                "item_hash": weapon["hash"],
                "weapon_name": weapon.get("name"),
                "item_subtype": weapon.get("itemSubType"),
                "socket_index": socket_index,
                "socket_type_hash": socket.get("socketTypeHash"),
            })
    randomized = defaultdict(set)
    for weapon in index:
        if not isinstance(weapon, dict) or weapon.get("item_type") != 3:
            continue
        item_hash = weapon.get("item_hash")
        if type(item_hash) is not int or item_hash <= 0:
            continue
        for socket in weapon.get("sockets") or []:
            if not isinstance(socket, dict):
                continue
            for plug_hash in socket.get("randomized_candidate_plug_hashes") or []:
                if type(plug_hash) is int and plug_hash > 0:
                    randomized[plug_hash].add((item_hash, socket.get("socket_index")))
    repeated_weapons = []
    multiple_subtypes = []
    randomized_overlap = []
    same_weapon_overlap = []
    for plug_hash, entries in sorted(occurrences.items()):
        weapon_hashes = {row["item_hash"] for row in entries}
        subtypes = {row["item_subtype"] for row in entries
                    if type(row["item_subtype"]) is int}
        if len(weapon_hashes) > 1:
            repeated_weapons.append(plug_hash)
        if len(subtypes) > 1:
            multiple_subtypes.append(plug_hash)
        memberships = randomized.get(plug_hash, set())
        if memberships:
            randomized_overlap.append(plug_hash)
            if any(item_hash in weapon_hashes for item_hash, _ in memberships):
                same_weapon_overlap.append(plug_hash)
    examples = []
    for plug_hash in sorted(occurrences):
        if (plug_hash in repeated_weapons or plug_hash in multiple_subtypes
                or plug_hash in randomized_overlap) and len(examples) < 30:
            examples.append({
                "plug_hash": plug_hash,
                "plug_name": by_hash[plug_hash].get("name"),
                "initial_weapon_hashes": sorted({r["item_hash"] for r in occurrences[plug_hash]}),
                "initial_weapon_subtypes": sorted({r["item_subtype"] for r in occurrences[plug_hash]
                                                  if type(r["item_subtype"]) is int}),
                "randomized_weapon_hashes": sorted({w for w, _ in randomized.get(plug_hash, set())}),
                "same_weapon_randomized_overlap": plug_hash in same_weapon_overlap,
                "active_frame_verified": False,
            })
    return {
        "manifest_version": version,
        "equippable_weapon_definitions": len(weapons),
        "unique_frames_labelled_initial_plug_hashes": len(occurrences),
        "initial_plug_hashes_reused_across_weapon_hashes": len(repeated_weapons),
        "initial_plug_hashes_spanning_weapon_subtypes": len(multiple_subtypes),
        "initial_plug_hashes_also_in_randomized_weapon_sockets": len(randomized_overlap),
        "initial_plug_hashes_randomized_on_same_weapon": len(same_weapon_overlap),
        "examples": examples,
        "active_frames_certified": 0,
        "limitations": ("Definition-level plug reuse and randomized membership only; "
                        "no active intrinsic, trait role, Champion behavior, acquisition, "
                        "enhancement, damage ownership, or runtime state certified."),
        "sources": [
            "https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html",
            "https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html",
        ],
    }


def main():
    root = Path(os.environ.get("OUTPUT_DIR", "output"))
    items = json.loads((root / "items_extended.json").read_text())
    index = json.loads((root / "item_socket_candidates.json").read_text())
    meta = json.loads((root / "manifest_metadata_extended.json").read_text())
    report = audit_frame_plug_reuse(items, index, meta["manifest_version"])
    (root / "frame_initial_plug_reuse_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
