"""Audit Bungie socket-type plug-category compatibility, not playable roll legality.

Bungie's DestinySocketTypeDefinition.plugWhitelist constrains plug categories.
An empty whitelist permits all categories. Missing metadata is UNKNOWN, never
silently compatible. Randomized plug-set membership is not live instance proof.
"""
import json
import os
from collections import Counter
from pathlib import Path


def audit_categories(index, items, socket_types, manifest_version):
    by_hash = {row["hash"]: row for row in items
               if type(row.get("hash")) is int and row["hash"] > 0}
    counts = Counter()
    categories = Counter()
    exceptions = []
    hidden_examples = []
    for weapon in index:
        if weapon.get("item_type") != 3:
            continue
        for socket in weapon.get("sockets", []):
            plugs = socket.get("randomized_candidate_plug_hashes") or []
            if not plugs:
                continue
            socket_hash = socket.get("socket_type_hash")
            definition = socket_types.get(str(socket_hash))
            whitelist = definition.get("plugWhitelist") if isinstance(definition, dict) else None
            if isinstance(whitelist, list):
                valid = all(isinstance(row, dict) and
                            type(row.get("categoryHash")) is int and
                            row["categoryHash"] > 0 for row in whitelist)
                allowed = {row["categoryHash"] for row in whitelist} if valid else None
            else:
                allowed = None
            for plug_hash in plugs:
                plug = by_hash.get(plug_hash)
                category = plug.get("plugCategoryHash") if plug else None
                identifier = plug.get("plugCategoryIdentifier") if plug else None
                if plug is None:
                    state = "missing_plug_definition"
                elif allowed is None:
                    state = "unknown_socket_type_or_whitelist"
                elif not allowed:
                    state = "compatible_empty_whitelist"
                elif type(category) is not int or category <= 0:
                    state = "unknown_plug_category"
                elif category in allowed:
                    state = "compatible_whitelist"
                else:
                    state = "category_not_whitelisted"
                counts[state] += 1
                if isinstance(identifier, str) and identifier:
                    categories[identifier] += 1
                detail = {"item_hash": weapon.get("item_hash"),
                          "name": weapon.get("name"),
                          "socket_index": socket.get("socket_index"),
                          "socket_type_hash": socket_hash,
                          "plug_hash": plug_hash,
                          "plug_name": plug.get("name") if plug else None,
                          "plug_category_hash": category,
                          "plug_category_identifier": identifier,
                          "classification": state}
                if state not in ("compatible_empty_whitelist", "compatible_whitelist") and len(exceptions) < 30:
                    exceptions.append(detail)
                if socket.get("default_visible") is False and len(hidden_examples) < 30:
                    hidden_examples.append(detail)
    return {
        "manifest_version": manifest_version,
        "weapon_randomized_plug_memberships_by_category_compatibility": dict(sorted(counts.items())),
        "top_plug_category_identifiers": [
            {"identifier": name, "memberships": n}
            for name, n in categories.most_common(40)],
        "noncompatible_or_unknown_examples": exceptions,
        "hidden_default_socket_examples": hidden_examples,
        "limitations": ("Socket whitelist compatibility is definition-level evidence only; "
                        "it does not establish trait role, current acquisition, simultaneous "
                        "equippability, enhanced legality, or runtime item state."),
    }


def main():
    root = Path(os.environ.get("OUTPUT_DIR", "output"))
    index = json.loads((root / "item_socket_candidates.json").read_text())
    items = json.loads((root / "items_extended.json").read_text())
    socket_types = json.loads((root / "socket_types.json").read_text())
    meta = json.loads((root / "manifest_metadata_extended.json").read_text())
    report = audit_categories(index, items, socket_types, meta["manifest_version"])
    (root / "weapon_socket_category_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
