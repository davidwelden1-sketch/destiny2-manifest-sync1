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
    resolved_plug_refs = build_weapon_plug_set_reference_index(weapon_refs, plug_definitions)
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
        "plug_set_join_scope": "Same-version definition joins; currentlyCanRoll is tri-state and not current acquisition, cross-socket roll or enhancement certification",
        "weapon_socket_reference_scope": "Definition references only; no plug-set resolution, obtainable rolls, enhanced eligibility or damage certification",
        "scope": "DestinyInventoryItemDefinition (en); API metadata, not measured sandbox values"
    }
    (OUT / "manifest_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (OUT / "inventory_index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "weapon_socket_refs_index.json").write_text(json.dumps(weapon_refs, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "weapon_plug_set_refs_index.json").write_text(json.dumps(resolved_plug_refs, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps(metadata, indent=2))

if __name__ == "__main__":
    main()
