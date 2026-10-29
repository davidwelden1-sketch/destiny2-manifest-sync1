"""Conservative role-evidence audit for game-wide randomized weapon sockets.

The category identifier is an official manifest label, NOT a certified live
socket role. Only explicit component labels are separated from unknown labels.
In particular 'frames' is intentionally unclassified: the name alone does not
prove that a plug is a frame rather than an active weapon trait.
"""
import json
import os
from collections import Counter
from pathlib import Path

# Exact identifiers observed in the 2026-10-29 manifest category audit.
EXPLICIT_COMPONENT_CATEGORIES = {
    "barrels": "barrel_label",
    "magazines": "magazine_label",
    "magazines_gl": "grenade_launcher_magazine_label",
    "tubes": "tube_label",
    "batteries": "battery_label",
    "v300.weapon.damage_type.energy": "elemental_damage_type_label",
}


def audit_roles(index, items, version):
    by_hash = {row["hash"]: row for row in items
               if type(row.get("hash")) is int and row["hash"] > 0}
    membership_labels = Counter()
    socket_states = Counter()
    unclassified_labels = Counter()
    examples = []
    for weapon in index:
        if weapon.get("item_type") != 3:
            continue
        for socket in weapon.get("sockets", []):
            hashes = socket.get("randomized_candidate_plug_hashes") or []
            if not hashes:
                continue
            labels = set()
            missing = False
            for h in hashes:
                plug = by_hash.get(h) if type(h) is int and h > 0 else None
                label = plug.get("plugCategoryIdentifier") if plug else None
                if not isinstance(label, str) or not label:
                    label = "<missing>"
                    missing = True
                labels.add(label)
                membership_labels[label] += 1
                if label not in EXPLICIT_COMPONENT_CATEGORIES:
                    unclassified_labels[label] += 1
            if missing:
                state = "unknown_missing_category"
            elif all(label in EXPLICIT_COMPONENT_CATEGORIES for label in labels):
                state = "explicit_component_labels_only"
            else:
                state = "unclassified_or_mixed_role"
            socket_states[state] += 1
            if len(examples) < 30 and (
                state != "explicit_component_labels_only" or len(labels) > 1
                or socket.get("default_visible") is False
            ):
                examples.append({
                    "item_hash": weapon.get("item_hash"),
                    "name": weapon.get("name"),
                    "socket_index": socket.get("socket_index"),
                    "socket_type_hash": socket.get("socket_type_hash"),
                    "category_identifiers": sorted(labels),
                    "role_evidence_state": state,
                    "default_visible": socket.get("default_visible"),
                })
    return {
        "manifest_version": version,
        "randomized_weapon_plug_memberships_by_identifier":
            dict(sorted(membership_labels.items())),
        "randomized_weapon_socket_role_evidence_counts":
            dict(sorted(socket_states.items())),
        "unclassified_memberships_by_identifier":
            dict(sorted(unclassified_labels.items())),
        "investigation_examples": examples,
        "explicit_component_identifiers": EXPLICIT_COMPONENT_CATEGORIES,
        "limitations": (
            "Category identifiers describe manifest plug categories, not active "
            "gameplay traits. Frames and all unlisted categories remain unclassified. "
            "Explicit component labels are not proof of live socket behavior; "
            "enhanced legality, acquisition, and damage remain unverified."
        ),
    }


def main():
    root = Path(os.environ.get("OUTPUT_DIR", "output"))
    index = json.loads((root / "item_socket_candidates.json").read_text())
    items = json.loads((root / "items_extended.json").read_text())
    meta = json.loads((root / "manifest_metadata_extended.json").read_text())
    report = audit_roles(index, items, meta["manifest_version"])
    (root / "weapon_socket_role_evidence.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "manifest_version": report["manifest_version"],
        "socket_states": report["randomized_weapon_socket_role_evidence_counts"],
        "unclassified_memberships_top": sorted(
            report["unclassified_memberships_by_identifier"].items(),
            key=lambda pair: -pair[1])[:12],
        "limitations": report["limitations"],
    }, indent=2))


if __name__ == "__main__":
    main()
