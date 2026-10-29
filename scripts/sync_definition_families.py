"""Download and index additional official Destiny manifest definition families.

Manifest definitions are structural metadata, not proof of current sandbox mechanics.
"""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://www.bungie.net"
FAMILIES = (
    "DestinyDamageTypeDefinition",
    "DestinyClassDefinition",
    "DestinyActivityDefinition",
    "DestinyActivityModeDefinition",
    "DestinyStatGroupDefinition",
    "DestinySocketTypeDefinition",
    "DestinySocketCategoryDefinition",
    "DestinyProgressionDefinition",
    "DestinyObjectiveDefinition",
    "DestinyCollectibleDefinition",
    "DestinyRecordDefinition",
    "DestinyTraitDefinition",
    "DestinyBreakerTypeDefinition",
    "DestinyEnergyTypeDefinition",
    "DestinyTalentGridDefinition",
    "DestinyNodeStepSummaryDefinition",
    "DestinyInventoryBucketDefinition",
    "DestinyItemCategoryDefinition",
    "DestinyPresentationNodeDefinition",
    "DestinyPowerCapDefinition",
)

def fetch(url):
    with urlopen(Request(url, headers={"User-Agent": "Destiny2BuildLab/0.3"}), timeout=180) as response:
        return response.read()

def main():
    root = Path(os.environ.get("OUTPUT_DIR", "output"))
    root.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(fetch(BASE + "/Platform/Destiny2/Manifest/"))
    if manifest.get("ErrorCode") != 1:
        raise RuntimeError("Bungie manifest request failed")
    response = manifest["Response"]
    paths = response["jsonWorldComponentContentPaths"]["en"]
    catalog = {}
    missing = []
    for family in FAMILIES:
        path = paths.get(family)
        if not path:
            missing.append(family)
            continue
        url = path if path.startswith("https://") else BASE + path
        raw = fetch(url)
        definitions = json.loads(raw)
        records = []
        for hash_value, value in definitions.items():
            display = value.get("displayProperties") or {}
            records.append({"hash": int(hash_value),
                            "name": display.get("name", ""),
                            "description": display.get("description", ""),
                            "icon": display.get("icon"),
                            "raw_definition": value})
        records.sort(key=lambda row: row["hash"])
        filename = "definitions_" + family + ".json"
        (root / filename).write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")))
        catalog[family] = {"file": filename, "count": len(records),
                           "sha256": hashlib.sha256(raw).hexdigest(), "url": url}
    metadata = {"manifest_version": response.get("version"),
                "retrieved_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "expected_families": list(FAMILIES),
                "families": catalog, "unavailable_families": missing,
                "interpretation": "Official definitions; not measured gameplay values or proof of active perk legality."}
    (root / "definition_catalog.json").write_text(json.dumps(metadata, indent=2))
    print(json.dumps({"version": response.get("version"),
                      "families": len(catalog), "missing": missing,
                      "definitions": sum(x["count"] for x in catalog.values())}))

if __name__ == "__main__":
    main()
