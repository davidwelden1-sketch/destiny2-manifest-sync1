"""Audit exact plug-category labels from same-version Bungie definitions.

Official schema: https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html
Category labels identify plug categories, not necessarily weapon traits.
This audit does not certify current drops, enhanced perks, or playable pairs.
"""
from collections import Counter


def audit_weapon_plug_categories(weapons):
    """Count occurrences and distinct plug hashes without inferring perk legality."""
    if not isinstance(weapons, list):
        raise TypeError("weapons must be a list")
    counts = Counter()
    randomized_hashes = set()
    randomized_known_hashes = set()
    categories = Counter()
    seen_weapons = set()
    for weapon in weapons:
        if not isinstance(weapon, dict):
            raise ValueError("malformed weapon")
        item_hash = weapon.get("itemHash")
        if type(item_hash) is not int or not 0 <= item_hash <= 0xFFFFFFFF or item_hash in seen_weapons:
            raise ValueError("invalid or duplicate weapon hash")
        seen_weapons.add(item_hash)
        entries = weapon.get("resolvedPlugSets")
        if not isinstance(entries, list):
            raise ValueError("missing resolved plug sets")
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("kind") not in ("randomized", "reusable"):
                raise ValueError("malformed plug-set entry")
            kind = entry["kind"]
            if entry.get("definitionFound") is not True:
                counts[kind + "UnresolvedPlugSets"] += 1
                continue
            plugs = entry.get("plugs")
            if not isinstance(plugs, list):
                raise ValueError("resolved plug set must contain a list")
            for plug in plugs:
                if not isinstance(plug, dict):
                    raise ValueError("malformed plug")
                h = plug.get("plugItemHash")
                if type(h) is not int or not 0 <= h <= 0xFFFFFFFF:
                    raise ValueError("invalid plug item hash")
                cat_hash = plug.get("plugCategoryHash")
                cat_id = plug.get("plugCategoryIdentifier")
                if cat_hash is not None and (type(cat_hash) is not int or not 0 <= cat_hash <= 0xFFFFFFFF):
                    raise ValueError("invalid plug category hash")
                if cat_id is not None and not isinstance(cat_id, str):
                    raise ValueError("invalid plug category identifier")
                counts[kind + "Occurrences"] += 1
                known = cat_hash is not None and isinstance(cat_id, str) and bool(cat_id.strip())
                counts[kind + ("KnownCategoryOccurrences" if known else "UnknownCategoryOccurrences")] += 1
                if kind == "randomized":
                    randomized_hashes.add(h)
                    if known:
                        randomized_known_hashes.add(h)
                        categories[cat_id] += 1
                    if plug.get("plugRedacted") is True:
                        counts["randomizedRedactedPlugOccurrences"] += 1
                    if entry.get("isFakePlugSet") is True:
                        counts["randomizedFakeSetOccurrences"] += 1
    counts["weaponDefinitions"] = len(seen_weapons)
    counts["uniqueRandomizedPlugHashes"] = len(randomized_hashes)
    counts["uniqueRandomizedPlugHashesWithCategory"] = len(randomized_known_hashes)
    counts["uniqueRandomizedCategoryIdentifiers"] = len(categories)
    return {
        "counts": dict(sorted(counts.items())),
        "randomizedCategoryIdentifiersByOccurrence": [
            {"identifier": name, "occurrences": n}
            for name, n in sorted(categories.items(), key=lambda p: (-p[1], p[0]))
        ],
        "manifestDefinitionOnly": True,
        "certifiedTraitCount": None,
        "certifiedObtainableRollCount": None,
        "certifiedEnhancedPerkCount": None,
        "certifiedPvEOrPvPPerformance": False,
        "limitations": (
            "Plug categories are definition labels, not verified weapon trait roles. "
            "Counts include repeated socket memberships and may include fake/redacted sets. "
            "Missing category fields remain unknown. Acquisition, enhancement, Artifact "
            "selection, PvE boss damage/DR and PvP TTK require independent evidence."
        ),
    }
