"""Fail-closed role triage of same-manifest randomized weapon plug categories.

This is a prioritization screen, NOT a trait-role, acquisition, enhancement,
cross-socket, or gameplay certification. Explicit component identifiers are
labels observed in the October 2026 manifest, not guaranteed permanent IDs.
Sources:
https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html
https://bungie-net.github.io/multi/schema_Destiny-Definitions-Sockets-DestinySocketTypeDefinition.html
"""

# Keep aligned with the explicit component screen in audit_weapon_socket_roles.py.
# Unknown categories, including "frames", MUST remain unclassified.
EXPLICIT_COMPONENT_IDENTIFIERS = frozenset((
    "barrels", "magazines", "magazines_gl", "tubes", "batteries",
    "v300.weapon.damage_type.energy",
))


def triage_category_roles(provenance, socket_map):
    """Join two independently computed reports by exact category hash AND ID.

    Fail on inconsistent category coverage instead of inventing role evidence.
    Category names alone never certify a playable weapon trait.
    """
    if not isinstance(provenance, dict) or not isinstance(socket_map, dict):
        raise TypeError("Expected two report objects")

    def indexed(report):
        categories = report.get("categories")
        if not isinstance(categories, list):
            raise ValueError("Missing category rows")
        by_key = {}
        for row in categories:
            if not isinstance(row, dict):
                raise ValueError("Malformed category row")
            h, label = row.get("categoryHash"), row.get("identifier")
            if type(h) is not int or not 0 <= h <= 0xFFFFFFFF:
                raise ValueError("Invalid category hash")
            if not isinstance(label, str) or not label.strip():
                raise ValueError("Invalid category identifier")
            key = (h, label)
            if key in by_key:
                raise ValueError("Duplicate category identity")
            by_key[key] = row
        return by_key

    left, right = indexed(provenance), indexed(socket_map)
    if set(left) != set(right):
        raise ValueError("Category coverage mismatch between reports")
    rows = []
    for (h, identifier) in sorted(left, key=lambda k: (k[1], k[0])):
        p, s = left[(h, identifier)], right[(h, identifier)]
        for field in ("uniqueWeaponDefinitions",):
            if type(p.get(field)) is not int or p[field] < 0 or p[field] != s.get(field):
                raise ValueError("Category weapon membership mismatch")
        occurrences = p.get("occurrences")
        positions = s.get("socketPositions")
        if type(occurrences) is not int or occurrences < 0 or not isinstance(positions, list):
            raise ValueError("Missing occurrence or socket evidence")
        if sum(x.get("occurrences", -1) for x in positions if isinstance(x, dict)) != occurrences:
            raise ValueError("Category occurrence totals disagree")
        samples = p.get("sampleNamedDefinitionMemberships", [])
        if not isinstance(samples, list):
            raise ValueError("Malformed named membership samples")
        component = identifier in EXPLICIT_COMPONENT_IDENTIFIERS
        rows.append({
            "categoryHash": h, "identifier": identifier,
            "roleScreen": ("explicit_component_label" if component
                           else "unclassified_not_trait_certified"),
            "componentLabel": (identifier if component else None),
            "occurrences": occurrences,
            "uniqueWeaponDefinitions": p["uniqueWeaponDefinitions"],
            "socketPositions": sorted(
                [x["socketIndex"] for x in positions
                 if isinstance(x, dict) and type(x.get("socketIndex")) is int]),
            "sampleNamedDefinitionMemberships": samples[:4],
            "certifiedWeaponTrait": False,
            "certifiedCurrentAcquisition": False,
            "certifiedEnhancedEligibility": False,
        })
    return {
        "counts": {
            "categoryIdentities": len(rows),
            "explicitComponentLabelCategories": sum(
                x["roleScreen"] == "explicit_component_label" for x in rows),
            "unclassifiedCategories": sum(
                x["roleScreen"] == "unclassified_not_trait_certified" for x in rows),
        },
        "categories": rows,
        "manifestDefinitionOnly": True,
        "certifiedPlayableTraitCount": None,
        "certifiedObtainableRollCount": None,
        "certifiedEnhancedPerkCount": None,
        "gameplayMeasured": False,
        "limitations": (
            "Only six exact category labels receive an explicit component screen. "
            "All other categories, including frames, remain unclassified. "
            "Even a component label is not proof of an active runtime socket. "
            "Manifest membership does not certify drops, enhancement, cross-socket "
            "rolls, Artifact allocation, PvE damage/DR or PvP TTK."
        ),
    }
