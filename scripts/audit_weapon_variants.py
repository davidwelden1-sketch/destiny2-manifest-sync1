"""Game-wide same-name weapon variant audit using Bungie randomized sockets.

The manifest can contain multiple item hashes sharing a display name. Never
merge their perk pools: a variant can have a different trait-column signature.
This is structural evidence, not a proof of acquisition or enhancement.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path


def randomized_signature(item):
    """Hashable socket-index/type/plug-membership signature for a weapon."""
    return tuple(sorted(
        (socket["socket_index"], socket.get("socket_type_hash"),
         tuple(sorted(set(socket.get("randomized_candidate_plug_hashes") or []))))
        for socket in item.get("sockets", [])
        if socket.get("randomized_candidate_plug_hashes")
    ))


def audit_variants(index, manifest_version):
    groups = defaultdict(list)
    seen_hashes = set()
    for item in index:
        if item.get("item_type") != 3 or not isinstance(item.get("name"), str) or not item["name"].strip():
            continue
        h = item.get("item_hash")
        if not isinstance(h, int) or isinstance(h, bool) or h <= 0 or h in seen_hashes:
            raise ValueError("Invalid or duplicate weapon item hash")
        seen_hashes.add(h)
        groups[item["name"].strip().casefold()].append(item)
    variants = []
    for name, items in sorted(groups.items()):
        if len(items) < 2:
            continue
        signatures = {randomized_signature(item) for item in items}
        variants.append({
            "name": name,
            "item_hashes": sorted(item["item_hash"] for item in items),
            "distinct_randomized_signatures": len(signatures),
            "divergent_randomized_evidence": len(signatures) > 1,
            "contains_no_randomized_sockets": any(not randomized_signature(item) for item in items),
        })
    return {
        "manifest_version": manifest_version,
        "indexed_weapon_definitions": len(seen_hashes),
        "same_name_variant_groups": len(variants),
        "divergent_variant_groups": sum(v["divergent_randomized_evidence"] for v in variants),
        "identical_signature_variant_groups": sum(not v["divergent_randomized_evidence"] for v in variants),
        "groups": variants,
        "interpretation": "Same-name item hashes must retain independent randomized socket evidence. Identical signatures do not certify equivalent drops; divergent signatures do not certify active acquisition, selectable rolls or enhanced perk eligibility.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    root = Path(args.output_dir)
    index = json.loads((root / "item_socket_candidates.json").read_text())
    metadata = json.loads((root / "manifest_metadata_extended.json").read_text())
    report = audit_variants(index, metadata["manifest_version"])
    (root / "weapon_variant_catalog_audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({k: v for k, v in report.items() if k != "groups"}, indent=2))
    print("Divergent examples:", json.dumps([v for v in report["groups"] if v["divergent_randomized_evidence"]][:12]))


if __name__ == "__main__":
    main()
