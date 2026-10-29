"""Query game-wide *structural* weapon perk-pair candidates from Bungie sockets.

This does not prove a drop, an enhanced version, simultaneous selectable traits,
or damage activation. It only checks distinct randomized socket memberships.
"""
import argparse
import json
import os
from pathlib import Path


def find_pair_candidates(index, plug_a, plug_b, current_roll_only=False):
    if not all(isinstance(h, int) and not isinstance(h, bool) and h > 0
               for h in (plug_a, plug_b)) or plug_a == plug_b:
        raise ValueError("Supply two distinct positive plug hashes")
    if not isinstance(current_roll_only, bool):
        raise ValueError("current_roll_only must be boolean")
    field = ("currently_rollable_randomized_candidate_plug_hashes" if current_roll_only
             else "randomized_candidate_plug_hashes")
    matches = []
    for item in index:
        if item.get("item_type") != 3:  # Destiny itemType 3 = Weapon
            continue
        sockets = item.get("sockets", [])
        a_sockets = [s for s in sockets if plug_a in s.get(field, [])]
        b_sockets = [s for s in sockets if plug_b in s.get(field, [])]
        pairs = []
        for a in a_sockets:
            for b in b_sockets:
                if a["socket_index"] == b["socket_index"]:
                    continue
                pairs.append({"a_socket_index": a["socket_index"], "b_socket_index": b["socket_index"],
                              "a_socket_type_hash": a.get("socket_type_hash"),
                              "b_socket_type_hash": b.get("socket_type_hash"),
                              "a_randomized_set_hashes": sorted(r["hash"] for r in a.get("plugset_references", [])
                                                                 if r["field"] == "randomizedPlugSetHash"),
                              "b_randomized_set_hashes": sorted(r["hash"] for r in b.get("plugset_references", [])
                                                                 if r["field"] == "randomizedPlugSetHash")})
        if pairs:
            matches.append({"item_hash": item["item_hash"], "name": item["name"],
                            "socket_pairs": sorted(pairs, key=lambda x: (x["a_socket_index"], x["b_socket_index"])),
                            "evidence": ("explicit_currentlyCanRoll_true_on_distinct_randomized_sockets"
                                         if current_roll_only else "distinct_randomized_socket_membership_only"),
                            "roll_legality": "unverified", "enhanced_perk_legality": "unverified",
                            "current_obtainability": "unverified"})
    return sorted(matches, key=lambda x: x["item_hash"])


def summarize(index, version):
    weapons = [x for x in index if x.get("item_type") == 3]
    randomized_sockets = [s for x in weapons for s in x.get("sockets", [])
                          if s.get("randomized_candidate_plug_hashes")]
    return {"manifest_version": version, "indexed_weapon_definitions": len(weapons),
            "weapon_definitions_with_two_or_more_randomized_sockets":
                sum(sum(bool(s.get("randomized_candidate_plug_hashes"))
                        for s in x.get("sockets", [])) >= 2 for x in weapons),
            "randomized_socket_entries": len(randomized_sockets),
            "currently_rollable_randomized_plug_memberships":
                sum(len(s.get("currently_rollable_randomized_candidate_plug_hashes", []))
                    for s in randomized_sockets),
            "noncurrent_randomized_plug_memberships":
                sum(len(s.get("noncurrent_randomized_candidate_plug_hashes", []))
                    for s in randomized_sockets),
            "unknown_current_roll_plug_memberships":
                sum(len(s.get("unknown_current_roll_randomized_candidate_plug_hashes", []))
                    for s in randomized_sockets),
            "interpretation": "Structural candidate counts, not unique playable weapons, trait columns, enhanced eligibility or obtainable rolls."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plug-a", type=int)
    parser.add_argument("--currently-rollable-only", action="store_true",
                        help="Require explicit Bungie currentlyCanRoll=true on both plugs")
    parser.add_argument("--plug-b", type=int)
    parser.add_argument("--output-dir", default=os.environ.get("OUTPUT_DIR", "output"))
    args = parser.parse_args()
    if (args.plug_a is None) != (args.plug_b is None):
        parser.error("--plug-a and --plug-b must be supplied together")
    root = Path(args.output_dir)
    index = json.loads((root / "item_socket_candidates.json").read_text())
    meta = json.loads((root / "manifest_metadata_extended.json").read_text())
    if args.plug_a is None:
        report = summarize(index, meta["manifest_version"])
        target = root / "weapon_randomized_socket_summary.json"
    else:
        report = {"manifest_version": meta["manifest_version"],
                  "plug_a": args.plug_a, "plug_b": args.plug_b,
                  "matches": find_pair_candidates(index, args.plug_a, args.plug_b,
                                                  current_roll_only=args.currently_rollable_only),
                  "current_roll_only": args.currently_rollable_only,
                  "interpretation": "Distinct randomized sockets only; not proof of a legal obtainable or enhanced roll."}
        suffix = "_currently_rollable" if args.currently_rollable_only else ""
        target = root / f"weapon_pair_{args.plug_a}_{args.plug_b}{suffix}.json"
    target.write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "matches"}, indent=2))
    if "matches" in report:
        print(f"Structural pair candidates: {len(report['matches'])}")


if __name__ == "__main__":
    main()
