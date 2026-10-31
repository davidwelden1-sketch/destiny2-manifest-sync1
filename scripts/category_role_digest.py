"""Small, auditable manifest category digest for GitHub Actions logs.

Shows named SAME-MANIFEST memberships without implying obtainable or enhanced
rolls. The complete provenance remains in weapon_plug_category_role_triage.json.
"""
def build_category_role_digest(triage):
    if not isinstance(triage, dict) or not isinstance(triage.get("categories"), list):
        raise TypeError("Expected role-triage categories")
    rows = []
    seen = set()
    for row in triage["categories"]:
        if not isinstance(row, dict):
            raise ValueError("Invalid category row")
        h, label = row.get("categoryHash"), row.get("identifier")
        if type(h) is not int or not 0 <= h <= 0xFFFFFFFF or not isinstance(label, str) or not label.strip():
            raise ValueError("Invalid category identity")
        if (h, label) in seen:
            raise ValueError("Duplicate category identity")
        seen.add((h, label))
        samples = row.get("sampleNamedDefinitionMemberships")
        if not isinstance(samples, list):
            raise ValueError("Missing sample membership list")
        example = None
        for sample in samples:
            if not isinstance(sample, dict):
                raise ValueError("Invalid sample")
            if (type(sample.get("itemHash")) is int
                and type(sample.get("plugHash")) is int
                and isinstance(sample.get("weaponName"), str)
                and isinstance(sample.get("plugName"), str)
                and sample["weaponName"].strip() and sample["plugName"].strip()):
                example = {
                    "itemHash": sample["itemHash"], "weaponName": sample["weaponName"],
                    "plugHash": sample["plugHash"], "plugName": sample["plugName"],
                }
                break
        rows.append({
            "categoryHash": h, "identifier": label,
            "roleScreen": row.get("roleScreen"),
            "occurrences": row.get("occurrences"),
            "uniqueWeaponDefinitions": row.get("uniqueWeaponDefinitions"),
            "exampleSameManifestMembership": example,
            "certifiedPlayableTrait": False,
            "certifiedObtainableRoll": False,
            "certifiedEnhancedPerk": False,
        })
    return {
        "categories": sorted(rows, key=lambda r: (r["identifier"], r["categoryHash"])),
        "evidenceGrade": "same_manifest_definition_only",
        "limitations": "Examples are not confirmed trait roles, obtainable or enhanced rolls, cross-socket pairs, or gameplay measurements.",
    }
