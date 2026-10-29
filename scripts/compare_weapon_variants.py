"""Compare same-name weapon hashes using official randomized socket evidence.

Version/variant differences are structural only. Identical socket membership
never certifies that both items drop, enhance, or share activity eligibility.
"""
import argparse
import json
import os
import re
from itertools import combinations
from pathlib import Path


def compare_named_variants(index, name, plug_names=None):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("A nonempty weapon name is required")
    matches = sorted((x for x in index if x.get("item_type") == 3
                      and x.get("name", "").strip().casefold() == name.strip().casefold()),
                     key=lambda x: x["item_hash"])
    if len({x["item_hash"] for x in matches}) != len(matches):
        raise ValueError("Duplicate weapon hash in source index")
    names = plug_names or {}

    def sockets(item):
        return {s["socket_index"]: (s.get("socket_type_hash"),
                set(s.get("randomized_candidate_plug_hashes", [])))
                for s in item.get("sockets", []) if s.get("randomized_candidate_plug_hashes")}

    def annotate(hashes):
        return [{"plug_hash": h, "name": names.get(h)} for h in sorted(hashes)]

    comparisons = []
    for left, right in combinations(matches, 2):
        ls, rs = sockets(left), sockets(right)
        changes = []
        for i in sorted(ls.keys() | rs.keys()):
            lt, lp = ls.get(i, (None, set()))
            rt, rp = rs.get(i, (None, set()))
            if lt != rt or lp != rp:
                changes.append({"socket_index": i, "left_socket_type_hash": lt,
                                "right_socket_type_hash": rt,
                                "left_only": annotate(lp - rp), "right_only": annotate(rp - lp)})
        comparisons.append({"left_item_hash": left["item_hash"],
                            "right_item_hash": right["item_hash"],
                            "identical_randomized_socket_evidence": not changes,
                            "changed_sockets": changes})
    return {"name": name.strip(), "variant_hashes": [x["item_hash"] for x in matches],
            "comparisons": comparisons,
            "interpretation": "Bungie randomized socket membership only; plug names do not certify enhancement, selectable rolls, current drops or ownership of damage effects."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--output-dir", default=os.environ.get("OUTPUT_DIR", "output"))
    args = parser.parse_args()
    root = Path(args.output_dir)
    index = json.loads((root / "item_socket_candidates.json").read_text())
    items = json.loads((root / "items_extended.json").read_text())
    meta = json.loads((root / "manifest_metadata_extended.json").read_text())
    result = compare_named_variants(index, args.name, {x["hash"]: x["name"] for x in items})
    result["manifest_version"] = meta["manifest_version"]
    slug = re.sub(r"[^a-z0-9]+", "-", args.name.casefold()).strip("-")
    path = root / f"weapon_variants_{slug}.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps({"name": result["name"], "variant_hashes": result["variant_hashes"],
                      "different_variant_pairs": sum(not x["identical_randomized_socket_evidence"]
                                                     for x in result["comparisons"]),
                      "report": str(path)}, indent=2))


if __name__ == "__main__":
    main()
