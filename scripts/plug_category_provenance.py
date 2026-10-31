"""Audit category provenance by unique weapon and plug identity.

Same-manifest plug category metadata is definition evidence, not a perk role,
currently obtainable roll, enhanced perk, or gameplay measurement.
Source: https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html
"""

from collections import Counter, defaultdict


def audit_category_provenance(weapons):
    """Separate occurrence counts from distinct plug and weapon membership."""
    if not isinstance(weapons, list):
        raise TypeError("weapons must be a list")
    counts = Counter()
    by_category = defaultdict(lambda: {"plugs": set(), "weapons": set(), "counts": Counter()})
    identities = defaultdict(set)
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
                raise ValueError("malformed plug set")
            if entry["kind"] != "randomized":
                continue
            if entry.get("definitionFound") is not True:
                counts["unresolvedRandomizedSets"] += 1
                continue
            plugs = entry.get("plugs")
            if not isinstance(plugs, list):
                raise ValueError("resolved randomized set must contain plugs")
            flags = (entry.get("isFakePlugSet"), entry.get("redacted"))
            if any(x is not None and type(x) is not bool for x in flags):
                raise ValueError("invalid set provenance flag")
            for plug in plugs:
                if not isinstance(plug, dict):
                    raise ValueError("malformed plug")
                h, ch, ci = (plug.get("plugItemHash"), plug.get("plugCategoryHash"),
                             plug.get("plugCategoryIdentifier"))
                if type(h) is not int or not 0 <= h <= 0xFFFFFFFF:
                    raise ValueError("invalid plug hash")
                if ch is not None and (type(ch) is not int or not 0 <= ch <= 0xFFFFFFFF):
                    raise ValueError("invalid category hash")
                if ci is not None and not isinstance(ci, str):
                    raise ValueError("invalid category identifier")
                roll, redacted = plug.get("currentlyCanRoll"), plug.get("plugRedacted")
                if any(x is not None and type(x) is not bool for x in (roll, redacted)):
                    raise ValueError("invalid plug provenance flag")
                counts["randomizedOccurrences"] += 1
                if ch is None or not ci or not ci.strip():
                    counts["unknownCategoryOccurrences"] += 1
                    continue
                key = (ch, ci)
                identities[h].add(key)
                record = by_category[key]
                record["plugs"].add(h)
                record["weapons"].add(item_hash)
                record["counts"]["occurrences"] += 1
                if True in flags or redacted is True or roll is False:
                    record["counts"]["explicitlyExcludedOccurrences"] += 1
                elif flags == (False, False) and redacted is False and roll is True:
                    record["counts"]["fullyExplicitDefinitionFlagOccurrences"] += 1
                else:
                    record["counts"]["unknownProvenanceOccurrences"] += 1
    conflicts = {h: sorted(labels) for h, labels in identities.items() if len(labels) > 1}
    return {
        "counts": {
            **dict(sorted(counts.items())),
            "uniqueKnownCategoryPlugHashes": len(identities),
            "plugHashesWithConflictingCategoryIdentity": len(conflicts),
            "uniqueCategoryIdentities": len(by_category),
        },
        "categories": [
            {"categoryHash": h, "identifier": identifier,
             "occurrences": record["counts"]["occurrences"],
             "uniquePlugHashes": len(record["plugs"]),
             "uniqueWeaponDefinitions": len(record["weapons"]),
             "explicitlyExcludedOccurrences": record["counts"]["explicitlyExcludedOccurrences"],
             "fullyExplicitDefinitionFlagOccurrences": record["counts"]["fullyExplicitDefinitionFlagOccurrences"],
             "unknownProvenanceOccurrences": record["counts"]["unknownProvenanceOccurrences"]}
            for (h, identifier), record in sorted(by_category.items(), key=lambda x: (-x[1]["counts"]["occurrences"], x[0]))
        ],
        "conflictingCategoryIdentityExamples": [
            {"plugHash": h, "categoryIdentities": [
                {"categoryHash": ch, "identifier": ci} for ch, ci in labels]}
            for h, labels in sorted(conflicts.items())[:20]
        ],
        "manifestDefinitionOnly": True,
        "certifiedObtainableRollCount": None,
        "certifiedEnhancedPerkCount": None,
        "certifiedPvEOrPvPPerformance": False,
        "limitations": (
            "Category identities and explicit provenance flags are structural only. "
            "No trait role, current acquisition, enhanced eligibility, cross-socket "
            "co-occurrence, Artifact allocation, PvE damage/DR or PvP TTK is certified."
        ),
    }
