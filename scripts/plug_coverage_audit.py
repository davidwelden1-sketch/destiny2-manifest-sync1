"""Summarize same-manifest weapon plug resolution without certifying rolls.

Every plug entry is a socket occurrence, not a unique perk or an obtainable
weapon roll. Fake/redacted/missing definitions remain explicit evidence gaps.
"""
from collections import Counter


def summarize_resolved_plug_coverage(weapons):
    if not isinstance(weapons, list):
        raise TypeError("resolved weapons must be a list")
    counts = Counter()
    seen = set()
    for weapon in weapons:
        if not isinstance(weapon, dict):
            raise ValueError("malformed weapon")
        h = weapon.get("itemHash")
        if type(h) is not int or not 0 <= h <= 0xFFFFFFFF or h in seen:
            raise ValueError("invalid or repeated exact weapon hash")
        seen.add(h)
        sets = weapon.get("resolvedPlugSets")
        if not isinstance(sets, list):
            raise ValueError("resolvedPlugSets must be a list")
        counts["weaponDefinitions"] += 1
        if not sets:
            counts["weaponsWithoutResolvedPlugSets"] += 1
        for entry in sets:
            if not isinstance(entry, dict) or entry.get("kind") not in ("randomized", "reusable"):
                raise ValueError("malformed plug-set reference")
            kind = entry["kind"]
            counts["plugSetReferences"] += 1
            found = entry.get("definitionFound")
            if type(found) is not bool:
                raise ValueError("definitionFound must be boolean")
            if not found:
                if entry.get("plugs") is not None:
                    raise ValueError("missing plug set must not have plugs")
                counts["missingPlugSetDefinitions"] += 1
                continue
            fake, redacted = entry.get("isFakePlugSet"), entry.get("redacted")
            if any(flag is not None and type(flag) is not bool for flag in (fake, redacted)):
                raise ValueError("fake/redacted flags must be bool or null")
            if fake is True:
                counts["fakePlugSetReferences"] += 1
            if redacted is True:
                counts["redactedPlugSetReferences"] += 1
            plugs = entry.get("plugs")
            if not isinstance(plugs, list):
                raise ValueError("found plug set must provide a list")
            if not plugs:
                counts["emptyPlugSetReferences"] += 1
            for plug in plugs:
                if not isinstance(plug, dict):
                    raise ValueError("malformed plug")
                ph = plug.get("plugItemHash")
                if type(ph) is not int or not 0 <= ph <= 0xFFFFFFFF:
                    raise ValueError("invalid plug hash")
                named = plug.get("plugName")
                if named is not None and (not isinstance(named, str) or not named.strip()):
                    raise ValueError("plugName must be a nonempty string or null")
                defined = plug.get("plugDefinitionFound")
                if type(defined) is not bool:
                    raise ValueError("plugDefinitionFound must be boolean")
                roll = plug.get("currentlyCanRoll")
                if roll is not None and type(roll) is not bool:
                    raise ValueError("currentlyCanRoll must be bool or null")
                counts["plugOccurrences"] += 1
                counts[kind + "PlugOccurrences"] += 1
                counts["namedPlugOccurrences" if named else "unnamedPlugOccurrences"] += 1
                if not defined:
                    counts["missingPlugItemDefinitions"] += 1
                counts["currentlyCanRoll_" + ("true" if roll is True else
                       "false" if roll is False else "unknown")] += 1
                if kind == "randomized" and roll is True and fake is not True and redacted is not True:
                    counts["explicitTrueRandomizedOccurrences"] += 1
    fields = ("weaponDefinitions", "weaponsWithoutResolvedPlugSets",
              "plugSetReferences", "missingPlugSetDefinitions",
              "fakePlugSetReferences", "redactedPlugSetReferences",
              "emptyPlugSetReferences", "plugOccurrences",
              "randomizedPlugOccurrences", "reusablePlugOccurrences",
              "namedPlugOccurrences", "unnamedPlugOccurrences",
              "missingPlugItemDefinitions", "currentlyCanRoll_true",
              "currentlyCanRoll_false", "currentlyCanRoll_unknown",
              "explicitTrueRandomizedOccurrences")
    return {
        "counts": {field: counts[field] for field in fields},
        "unit": "weapon definitions, plug-set references and socket-level plug occurrences; not unique rolls",
        "manifestJoinOnly": True,
        "certifiedObtainableRollCount": None,
        "certifiedEnhancedPerkCount": None,
        "certifiedPvEOrPvPPerformance": False,
        "limitations": (
            "A currentlyCanRoll=true plug is definition evidence only. "
            "Fake/redacted sets, unresolved names, missing definitions, "
            "socket role, acquisition, enhancement and cross-socket compatibility "
            "require independent review."
        ),
    }
