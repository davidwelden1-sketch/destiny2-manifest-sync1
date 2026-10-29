#!/usr/bin/env python3
"""Fetch official Bungie manifest and create an auditable compact item index."""
import datetime as dt
import hashlib
import json
import os
import pathlib
import urllib.request

BASE = "https://www.bungie.net"
OUT = pathlib.Path(os.environ.get("OUTPUT_DIR", "output"))
OUT.mkdir(parents=True, exist_ok=True)

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Destiny2BuildLabManifestSync/0.1"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read()

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
    metadata = {
        "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "manifest_version": payload.get("version"),
        "manifest_endpoint": manifest_url,
        "definition_url": source_url,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "item_count": len(index),
        "scope": "DestinyInventoryItemDefinition (en); API metadata, not measured sandbox values"
    }
    (OUT / "manifest_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (OUT / "inventory_index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps(metadata, indent=2))

if __name__ == "__main__":
    main()
