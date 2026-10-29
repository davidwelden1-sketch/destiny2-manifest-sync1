"""Audit source completeness before treating randomized socket absence as evidence.

A missing DestinyPlugSetDefinition is different from a defined empty set.
This is a data-quality report, not a playable-roll legality certificate.
"""
import argparse
import json
from pathlib import Path

FIELDS = ("randomizedPlugSetHash", "reusablePlugSetHash")


def audit_references(items, plugsets):
    missing = []
    empty = []
    invalid = []
    references = 0
    for item in items:
        if item.get("itemType") != 3 or not item.get("equippable"):
            continue
        for socket_index, socket in enumerate(item.get("socketEntries") or []):
            for field in FIELDS:
                h = socket.get(field)
                if h is None:
                    continue
                references += 1
                key = str(h)
                detail = {"item_hash": item["hash"], "socket_index": socket_index,
                          "field": field, "plugset_hash": h}
                if key not in plugsets:
                    missing.append(detail)
                elif not isinstance(plugsets[key], list):
                    invalid.append({**detail, "reason": "not_a_list"})
                elif not plugsets[key]:
                    empty.append(detail)
                elif any(not isinstance(p, int) or isinstance(p, bool) or p <= 0
                         for p in plugsets[key]):
                    invalid.append({**detail, "reason": "invalid_plug_hash"})
    return {"scope": "equippable_weapon_definitions_only",
            "referenced_plugsets": references,
            "missing_reference_count": len(missing),
            "defined_empty_reference_count": len(empty),
            "invalid_reference_count": len(invalid),
            "missing_references": missing,
            "defined_empty_references": empty,
            "invalid_references": invalid,
            "interpretation": "Missing set definitions prevent exhaustive candidate claims; defined empty sets are distinct. Neither case certifies drop or enhancement legality."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--strict", action="store_true", help="Fail on missing or invalid plug-set references")
    args = parser.parse_args()
    root = Path(args.output_dir)
    items = json.loads((root / "items_extended.json").read_text())
    plugsets = json.loads((root / "plugsets.json").read_text())
    report = audit_references(items, plugsets)
    (root / "plugset_integrity_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if not k.endswith("_references")}, indent=2))
    if args.strict and (report["missing_reference_count"] or report["invalid_reference_count"]):
        raise SystemExit("Missing or malformed referenced plug-set definitions")


if __name__ == "__main__":
    main()
