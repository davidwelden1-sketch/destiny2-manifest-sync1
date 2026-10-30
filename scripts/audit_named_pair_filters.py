"""Compare exact-hash named weapon pair evidence under conservative manifest filters.

The four screens are definition-level signals, NOT obtainable or enhanced rolls.
Keep variant hashes separate and never equate currentlyCanRoll or defaultVisible
with inventory, vendor availability, live socket state, or PvE/PvP damage.
"""
import argparse
import json
from pathlib import Path

from scripts.query_named_weapon_perks import query_named_pairs


FILTERS = (
    ("structural", False, False),
    ("explicit_current_flag", True, False),
    ("default_visible", False, True),
    ("both_filters", True, True),
)


def audit_named_pair_filters(index, items, perk_a, perk_b):
    reports = {
        key: query_named_pairs(index, items, perk_a, perk_b,
                               current_roll_only=current, default_visible_only=visible)
        for key, current, visible in FILTERS
    }
    baseline = reports["structural"]
    by_screen = {}
    for key, report in reports.items():
        by_screen[key] = {row["item_hash"]: row for row in
                          report["unique_weapon_definitions"]}
    # A filtered report must retain the same exact weapon+plug-pair identity.
    # Checking only weapon hashes can miss a swapped perk pair on one weapon.
    pair_keys = {}
    for key, report in reports.items():
        identities = [(r["item_hash"], r["perk_a_hash"], r["perk_b_hash"])
                      for r in report["structural_pair_matches"]]
        if len(identities) != len(set(identities)):
            raise ValueError(f"Duplicate exact weapon/plug pair in {key}")
        if len(identities) != report["structural_match_count"]:
            raise ValueError(f"Pair row count mismatch in {key}")
        if {identity[0] for identity in identities} != set(by_screen[key]):
            raise ValueError(f"Pair weapon hashes disagree with summaries in {key}")
        if sum(w["structural_pair_count"] for w in
               report["unique_weapon_definitions"]) != len(identities):
            raise ValueError(f"Per-weapon pair counts disagree in {key}")
        pair_keys[key] = set(identities)
    for key in ("explicit_current_flag", "default_visible", "both_filters"):
        if not pair_keys[key].issubset(pair_keys["structural"]):
            raise ValueError(f"Filtered plug pairs exceed structural baseline in {key}")
    if not pair_keys["both_filters"].issubset(
            pair_keys["explicit_current_flag"] & pair_keys["default_visible"]):
        raise ValueError("Combined filter contains pairs absent from an individual filter")
    base_hashes = set(by_screen["structural"])
    for key in ("explicit_current_flag", "default_visible", "both_filters"):
        if not set(by_screen[key]).issubset(base_hashes):
            raise ValueError("Filtered weapon hashes cannot exceed structural baseline")
    if not set(by_screen["both_filters"]).issubset(
            set(by_screen["explicit_current_flag"]) & set(by_screen["default_visible"])):
        raise ValueError("Combined filter must be a subset of each individual filter")

    per_weapon = []
    for h in sorted(base_hashes):
        base = by_screen["structural"][h]
        per_weapon.append({
            "item_hash": h,
            "weapon_name": base["weapon_name"],
            "structural_pair_count": base["structural_pair_count"],
            "explicit_current_flag_pair_count": by_screen["explicit_current_flag"].get(
                h, {}).get("structural_pair_count", 0),
            "default_visible_pair_count": by_screen["default_visible"].get(
                h, {}).get("structural_pair_count", 0),
            "both_filters_pair_count": by_screen["both_filters"].get(
                h, {}).get("structural_pair_count", 0),
            "role_screen_states": base["category_role_screens"],
            "roll_legality": "unverified",
            "enhanced_perk_legality": "unverified",
            "current_acquisition": "unverified",
        })
    counts = {
        key: {"structural_pair_rows": report["structural_match_count"],
              "unique_weapon_hashes": report["unique_weapon_definition_count"]}
        for key, report in reports.items()
    }
    return {
        "perk_a": perk_a,
        "perk_b": perk_b,
        "resolved_plug_hashes": baseline["resolved_plug_hashes"],
        "unresolved_names": baseline["unresolved_names"],
        "filter_counts": counts,
        "per_exact_weapon_hash": per_weapon,
        "explicit_current_flag_filter_reduced_rows": (
            counts["explicit_current_flag"]["structural_pair_rows"]
            < counts["structural"]["structural_pair_rows"]),
        "default_visibility_filter_reduced_rows": (
            counts["default_visible"]["structural_pair_rows"]
            < counts["structural"]["structural_pair_rows"]),
        "interpretation": (
            "The screens compare randomized socket memberships for the SAME exact "
            "weapon item hash. currentlyCanRoll=true is a manifest plug flag, "
            "not proof that the weapon can currently drop; defaultVisible=true "
            "is not proof of an active runtime socket. No screen certifies "
            "simultaneous obtainable rolls, enhanced perks, or gameplay damage. "
            "No reduction under a filter does not validate its selectivity."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--perk-a", required=True)
    parser.add_argument("--perk-b", required=True)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    root = Path(args.output_dir)
    index = json.loads((root / "item_socket_candidates.json").read_text())
    items = json.loads((root / "items_extended.json").read_text())
    meta = json.loads((root / "manifest_metadata_extended.json").read_text())
    report = audit_named_pair_filters(index, items, args.perk_a, args.perk_b)
    report["manifest_version"] = meta["manifest_version"]
    report["retrieved_at_utc"] = meta.get("retrieved_at_utc")
    (root / "named_weapon_pair_filter_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
