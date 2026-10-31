#!/usr/bin/env python3
"""Fetch official Bungie manifest and create an auditable compact item index."""
import datetime as dt
import hashlib
import json
import os
import pathlib
from http_retry import fetch_with_retry
from weapon_socket_refs import build_weapon_socket_reference_index
from weapon_plug_set_refs import build_weapon_plug_set_reference_index
from plug_coverage_audit import summarize_resolved_plug_coverage
from plug_uniqueness_audit import audit_unique_weapon_plugs
from plug_category_coverage_audit import audit_weapon_plug_categories
from plug_category_provenance import audit_category_provenance
from plug_category_socket_map import audit_category_socket_map

BASE = "https://www.bungie.net"
OUT = pathlib.Path(os.environ.get("OUTPUT_DIR", "output"))
OUT.mkdir(parents=True, exist_ok=True)

def get(url):
    return fetch_with_retry(url, user_agent="Destiny2BuildLabManifestSync/0.1", timeout=120)

def main():
    manifest_url = BASE + "/Platform/Destiny2/Manifest/"
    manifest = json.loads(get(manifest_url))
    if manifest.get("ErrorCode") != 1:
        raise RuntimeError("Bungie manifest endpoint returned an error: " + str(manifest.get("Message")))
    payload = manifest["Response"]
    relpath = payload["jsonWorldComponentContentPaths"]["en"]["DestinyInventoryItemDefinition"]
    source_url = relpath if relpath.startswith("https://") else BASE + relpath
    raw = get(source_url)
    records = json.loads(raw)
    if not isinstance(records, dict):
        raise ValueError("Unexpected inventory definition structure")
    index = []
    for key, item in records.items():
        display = item.get("displayProperties") or {}
        inv = item.get("inventory") or {}
        index.append({
            "hash": int(key),
            "name": display.get("name", ""),
            "itemType": item.get("itemType"),
            "itemSubType": item.get("itemSubType"),
            "tierType": inv.get("tierType"),
            "equippable": item.get("equippable", False),
            "collectibleHash": item.get("collectibleHash"),
        })
    index.sort(key=lambda x: x["hash"])
    weapon_refs = build_weapon_socket_reference_index(records)
    # Resolve the same-version DestinyPlugSetDefinition component. Socket
    # references alone do not reveal plug hashes or currentlyCanRoll flags.
    plug_relpath = payload["jsonWorldComponentContentPaths"]["en"]["DestinyPlugSetDefinition"]
    plug_url = plug_relpath if plug_relpath.startswith("https://") else BASE + plug_relpath
    plug_raw = get(plug_url)
    plug_definitions = json.loads(plug_raw)
    if not isinstance(plug_definitions, dict):
        raise ValueError("Unexpected plug-set definition structure")
    resolved_plug_refs = build_weapon_plug_set_reference_index(weapon_refs, plug_definitions, records)
    plug_coverage = summarize_resolved_plug_coverage(resolved_plug_refs)
    unique_plug_coverage = audit_unique_weapon_plugs(resolved_plug_refs)
    plug_category_coverage = audit_weapon_plug_categories(resolved_plug_refs)
    category_provenance = audit_category_provenance(resolved_plug_refs)
    category_socket_map = audit_category_socket_map(resolved_plug_refs)
    metadata = {
        "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "manifest_version": payload.get("version"),
        "manifest_endpoint": manifest_url,
        "definition_url": source_url,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "item_count": len(index),
        "weapon_definition_count": len(weapon_refs),
        "plug_set_definition_url": plug_url,
        "plug_set_definition_sha256": hashlib.sha256(plug_raw).hexdigest(),
        "plug_set_definition_count": len(plug_definitions),
        "resolved_weapon_definition_count": len(resolved_plug_refs),
        "plug_coverage_counts": plug_coverage["counts"],
        "unique_plug_coverage_counts": unique_plug_coverage["counts"],
        "plug_category_coverage_counts": plug_category_coverage["counts"],
        "plug_category_provenance_counts": category_provenance["counts"],
        "plug_category_socket_map_counts": category_socket_map["counts"],
        "plug_category_scope": "Same-manifest plug category labels, not certified traits, obtainable/enhanced rolls, PvE or PvP effects",
        "named_plug_resolution_scope": "Same-version DestinyInventoryItemDefinition display labels; names do not certify perk socket roles, roll acquisition or enhancement",
        "plug_set_join_scope": "Same-version definition joins; currentlyCanRoll is tri-state and not current acquisition, cross-socket roll or enhancement certification",
        "weapon_socket_reference_scope": "Definition socket references; separate resolved plug-set index supplies hashes and display names, but not obtainable rolls, enhanced eligibility or damage certification",
        "scope": "DestinyInventoryItemDefinition (en); API metadata, not measured sandbox values"
    }
    (OUT / "manifest_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (OUT / "inventory_index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "weapon_socket_refs_index.json").write_text(json.dumps(weapon_refs, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "weapon_plug_set_refs_index.json").write_text(json.dumps(resolved_plug_refs, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "weapon_plug_coverage.json").write_text(json.dumps(plug_coverage, indent=2) + "\n", encoding="utf-8")
    (OUT / "weapon_unique_plug_coverage.json").write_text(json.dumps(unique_plug_coverage, indent=2) + "\n", encoding="utf-8")
    (OUT / "weapon_plug_category_coverage.json").write_text(json.dumps(plug_category_coverage, indent=2) + "\n", encoding="utf-8")
    (OUT / "weapon_plug_category_provenance.json").write_text(json.dumps(category_provenance, indent=2) + "\n", encoding="utf-8")
    (OUT / "weapon_plug_category_socket_map.json").write_text(json.dumps(category_socket_map, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))

if __name__ == "__main__":
    main()
