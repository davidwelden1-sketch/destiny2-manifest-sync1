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
    # A single exact weapon hash can carry several initial plugs labelled
    # 'frames'. They may occupy different sockets and are NOT necessarily
    # mutually exclusive, or the active intrinsic frame.
    by_weapon = {}
    for candidate in candidates:
        by_weapon.setdefault(candidate["item_hash"], []).append(candidate)
    multi_frame = []
    for item_hash, entries in sorted(by_weapon.items()):
        if len(entries) < 2:
            continue
        multi_frame.append({
            "item_hash": item_hash,
            "weapon_name": entries[0].get("weapon_name"),
            "labelled_occurrences": len(entries),
            "distinct_initial_plug_hashes": len({
                row["initial_plug_hash"] for row in entries}),
            "socket_indexes": sorted({row["socket_index"] for row in entries}),
            "initial_plug_names": sorted({
                row["initial_plug_name"] for row in entries
                if isinstance(row["initial_plug_name"], str)}),
        })
    # Count paired initial-plug relationships without assigning active frame roles.
    # Socket indexes and socket type hashes remain definition-level evidence.
    socket_index_patterns = Counter()
    socket_type_relationships = Counter()
    plug_identity_relationships = Counter()
    socket_type_pairs = Counter()
    pair_examples = []
    for row in multi_frame:
        entries = by_weapon[row["item_hash"]]
        socket_index_patterns[",".join(str(x["socket_index"]) for x in entries)] += 1
        plug_identity_relationships[
            "same_initial_plug" if row["distinct_initial_plug_hashes"] == 1
            else "different_initial_plugs"] += 1
        types = [x["socket_type_hash"] for x in entries]
        if any(type(h) is not int or h <= 0 for h in types):
            relationship = "unknown_socket_type"
        elif len(set(types)) == 1:
            relationship = "same_socket_type"
        else:
            relationship = "different_socket_types"
        socket_type_relationships[relationship] += 1
        if relationship != "unknown_socket_type":
            socket_type_pairs[",".join(str(h) for h in sorted(types))] += 1
        if len(pair_examples) < 30:
            pair_examples.append({
                "item_hash": row["item_hash"],
                "weapon_name": row["weapon_name"],
                "socket_indexes": row["socket_indexes"],
                "socket_type_hashes": types,
                "initial_plug_hashes": [x["initial_plug_hash"] for x in entries],
                "socket_type_relationship": relationship,
                "active_frame_verified": False,
            })
    # Surface exact-hash exceptions to the dominant socket-type pattern.
    # A dominant pair is only selected when uniquely most frequent; ties
    # and absent/invalid type hashes must never imply a standard frame role.
    ranked_pairs = sorted(socket_type_pairs.items(),
                          key=lambda pair: (-pair[1], pair[0]))
    dominant_pair = (ranked_pairs[0][0] if ranked_pairs
                     and ranked_pairs[0][1] > 1
                     and (len(ranked_pairs) == 1
                          or ranked_pairs[0][1] > ranked_pairs[1][1])
                     else None)
    exceptional_rows = []
    for row in multi_frame:
        entries = by_weapon[row["item_hash"]]
        types = [entry["socket_type_hash"] for entry in entries]
        if any(type(h) is not int or h <= 0 for h in types):
            reason = "unknown_socket_type"
        elif dominant_pair is None:
            reason = "no_unique_dominant_pair"
        elif ",".join(str(h) for h in sorted(types)) != dominant_pair:
            reason = "non_dominant_socket_type_pair"
        else:
            continue
        exceptional_rows.append({
            "item_hash": row["item_hash"],
            "weapon_name": row["weapon_name"],
            "reason": reason,
            "socket_indexes": [entry["socket_index"] for entry in entries],
            "socket_type_hashes": types,
            "initial_plug_hashes": [entry["initial_plug_hash"] for entry in entries],
            "initial_plug_names": [entry["initial_plug_name"] for entry in entries],
            "active_frame_verified": False,
            "current_acquisition_verified": False,
        })
    exceptional_rows.sort(key=lambda row: row["item_hash"])
    return {
        "manifest_version": version,
        "equippable_weapon_definitions": len(weapons),
        "initial_plug_category_occurrences": dict(sorted(categories.items())),
        "frames_labelled_initial_plug_occurrences": len(candidates),
        "weapons_with_frames_labelled_initial_plug": len(
            {row["item_hash"] for row in candidates}),
        "weapons_with_multiple_frame_labelled_initial_plugs": len(multi_frame),
        "multi_frame_labelled_occurrences": sum(
            row["labelled_occurrences"] for row in multi_frame),
        "multi_frame_labelled_examples": multi_frame[:30],
        "multi_frame_socket_index_patterns": dict(sorted(socket_index_patterns.items())),
        "multi_frame_socket_type_relationships": dict(sorted(socket_type_relationships.items())),
        "multi_frame_plug_identity_relationships": dict(sorted(plug_identity_relationships.items())),
        "multi_frame_socket_type_pairs_top": sorted(socket_type_pairs.items(),
            key=lambda pair: (-pair[1], pair[0]))[:30],
        "multi_frame_relationship_examples": pair_examples,
        "multi_frame_dominant_socket_type_pair": dominant_pair,
        "multi_frame_exception_count": len(exceptional_rows),
        "multi_frame_exception_examples": exceptional_rows[:50],
        "unresolved_initial_plug_references": len(unresolved),
        "unresolved_initial_plug_examples": unresolved[:30],
        "frame_candidates": candidates,
        "limitations": (
            "An initial plug with category 'frames' is only a manifest candidate, "
            "not a certified active intrinsic/frame. Exact-hash live state, "
            "multiple frame-labelled plugs may be different socket roles; "
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
                                     "unresolved_initial_plug_examples",
                                     "multi_frame_labelled_examples",
                                     "multi_frame_relationship_examples")}, indent=2))


if __name__ == "__main__":
    main()
