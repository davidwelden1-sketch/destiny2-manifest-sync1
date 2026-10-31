"""Map same-manifest randomized plug categories to exact weapon socket positions.

Category identifiers and socket positions are structural evidence only; neither
proves a trait role, an obtainable roll, enhancement or simultaneous activation.
Official schema: https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html
"""
from collections import Counter, defaultdict


def audit_category_socket_map(weapons):
    if not isinstance(weapons, list):
        raise TypeError("weapons must be a list")
    category_sockets = defaultdict(lambda: defaultdict(lambda: {"weapons": set(), "plugs": set(), "occurrences": 0}))
    category_weapons = defaultdict(lambda: defaultdict(set))
    identifiers = defaultdict(set)
    hashes = defaultdict(set)
    counts = Counter()
    seen = set()
    for weapon in weapons:
        if not isinstance(weapon, dict):
            raise ValueError("malformed weapon")
        item = weapon.get("itemHash")
        if type(item) is not int or not 0 <= item <= 0xFFFFFFFF or item in seen:
            raise ValueError("invalid or duplicate weapon hash")
        seen.add(item)
        entries = weapon.get("resolvedPlugSets")
        if not isinstance(entries, list):
            raise ValueError("missing resolved plug sets")
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("kind") not in ("randomized", "reusable"):
                raise ValueError("malformed plug-set entry")
            if entry["kind"] != "randomized":
                continue
            position = entry.get("socketIndex")
            if type(position) is not int or position < 0:
                raise ValueError("randomized plug set requires a nonnegative socketIndex")
            if entry.get("definitionFound") is not True:
                counts["unresolvedRandomizedSets"] += 1
                continue
            plugs = entry.get("plugs")
            if not isinstance(plugs, list):
                raise ValueError("resolved randomized plug set must contain plugs")
            fake, redacted = entry.get("isFakePlugSet"), entry.get("redacted")
            if any(x is not None and type(x) is not bool for x in (fake, redacted)):
                raise ValueError("invalid set provenance flag")
            for plug in plugs:
                if not isinstance(plug, dict):
                    raise ValueError("malformed plug")
                h, ch, ci = plug.get("plugItemHash"), plug.get("plugCategoryHash"), plug.get("plugCategoryIdentifier")
                if type(h) is not int or not 0 <= h <= 0xFFFFFFFF:
                    raise ValueError("invalid plug hash")
                if ch is not None and (type(ch) is not int or not 0 <= ch <= 0xFFFFFFFF):
                    raise ValueError("invalid category hash")
                if ci is not None and not isinstance(ci, str):
                    raise ValueError("invalid category identifier")
                roll, plug_redacted = plug.get("currentlyCanRoll"), plug.get("plugRedacted")
                if any(x is not None and type(x) is not bool for x in (roll, plug_redacted)):
                    raise ValueError("invalid plug provenance flag")
                counts["randomizedOccurrences"] += 1
                if ch is None or not ci or not ci.strip():
                    counts["unknownCategoryOccurrences"] += 1
                    continue
                key = (ch, ci)
                identifiers[ci].add(ch)
                hashes[ch].add(ci)
                category_weapons[key][item].add(position)
                record = category_sockets[key][position]
                record["occurrences"] += 1
                record["weapons"].add(item)
                record["plugs"].add(h)
                if fake is True or redacted is True or plug_redacted is True or roll is False:
                    counts["explicitlyExcludedOccurrences"] += 1
                elif fake is False and redacted is False and plug_redacted is False and roll is True:
                    counts["fullyExplicitDefinitionFlagOccurrences"] += 1
                else:
                    counts["unknownProvenanceOccurrences"] += 1
    categories = []
    for (ch, ci), slots in sorted(category_sockets.items(), key=lambda kv: (-sum(s["occurrences"] for s in kv[1].values()), kv[0])):
        categories.append({
            "categoryHash": ch, "identifier": ci,
            "uniqueWeaponDefinitions": len(category_weapons[(ch, ci)]),
            "weaponsWithMultipleSocketPositions": sum(len(pos) > 1 for pos in category_weapons[(ch, ci)].values()),
            "socketPositions": [
                {"socketIndex": pos, "occurrences": rec["occurrences"],
                 "uniqueWeaponDefinitions": len(rec["weapons"]), "uniquePlugHashes": len(rec["plugs"])}
                for pos, rec in sorted(slots.items())
            ],
        })
    return {
        "counts": {**dict(sorted(counts.items())), "uniqueCategoryIdentities": len(categories),
                   "categoryIdentifiersWithMultipleHashes": sum(len(v) > 1 for v in identifiers.values()),
                   "categoryHashesWithMultipleIdentifiers": sum(len(v) > 1 for v in hashes.values()),
                   "categoriesSpanningMultipleSocketIndexes": sum(len(c["socketPositions"]) > 1 for c in categories)},
        "categories": categories,
        "manifestDefinitionOnly": True,
        "certifiedTraitCount": None,
        "certifiedObtainableRollCount": None,
        "certifiedEnhancedPerkCount": None,
        "certifiedCrossSocketPairCount": None,
        "gameplayMeasured": False,
        "limitations": ("Socket indexes are weapon-relative; cross-weapon positions are not fixed trait slots. "
                        "Category labels do not prove acquisition, perk pairing, enhancement, "
                        "current Artifact legality, PvE damage or PvP TTK."),
    }
