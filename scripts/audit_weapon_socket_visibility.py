"""Audit weapon randomized socket default-visibility exceptions.

This is definition metadata only. Hidden-by-default does not prove a socket is
unusable: an individual item's runtime sockets can override definition state.
"""
import json
import os
from pathlib import Path


def audit_visibility(index, manifest_version):
    exceptions = []
    counts = {"visible": 0, "hidden": 0, "unknown": 0}
    for item in index:
        if item.get("item_type") != 3:
            continue
        for socket in item.get("sockets", []):
            plugs = socket.get("randomized_candidate_plug_hashes") or []
            if not plugs:
                continue
            visibility = socket.get("default_visible")
            category = ("visible" if visibility is True else
                        "hidden" if visibility is False else "unknown")
            counts[category] += 1
            if category == "visible":
                continue
            exceptions.append({
                "item_hash": item.get("item_hash"),
                "item_name": item.get("name"),
                "socket_index": socket.get("socket_index"),
                "default_visible": visibility if type(visibility) is bool else None,
                "socket_type_hash": socket.get("socket_type_hash"),
                "plug_sources": socket.get("plug_sources"),
                "vendor_purchase_initialization_blocked":
                    socket.get("vendor_purchase_initialization_blocked"),
                "randomized_plug_count": len(plugs),
                "randomized_plug_hashes": sorted(plugs),
                "explicit_current_roll_count": len(
                    socket.get("currently_rollable_randomized_candidate_plug_hashes") or []),
                "randomized_plugset_hashes": sorted(
                    r["hash"] for r in socket.get("plugset_references", [])
                    if r.get("field") == "randomizedPlugSetHash"
                    and type(r.get("hash")) is int),
            })
    exceptions.sort(key=lambda x: (x["item_hash"], x["socket_index"]))
    return {
        "manifest_version": manifest_version,
        "randomized_weapon_socket_counts": counts,
        "exceptions": exceptions,
        "interpretation": (
            "Definition-level hidden or unknown default visibility only. "
            "Runtime item socket state, current acquisition and enhancement remain unverified."
        ),
    }


def main():
    root = Path(os.environ.get("OUTPUT_DIR", "output"))
    index = json.loads((root / "item_socket_candidates.json").read_text())
    meta = json.loads((root / "manifest_metadata_extended.json").read_text())
    report = audit_visibility(index, meta["manifest_version"])
    (root / "weapon_socket_visibility_exceptions.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
