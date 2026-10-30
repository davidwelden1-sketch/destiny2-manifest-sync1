"""Resolve named weapon perks to exact Bungie hashes before structural pair queries.

Bungie manifest item names are labels, not unique IDs. Only plug hashes found
on randomized sockets of exact weapon definitions are eligible for this query.
A hit is NOT evidence of a currently obtainable, enhanced, or playable roll.
Source: https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html
"""
import argparse
import json
from pathlib import Path

from scripts.query_weapon_pairs import find_pair_candidates


def _normalize_name(name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Perk name must be a nonempty string")
    return name.strip().casefold()


def resolve_names(index, items, names):
    """Return each requested name's exact matching randomized plug hashes.

    Duplicate display names are kept as distinct hashes. Missing names stay
    unresolved; we never silently fall back to fuzzy or partial matching.
    """
    requested = [_normalize_name(name) for name in names]
    eligible = set()
    for weapon in index:
        if weapon.get("item_type") != 3:
            continue
        for socket in weapon.get("sockets", []):
            for h in socket.get("randomized_candidate_plug_hashes", []):
                if type(h) is int and h > 0:
                    eligible.add(h)
    matches = {name: set() for name in requested}
    for item in items:
        if not isinstance(item, dict):
            continue
        h = item.get("hash")
        label = item.get("name")
        if type(h) is not int or h not in eligible or not isinstance(label, str):
            continue
        normalized = label.strip().casefold()
        if normalized in matches:
            matches[normalized].add(h)
    return {name: sorted(matches[name]) for name in requested}


def query_named_pairs(index, items, perk_a, perk_b,
                      current_roll_only=False, default_visible_only=False):
    """Conservatively query exact-hash, distinct-randomized-socket candidates."""
    a, b = _normalize_name(perk_a), _normalize_name(perk_b)
    if a == b:
        raise ValueError("Supply two different perk names")
    if type(current_roll_only) is not bool or type(default_visible_only) is not bool:
        raise ValueError("Filters must be boolean")
    resolved = resolve_names(index, items, (perk_a, perk_b))
    rows = []
    for ah in resolved[a]:
        for bh in resolved[b]:
            if ah == bh:
                continue
            for hit in find_pair_candidates(index, ah, bh,
                                            current_roll_only=current_roll_only,
                                            default_visible_only=default_visible_only):
                rows.append({"item_hash": hit["item_hash"],
                             "weapon_name": hit["name"],
                             "perk_a_hash": ah, "perk_b_hash": bh,
                             "socket_pairs": hit["socket_pairs"],
                             "evidence": hit["evidence"]})
    rows.sort(key=lambda r: (r["item_hash"], r["perk_a_hash"], r["perk_b_hash"]))
    return {
        "perk_a": perk_a, "perk_b": perk_b,
        "resolved_plug_hashes": {"a": resolved[a], "b": resolved[b]},
        "unresolved_names": [label for label, key in ((perk_a, a), (perk_b, b))
                             if not resolved[key]],
        "current_roll_only": current_roll_only,
        "default_visible_only": default_visible_only,
        "structural_pair_matches": rows,
        "roll_legality": "unverified",
        "enhanced_perk_legality": "unverified",
        "current_acquisition": "unverified",
        "gameplay_effect": "unverified",
        "interpretation": (
            "Exact-name, exact-plug-hash, distinct randomized socket membership "
            "within one weapon item hash only. A zero result is not proof of "
            "impossibility: historical, fixed, reusable, vendor, crafted and "
            "runtime states may differ. Manifest flags are not drop certification."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--perk-a", required=True)
    parser.add_argument("--perk-b", required=True)
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--currently-rollable-only", action="store_true")
    parser.add_argument("--default-visible-only", action="store_true")
    args = parser.parse_args()
    root = Path(args.output_dir)
    index = json.loads((root / "item_socket_candidates.json").read_text())
    items = json.loads((root / "items_extended.json").read_text())
    meta = json.loads((root / "manifest_metadata_extended.json").read_text())
    report = query_named_pairs(index, items, args.perk_a, args.perk_b,
                               args.currently_rollable_only, args.default_visible_only)
    report["manifest_version"] = meta["manifest_version"]
    report["retrieved_at_utc"] = meta.get("retrieved_at_utc")
    (root / "named_weapon_perk_pair_query.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "structural_pair_matches"},
                     indent=2, ensure_ascii=False))
    print("Structural exact-hash matches:", len(report["structural_pair_matches"]))


if __name__ == "__main__":
    main()
