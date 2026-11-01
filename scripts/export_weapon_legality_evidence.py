"""Export app-ready exact-item-hash structural weapon evidence.

Reads the already indexed Bungie manifest. This is not an acquisition service:
randomized plug membership, even with currentlyCanRoll=True, does not establish
a legal live roll, enhanced trait, crafted variant, or damage value.
"""
import json
from datetime import datetime
from pathlib import Path
import argparse


def _hashes(values, field):
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"{field} must be a sequence")
    if any(type(h) is not int or h <= 0 for h in values):
        raise ValueError(f"{field} contains an invalid plug hash")
    if len(set(values)) != len(values):
        raise ValueError(f"{field} contains duplicate plug hashes")
    return set(values)


def export_weapon_evidence(index, metadata):
    """Build versioned evidence without ever joining weapon names."""
    if not isinstance(index, list) or not isinstance(metadata, dict):
        raise ValueError("Index and metadata must be structured")
    version = metadata.get("manifest_version")
    retrieved = metadata.get("retrieved_at_utc")
    sources = metadata.get("sources")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Missing manifest version")
    if not isinstance(retrieved, str):
        raise ValueError("Missing retrieval timestamp")
    try:
        timestamp = datetime.fromisoformat(retrieved.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid retrieval timestamp") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset().total_seconds() != 0:
        raise ValueError("Retrieval timestamp must be UTC")
    item_source = sources.get("DestinyInventoryItemDefinition") if isinstance(sources, dict) else None
    plug_source = sources.get("DestinyPlugSetDefinition") if isinstance(sources, dict) else None
    for source in (item_source, plug_source):
        if not isinstance(source, dict) or not isinstance(source.get("url"), str) or not source["url"].startswith("https://"):
            raise ValueError("Missing official component source URL")
        digest = source.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Missing official component SHA-256")
    seen_items = set()
    records = []
    for item in index:
        if not isinstance(item, dict):
            raise ValueError("Malformed item row")
        if item.get("item_type") != 3:
            continue
        item_hash = item.get("item_hash")
        if type(item_hash) is not int or item_hash <= 0 or item_hash in seen_items:
            raise ValueError("Invalid or duplicated exact weapon hash")
        seen_items.add(item_hash)
        if not isinstance(item.get("name"), str) or not item["name"].strip():
            raise ValueError("Missing weapon label")
        sockets = item.get("sockets")
        if not isinstance(sockets, list):
            raise ValueError("Missing weapon socket evidence")
        seen_sockets = set()
        exported_sockets = []
        for socket in sockets:
            if not isinstance(socket, dict):
                raise ValueError("Malformed socket")
            slot = socket.get("socket_index")
            if type(slot) is not int or slot < 0 or slot in seen_sockets:
                raise ValueError("Invalid or duplicate socket index")
            seen_sockets.add(slot)
            randomized = _hashes(socket.get("randomized_candidate_plug_hashes"), "randomized")
            current = _hashes(socket.get("currently_rollable_randomized_candidate_plug_hashes"), "current")
            retired = _hashes(socket.get("noncurrent_randomized_candidate_plug_hashes"), "noncurrent")
            unknown = _hashes(socket.get("unknown_current_roll_randomized_candidate_plug_hashes"), "unknown")
            if current & retired or current & unknown or retired & unknown or randomized != current | retired | unknown:
                raise ValueError("Contradictory or incomplete randomized roll-state partition")
            references = socket.get("plugset_references")
            if not isinstance(references, list):
                raise ValueError("Missing socket provenance")
            randomized_refs = [r for r in references if isinstance(r, dict) and r.get("field") == "randomizedPlugSetHash"]
            if randomized and (len(randomized_refs) != 1 or
                               type(randomized_refs[0].get("hash")) is not int or randomized_refs[0]["hash"] <= 0):
                raise ValueError("Randomized plugs lack exact plug-set provenance")
            exported_sockets.append({
                "socket_index": slot,
                "randomized_plug_hashes": sorted(randomized),
                "explicit_current_flag_plug_hashes": sorted(current),
                "explicit_noncurrent_flag_plug_hashes": sorted(retired),
                "unknown_current_flag_plug_hashes": sorted(unknown),
                "randomized_plug_set_hash": randomized_refs[0]["hash"] if randomized_refs else None,
                "trait_role_certified": False,
                "obtainable_roll_certified": False,
                "enhanced_trait_certified": False,
            })
        records.append({
            "id": f"d2:weapon:{item_hash}",
            "item_hash": item_hash,
            "display_name": item["name"],
            "item_subtype": item.get("item_subtype"),
            "sockets": sorted(exported_sockets, key=lambda s: s["socket_index"]),
            "confidence_grade": "official_manifest_structural_only",
            "current_acquisition": "unverified",
            "enhanced_perk_legality": "unverified",
            "pve_damage_measurement": None,
            "pvp_damage_measurement": None,
        })
    return {
        "schema_version": "1.0.0",
        "dataset_id": "vaeltrion:weapon-structural-evidence",
        "manifest_version": version,
        "retrieved_at_utc": retrieved,
        "provenance": {
            "publisher": "Bungie",
            "inventory_definition": item_source,
            "plug_set_definition": plug_source,
            "evidence_grade": "official_manifest_structural_only",
        },
        "weapon_count": len(records),
        "weapons": sorted(records, key=lambda r: r["item_hash"]),
        "limitations": (
            "Same-name variants remain separate exact hashes. currentlyCanRoll flags are "
            "not live acquisition, trait-role, enhanced-perk, PvE DPS or PvP TTK certification."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    root = Path(args.output_dir)
    index = json.loads((root / "item_socket_candidates.json").read_text(encoding="utf-8"))
    metadata = json.loads((root / "manifest_metadata_extended.json").read_text(encoding="utf-8"))
    result = export_weapon_evidence(index, metadata)
    (root / "weapon_legality_evidence_index.json").write_text(
        json.dumps(result, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"manifest_version": result["manifest_version"],
                      "weapon_count": result["weapon_count"],
                      "confidence_grade": result["provenance"]["evidence_grade"]}))


if __name__ == "__main__":
    main()
