"""Index Bungie weapon-definition socket references without inferring legal rolls.

Schema: https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html
A plug-set hash is a reference, not a resolved pool, an obtainable roll,
or proof that an enhanced perk is selectable. Same-named item hashes stay separate.
"""

def _optional_hash(value, field):
    if value is None:
        return None
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise ValueError(f"{field} must be a uint32 or null")
    return value


def build_weapon_socket_reference_index(records):
    """Return sorted definition-only references for all itemType=3 records."""
    if not isinstance(records, dict):
        raise TypeError("inventory definitions must be a mapping")
    index = []
    for key, item in records.items():
        if not isinstance(item, dict) or item.get("itemType") != 3:
            continue
        item_hash = _optional_hash(int(key), "item hash") if isinstance(key, str) and key.isdecimal() else _optional_hash(key, "item hash")
        sockets = item.get("sockets") or {}
        if not isinstance(sockets, dict):
            raise ValueError(f"malformed sockets for item {item_hash}")
        entries = sockets.get("socketEntries") or []
        if not isinstance(entries, list):
            raise ValueError(f"malformed socketEntries for item {item_hash}")
        socket_refs = []
        for position, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise ValueError(f"malformed socket {position} for item {item_hash}")
            reusable = entry.get("reusablePlugItems") or []
            if not isinstance(reusable, list):
                raise ValueError(f"malformed reusablePlugItems for item {item_hash}")
            reusable_hashes = []
            for plug in reusable:
                if not isinstance(plug, dict):
                    raise ValueError(f"malformed reusable plug for item {item_hash}")
                reusable_hashes.append(_optional_hash(plug.get("plugItemHash"), "plugItemHash"))
            socket_refs.append({
                "socketIndex": position,
                "socketTypeHash": _optional_hash(entry.get("socketTypeHash"), "socketTypeHash"),
                "randomizedPlugSetHash": _optional_hash(entry.get("randomizedPlugSetHash"), "randomizedPlugSetHash"),
                "reusablePlugSetHash": _optional_hash(entry.get("reusablePlugSetHash"), "reusablePlugSetHash"),
                "singleInitialItemHash": _optional_hash(entry.get("singleInitialItemHash"), "singleInitialItemHash"),
                "reusablePlugItemHashes": reusable_hashes,
            })
        index.append({
            "hash": item_hash,
            "name": (item.get("displayProperties") or {}).get("name", ""),
            "itemSubType": item.get("itemSubType"),
            "itemTypeDisplayName": item.get("itemTypeDisplayName"),
            "equippable": item.get("equippable", False),
            "sockets": socket_refs,
            "evidenceGrade": "manifest_definition_references_only",
            "certifiedObtainableRoll": False,
            "certifiedEnhancedPerks": False,
        })
    return sorted(index, key=lambda row: row["hash"])
