"""Deduplicate same-manifest weapon plug memberships without certifying rolls.

A socket occurrence is not a distinct perk or a live roll. Bungie's plug-set
schema permits fake sets and repeated reusable memberships; count exact
weapon/plug identities separately from source and socket occurrences.
https://github.com/Bungie-net/api/wiki/2019-10-API-Updates-for-Sockets-and-Plugs-%28and-removal-of-a-long-deprecated-Stats-property%29
"""

def audit_unique_weapon_plugs(weapons):
    if not isinstance(weapons, list):
        raise TypeError("weapons must be a list")
    all_hashes, random_hashes, clear_hashes = set(), set(), set()
    counts = dict(weaponDefinitions=0, plugOccurrences=0,
                  distinctWeaponPlugMemberships=0,
                  distinctWeaponRandomizedMemberships=0,
                  distinctWeaponClearRandomizedMemberships=0,
                  weaponsWithTwoClearRandomizedSocketPositions=0,
                  excludedFakeOrRedactedRandomizedOccurrences=0,
                  unknownFakeOrRedactedRandomizedOccurrences=0)
    seen_weapons = set()
    for weapon in weapons:
        if not isinstance(weapon, dict):
            raise ValueError("malformed weapon")
        h = weapon.get("itemHash")
        if type(h) is not int or not 0 <= h <= 0xFFFFFFFF or h in seen_weapons:
            raise ValueError("invalid or duplicate weapon hash")
        seen_weapons.add(h)
        entries = weapon.get("resolvedPlugSets")
        if not isinstance(entries, list):
            raise ValueError("resolvedPlugSets must be a list")
        any_plugs, randomized, clear, clear_sockets = set(), set(), set(), set()
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("kind") not in ("randomized", "reusable"):
                raise ValueError("invalid plug-set entry")
            if type(entry.get("socketIndex")) is not int or entry["socketIndex"] < 0:
                raise ValueError("invalid socket index")
            found = entry.get("definitionFound")
            if type(found) is not bool:
                raise ValueError("definitionFound must be boolean")
            plugs = entry.get("plugs")
            if not found:
                if plugs is not None:
                    raise ValueError("unresolved plug set cannot contain plugs")
                continue
            if not isinstance(plugs, list):
                raise ValueError("resolved plug set requires plugs")
            fake, redacted = entry.get("isFakePlugSet"), entry.get("redacted")
            if any(flag is not None and type(flag) is not bool for flag in (fake, redacted)):
                raise ValueError("invalid fake/redacted flag")
            for plug in plugs:
                if not isinstance(plug, dict):
                    raise ValueError("invalid plug")
                ph = plug.get("plugItemHash")
                if type(ph) is not int or not 0 <= ph <= 0xFFFFFFFF:
                    raise ValueError("invalid plug hash")
                roll = plug.get("currentlyCanRoll")
                if roll is not None and type(roll) is not bool:
                    raise ValueError("invalid roll flag")
                counts["plugOccurrences"] += 1
                any_plugs.add(ph)
                all_hashes.add(ph)
                if entry["kind"] == "randomized":
                    randomized.add(ph)
                    random_hashes.add(ph)
                    if fake is True or redacted is True:
                        counts["excludedFakeOrRedactedRandomizedOccurrences"] += 1
                    elif fake is not False or redacted is not False:
                        counts["unknownFakeOrRedactedRandomizedOccurrences"] += 1
                    elif roll is True:
                        clear.add(ph)
                        clear_hashes.add(ph)
                        clear_sockets.add(entry["socketIndex"])
        counts["weaponDefinitions"] += 1
        counts["distinctWeaponPlugMemberships"] += len(any_plugs)
        counts["distinctWeaponRandomizedMemberships"] += len(randomized)
        counts["distinctWeaponClearRandomizedMemberships"] += len(clear)
        if len(clear_sockets) >= 2:
            counts["weaponsWithTwoClearRandomizedSocketPositions"] += 1
    counts["uniquePlugHashesAllSources"] = len(all_hashes)
    counts["uniquePlugHashesRandomized"] = len(random_hashes)
    counts["uniquePlugHashesClearRandomized"] = len(clear_hashes)
    counts["repeatedSocketOccurrencesBeyondWeaponPlugMemberships"] = (
        counts["plugOccurrences"] - counts["distinctWeaponPlugMemberships"])
    return {
        "counts": counts,
        "manifestJoinOnly": True,
        "certifiedObtainableRollCount": None,
        "certifiedEnhancedPerkCount": None,
        "certifiedPvEOrPvPPerformance": False,
        "limitations": (
            "Unique plug hashes and exact weapon/plug memberships are not unique "
            "perks, live drops or legal combinations. Clear randomized evidence "
            "requires explicit isFakePlugSet=false, redacted=false and "
            "currentlyCanRoll=true; even two sockets do not certify a roll. "
            "Socket roles, acquisition, enhancement and Artifact remain unverified."
        ),
    }
