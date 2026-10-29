"""Audit fictitious perk pairings caused by merging same-name weapon variants.

Uses only randomized plug membership from Bungie item definitions. A "phantom"
pair exists in the name-merged socket union but in NO individual item hash.
This is a structural data-quality finding, not drop/enhancement certification.
"""
import argparse
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path


def socket_pools(item):
    pools = defaultdict(set)
    for socket in item.get("sockets", []):
        index = socket.get("socket_index")
        plugs = socket.get("randomized_candidate_plug_hashes") or []
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            raise ValueError("Invalid socket index")
        if any(not isinstance(h, int) or isinstance(h, bool) or h <= 0 for h in plugs):
            raise ValueError("Invalid randomized plug hash")
        pools[index].update(plugs)
    return pools


def distinct_socket_pairs(pools):
    result = set()
    for (_, a), (_, b) in combinations(sorted(pools.items()), 2):
        for x in a:
            for y in b:
                if x != y:
                    result.add((min(x, y), max(x, y)))
    return result


def audit_cross_variant_phantoms(index, manifest_version, sample_limit=5):
    if not isinstance(sample_limit, int) or isinstance(sample_limit, bool) or sample_limit < 0:
        raise ValueError("sample_limit must be nonnegative")
    groups = defaultdict(list)
    seen = set()
    for item in index:
        if item.get("item_type") != 3 or not isinstance(item.get("name"), str) or not item["name"].strip():
            continue
        h = item.get("item_hash")
        if not isinstance(h, int) or isinstance(h, bool) or h <= 0 or h in seen:
            raise ValueError("Duplicate or invalid weapon item hash")
        seen.add(h)
        groups[item["name"].strip().casefold()].append(item)
    rows = []
    for name, variants in sorted(groups.items()):
        if len(variants) < 2:
            continue
        merged = defaultdict(set)
        actually_possible = set()
        for variant in variants:
            pools = socket_pools(variant)
            actually_possible.update(distinct_socket_pairs(pools))
            for index, plugs in pools.items():
                merged[index].update(plugs)
        phantom = distinct_socket_pairs(merged) - actually_possible
        if phantom:
            rows.append({
                "name": name,
                "item_hashes": sorted(v["item_hash"] for v in variants),
                "phantom_pair_count": len(phantom),
                "example_phantom_plug_pairs": [list(p) for p in sorted(phantom)[:sample_limit]],
            })
    return {
        "manifest_version": manifest_version,
        "weapon_definitions_checked": len(seen),
        "same_name_variant_groups_checked": sum(len(v) > 1 for v in groups.values()),
        "groups_with_phantom_pairs": len(rows),
        "phantom_pair_occurrences_across_groups": sum(r["phantom_pair_count"] for r in rows),
        "groups": rows,
        "interpretation": "Name-merged randomized socket pools can imply pairs absent from every individual item hash. Counts are per name-group structural hash pairs, not playable rolls or unique perks; no acquisition/enhancement certification.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    root = Path(args.output_dir)
    index = json.loads((root / "item_socket_candidates.json").read_text())
    metadata = json.loads((root / "manifest_metadata_extended.json").read_text())
    report = audit_cross_variant_phantoms(index, metadata["manifest_version"])
    (root / "cross_variant_phantom_pairs.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "groups"}, indent=2))
    print("Example affected names:", [r["name"] for r in report["groups"][:12]])


if __name__ == "__main__":
    main()
