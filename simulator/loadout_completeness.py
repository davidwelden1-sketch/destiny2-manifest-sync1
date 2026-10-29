"""Phase 4: inspect build completeness without pretending to verify mechanics.

A complete field list is necessary but never sufficient for certification.
"""
REQUIRED_LOADOUT = (
    "class", "activity", "artifact_perks", "exotic_armor",
    "subclass", "super", "aspects", "fragments",
    "grenade", "melee", "class_ability", "armor_stats",
    "armor_mods", "kinetic_slot", "energy_slot", "power_slot",
    "weapon_perks", "rotation", "source_records",
)

def loadout_gaps(build):
    if not isinstance(build, dict):
        raise TypeError("build must be a mapping")
    missing = []
    for field in REQUIRED_LOADOUT:
        value = build.get(field)
        if value is None or value == "" or value == [] or value == {}:
            missing.append(field)
    return {"complete_fields": not missing, "missing": tuple(missing),
            "certified_build": False, "status": "field_completeness_only"}
