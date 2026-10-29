"""Source-separated Bungie manifest socket provenance for exact item hashes.

Does not infer playable perk combinations, active frames, or obtainability.
Schema: https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html
"""
RUNTIME_FLAGS = {1: "inventory_sourced", 2: "reusable_runtime",
                 4: "profile_plug_set", 8: "character_plug_set"}

def socket_provenance(item_hash, item_definitions, plug_sets):
    """Return socket references with missing-source and runtime warnings."""
    if type(item_hash) is not int or item_hash < 0:
        raise ValueError("item_hash must be a nonnegative integer")
    if not isinstance(item_definitions, dict) or not isinstance(plug_sets, dict):
        raise TypeError("manifest components must be mappings")
    item = item_definitions.get(str(item_hash), item_definitions.get(item_hash))
    if not isinstance(item, dict):
        return {"item_hash": item_hash, "sockets": [], "status": "item_missing"}
    socket_block = item.get("sockets") or {}
    if not isinstance(socket_block, dict):
        return {"item_hash": item_hash, "sockets": [], "status": "malformed_sockets"}
    sockets = socket_block.get("socketEntries", [])
    if not isinstance(sockets, list):
        return {"item_hash": item_hash, "sockets": [], "status": "malformed_sockets"}
    results = []
    for index, entry in enumerate(sockets):
        if not isinstance(entry, dict):
            return {"item_hash": item_hash, "sockets": [], "status": "malformed_entry"}
        flags = entry.get("plugSources", 0)
        if type(flags) is not int or flags < 0:
            return {"item_hash": item_hash, "sockets": [], "status": "malformed_plug_sources"}
        references = {}
        unresolved = []
        fake_sets = []
        for field in ("randomizedPlugSetHash", "reusablePlugSetHash"):
            h = entry.get(field)
            if h is None:
                continue
            if type(h) is not int or h < 0:
                return {"item_hash": item_hash, "sockets": [], "status": "malformed_plug_set_hash"}
            references[field] = h
            plugset = plug_sets.get(str(h), plug_sets.get(h))
            if not isinstance(plugset, dict):
                unresolved.append(field)
            elif plugset.get("isFakePlugSet") is True:
                fake_sets.append(field)
        results.append({
            "socket_index": index,
            "plug_sources": flags,
            "runtime_sources": [label for bit, label in RUNTIME_FLAGS.items() if flags & bit],
            "unknown_source_bits": flags & ~15,
            "plug_set_references": references,
            "unresolved_references": unresolved,
            "fake_plug_sets": fake_sets,
            "initial_plug_hash": entry.get("singleInitialItemHash"),
            "certified_roll": False,
        })
    return {"item_hash": item_hash, "sockets": results, "status": "manifest_structure_only"}
