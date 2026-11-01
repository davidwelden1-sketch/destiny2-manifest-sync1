"""Query game-wide *structural* weapon perk-pair candidates from Bungie sockets.

This does not prove a drop, an enhanced version, simultaneous selectable traits,
or damage activation. It only checks distinct randomized socket memberships.
"""
import argparse
import json
import os
from pathlib import Path


def find_pair_candidates(index, plug_a, plug_b, current_roll_only=False,
                         default_visible_only=False):
    if not all(isinstance(h, int) and not isinstance(h, bool) and h > 0
               for h in (plug_a, plug_b)) or plug_a == plug_b:
        raise ValueError("Supply two distinct positive plug hashes")
    if not isinstance(current_roll_only, bool) or not isinstance(default_visible_only, bool):
        raise ValueError("Roll and visibility filters must be boolean")
    field = ("currently_rollable_randomized_candidate_plug_hashes" if current_roll_only
             else "randomized_candidate_plug_hashes")
    if not isinstance(index, (list, tuple)):
        raise ValueError("weapon index must be a list of item definitions")
    # A repeated item hash is an integrity conflict, not an extra weapon.
    # Reject ALL copies of conflicting identities rather than joining them.
    counts = {}
    for item in index:
        if isinstance(item, dict) and type(item.get("item_hash")) is int and item["item_hash"] > 0:
            counts[item["item_hash"]] = counts.get(item["item_hash"], 0) + 1
    matches = []
    for item in index:
        if not isinstance(item, dict) or item.get("item_type") != 3:
            continue
        if type(item.get("item_hash")) is not int or item["item_hash"] <= 0:
            continue
        if counts[item["item_hash"]] != 1 or not isinstance(item.get("sockets"), (list, tuple)):
            continue
        # Each Bungie socket index identifies one socket on this exact item.
        # Duplicate indices in a malformed extraction can mix incompatible
        # definitions and fabricate cross-column combinations. Fail closed
        # for the whole weapon, not merely the duplicate entry.
        # A non-dict socket row is corrupt evidence, even if other rows
        # appear to form a valid pair. Do not silently omit the bad row.
        if any(not isinstance(s, dict) for s in item["sockets"]):
            continue
        raw_indices = [s.get("socket_index") for s in item["sockets"]]
        if any(type(i) is not int or i < 0 for i in raw_indices):
            continue
        if len(raw_indices) != len(set(raw_indices)):
            continue
        # Fail closed on malformed manifest-derived sockets. In Python,
        # True == 1 and False == 0: a boolean candidate could otherwise
        # masquerade as a valid exact plug hash in a game-wide pair query.
        # Reject the *whole* malformed socket, not just its bad element.
        sockets = []
        malformed_socket = False
        for s in item["sockets"]:
            # Never silently discard a corrupt *dictionary* socket while
            # accepting a pair from its siblings. That would misrepresent
            # the integrity of the exact item definition.
            plugs = s.get(field, [])
            if (not isinstance(plugs, (list, tuple, set, frozenset))
                    or any(type(h) is not int or h <= 0 for h in plugs)):
                malformed_socket = True
                break
            refs = s.get("plugset_references", [])
            if not isinstance(refs, (list, tuple)) or any(
                not isinstance(ref, dict)
                or ref.get("field") not in ("randomizedPlugSetHash", "reusablePlugSetHash", "singleInitialItemHash")
                or type(ref.get("hash")) is not int or ref["hash"] <= 0
                for ref in refs
            ):
                malformed_socket = True
                break
            if default_visible_only and s.get("default_visible") is not True:
                continue
            sockets.append(s)
        if malformed_socket:
            continue
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
                              "a_default_visible": a.get("default_visible"),
                              "b_default_visible": b.get("default_visible"),
                              "a_plug_sources": a.get("plug_sources"),
                              "b_plug_sources": b.get("plug_sources"),
                              "a_vendor_purchase_initialization_blocked": a.get("vendor_purchase_initialization_blocked"),
                              "b_vendor_purchase_initialization_blocked": b.get("vendor_purchase_initialization_blocked"),
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
                            "current_obtainability": "unverified",
                            "runtime_socket_state": "unverified",
                            "default_visible_only": default_visible_only})
    return sorted(matches, key=lambda x: x["item_hash"])


def summarize(index, version):
    weapons = [x for x in index if x.get("item_type") == 3]
    randomized_sockets = [s for x in weapons for s in x.get("sockets", [])
                          if s.get("randomized_candidate_plug_hashes")]
    noncurrent_count = sum(len(s.get("noncurrent_randomized_candidate_plug_hashes", []))
                           for s in randomized_sockets)
    unknown_count = sum(len(s.get("unknown_current_roll_randomized_candidate_plug_hashes", []))
                        for s in randomized_sockets)
    visible = sum(s.get("default_visible") is True for s in randomized_sockets)
    hidden = sum(s.get("default_visible") is False for s in randomized_sockets)
    unknown_visibility = len(randomized_sockets) - visible - hidden
    return {"manifest_version": version, "indexed_weapon_definitions": len(weapons),
            "randomized_socket_default_visibility": {
                "true": visible, "false": hidden, "unknown": unknown_visibility},
            "weapon_definitions_with_two_or_more_randomized_sockets":
                sum(sum(bool(s.get("randomized_candidate_plug_hashes"))
                        for s in x.get("sockets", [])) >= 2 for x in weapons),
            "randomized_socket_entries": len(randomized_sockets),
            "currently_rollable_randomized_plug_memberships":
                sum(len(s.get("currently_rollable_randomized_candidate_plug_hashes", []))
                    for s in randomized_sockets),
            "noncurrent_randomized_plug_memberships": noncurrent_count,
            "unknown_current_roll_plug_memberships": unknown_count,
            "explicit_noncurrent_roll_evidence_found": noncurrent_count > 0,
            "roll_flag_caveat": (
                "No explicit currentlyCanRoll=false memberships found in indexed weapon sockets; "
                "the flag cannot distinguish retired rolls in this snapshot."
                if noncurrent_count == 0 and unknown_count == 0 else
                "Current-roll flags are evidence for a version, not proof of acquisition or enhancement."
            ),
            "interpretation": "Structural candidate counts, not unique playable weapons, trait columns, enhanced eligibility or obtainable rolls."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plug-a", type=int)
    parser.add_argument("--currently-rollable-only", action="store_true",
                        help="Require explicit Bungie currentlyCanRoll=true on both plugs")
    parser.add_argument("--default-visible-only", action="store_true",
                        help="Require both randomized sockets to be explicitly defaultVisible=true; runtime may differ")
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
                                                  current_roll_only=args.currently_rollable_only,
                                                  default_visible_only=args.default_visible_only),
                  "current_roll_only": args.currently_rollable_only,
                  "default_visible_only": args.default_visible_only,
                  "interpretation": "Distinct randomized sockets only; not proof of a legal obtainable or enhanced roll."}
        suffix = ("_currently_rollable" if args.currently_rollable_only else "")
        suffix += "_default_visible" if args.default_visible_only else ""
        target = root / f"weapon_pair_{args.plug_a}_{args.plug_b}{suffix}.json"
    target.write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "matches"}, indent=2))
    if "matches" in report:
        print(f"Structural pair candidates: {len(report['matches'])}")


if __name__ == "__main__":
    main()
