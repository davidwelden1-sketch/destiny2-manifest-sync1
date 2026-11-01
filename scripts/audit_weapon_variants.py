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
    """Validate one exact weapon's socket identity before comparing variants.

    A corrupt or duplicated socket index must not be silently collapsed into
    an apparently identical signature. This is structural evidence only.
    """
    sockets = item.get("sockets", [])
    if not isinstance(sockets, (list, tuple)):
        raise ValueError("Weapon sockets must be a sequence")
    seen_indices = set()
    signature = []
    for socket in sockets:
        if not isinstance(socket, dict):
            raise ValueError("Malformed socket row")
        index = socket.get("socket_index")
        if type(index) is not int or index < 0 or index in seen_indices:
            raise ValueError("Invalid or duplicate socket index")
        seen_indices.add(index)
        plugs = socket.get("randomized_candidate_plug_hashes", [])
        if not isinstance(plugs, (list, tuple)) or any(
                type(h) is not int or h <= 0 for h in plugs):
            raise ValueError("Malformed randomized plug membership")
        if plugs:
            socket_type = socket.get("socket_type_hash")
            if socket_type is not None and (
                    type(socket_type) is not int or socket_type <= 0):
                raise ValueError("Invalid randomized socket type")
            # Preserve legacy normalization of duplicate plugs within a
            # socket; cross-socket duplication is always an identity error.
            signature.append((index, socket_type, tuple(sorted(set(plugs)))))
    return tuple(sorted(signature))

def audit_variants(index, manifest_version):
    if not isinstance(index, (list, tuple)):
        raise ValueError("Weapon index must be a sequence")
    groups = defaultdict(list)
    seen_hashes = set()
    for item in index:
        if not isinstance(item, dict):
            raise ValueError("Malformed item row")
        if item.get("item_type") != 3 or not isinstance(item.get("name"), str) or not item["name"].strip():
            continue
        # Validate every named weapon, including singleton names. Previously
        # only multi-hash name groups were checked, allowing malformed
        # singleton socket definitions to evade the game-wide audit.
        randomized_signature(item)
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
