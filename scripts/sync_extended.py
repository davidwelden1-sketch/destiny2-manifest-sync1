#!/usr/bin/env python3
"""Create a richer, provenance-labelled inventory and plug-set relationship index.

Reads the official English manifest JSON components directly. This is structural
data, NOT proof that a roll is currently obtainable or active in the sandbox.
"""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from http_retry import fetch_with_retry

BASE = "https://www.bungie.net"
OUT = Path(os.environ.get("OUTPUT_DIR", "output"))
OUT.mkdir(parents=True, exist_ok=True)

def download(url):
    return fetch_with_retry(url, user_agent="Destiny2BuildLab/0.2", timeout=180)

def main():
    manifest = json.loads(download(BASE + "/Platform/Destiny2/Manifest/"))
    if manifest.get("ErrorCode") != 1:
        raise RuntimeError(f"Bungie manifest error: {manifest.get('Message')}")
    data = manifest["Response"]
    paths = data["jsonWorldComponentContentPaths"]["en"]
    names = ("DestinyInventoryItemDefinition", "DestinyPlugSetDefinition",
             "DestinyStatDefinition", "DestinySandboxPerkDefinition",
             "DestinySocketTypeDefinition")
    tables = {}
    sources = {}
    for name in names:
        path = paths[name]
        url = path if path.startswith("https://") else BASE + path
        raw = download(url)
        tables[name] = json.loads(raw)
        sources[name] = {"url": url, "sha256": hashlib.sha256(raw).hexdigest(),
                         "count": len(tables[name])}
    items = tables["DestinyInventoryItemDefinition"]
    rows = []
    for key, item in items.items():
        d = item.get("displayProperties") or {}
        sockets = item.get("sockets") or {}
        inv = item.get("inventory") or {}
        stats = item.get("stats") or {}
        rows.append({
            "hash": int(key), "name": d.get("name", ""),
            "plugCategoryHash": (item.get("plug") or {}).get("plugCategoryHash"),
            "plugCategoryIdentifier": (item.get("plug") or {}).get("plugCategoryIdentifier"),
            "itemType": item.get("itemType"), "itemSubType": item.get("itemSubType"),
            "tierType": inv.get("tierType"), "equippable": item.get("equippable", False),
            "classType": item.get("classType"), "damageType": item.get("defaultDamageType"),
            "ammoType": (item.get("equippingBlock") or {}).get("ammoType"),
            "stats": {str(k): v.get("value") for k, v in (stats.get("stats") or {}).items()},
            "socketEntries": [
                {"socketTypeHash": s.get("socketTypeHash"),
                 "singleInitialItemHash": s.get("singleInitialItemHash"),
                 "randomizedPlugSetHash": s.get("randomizedPlugSetHash"),
                 "reusablePlugSetHash": s.get("reusablePlugSetHash"),
                 "defaultVisible": s.get("defaultVisible"),
                 "plugSources": s.get("plugSources"),
                 "preventInitializationOnVendorPurchase": s.get("preventInitializationOnVendorPurchase")}
                for s in sockets.get("socketEntries", [])],
        })
    rows.sort(key=lambda r: r["hash"])
    plugsets = {
        key: [p.get("plugItemHash") for p in value.get("reusablePlugItems", [])]
        for key, value in tables["DestinyPlugSetDefinition"].items()
    }
    # Preserve Bungie's per-plug currentlyCanRoll signal. This field is distinct
    # from membership in a historical plug set and is not proof of acquisition.
    # Missing/non-boolean flags remain unknown; never silently treat as True.
    plugset_roll_flags = {
        key: [{"plugItemHash": p.get("plugItemHash"),
               "currentlyCanRoll": p.get("currentlyCanRoll")
               if isinstance(p.get("currentlyCanRoll"), bool) else None}
              for p in value.get("reusablePlugItems", [])]
        for key, value in tables["DestinyPlugSetDefinition"].items()
    }
    socket_types = {
        key: {"socketCategoryHash": value.get("socketCategoryHash"),
              "plugWhitelist": value.get("plugWhitelist"),
              "visibility": value.get("visibility")}
        for key, value in tables["DestinySocketTypeDefinition"].items()
    }
    metadata = {"retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "manifest_version": data.get("version"), "sources": sources,
                "limitations": "Manifest socket/plug-set possibilities are not proof of obtainable rolls, PvP damage, active artifact, or stacking."}
    for filename, content in (
        ("manifest_metadata_extended.json", metadata),
        ("items_extended.json", rows),
        ("plugsets.json", plugsets),
        ("plugset_roll_flags.json", plugset_roll_flags),
        ("socket_types.json", socket_types)):
        (OUT / filename).write_text(json.dumps(content, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"manifest_version": data.get("version"), "items": len(rows),
                      "plugsets": len(plugsets), "sources": sources}, indent=2))

if __name__ == "__main__":
    main()
