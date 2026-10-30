"""Official 9.7.0 Shieldburst Rally weapon-type eligibility, NOT gameplay proof.

Bungie 2026-06-09: Sunbreaker Shieldburst Rally Barricade grants
"scorching rounds" to allies' Solar and Kinetic weapons while behind it.
Source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0

No published scorch stacks, damage, source ownership, PvP breakpoint,
Artifact interaction, or measured uptime is assumed here.
"""
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_DATE = "2026-06-09"
REVIEWED_DATE = "2026-10-30"
_DAMAGE_TYPES = {"kinetic", "solar", "arc", "void", "stasis", "strand"}


def rally_scorching_rounds_eligibility(*, class_name, subclass, aspect_equipped,
                                      barricade_type, barricade_deployed,
                                      actor_is_ally, ally_behind_barricade,
                                      weapon_damage_type):
    """Return official textual eligibility, not a verified activation.

    Damage type is distinct from weapon inventory slot: Stasis and Strand
    weapons in the kinetic slot are not Kinetic-damage weapons.
    None for a required condition yields unknown unless another condition
    is explicitly contradicted.
    """
    for value in (aspect_equipped, barricade_deployed, actor_is_ally,
                  ally_behind_barricade):
        if value is not None and type(value) is not bool:
            raise ValueError("condition flags must be booleans or None")
    for value in (class_name, subclass, barricade_type, weapon_damage_type):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError("text conditions must be nonempty strings or None")
    damage_type = weapon_damage_type.strip().casefold() if weapon_damage_type is not None else None
    if damage_type is not None and damage_type not in _DAMAGE_TYPES:
        raise ValueError("weapon_damage_type must be a known elemental damage type")
    conditions = {
        "titan": None if class_name is None else class_name.strip().casefold() == "titan",
        "sunbreaker": None if subclass is None else subclass.strip().casefold() == "sunbreaker",
        "shieldburst": aspect_equipped,
        "rally": None if barricade_type is None else barricade_type.strip().casefold() == "rally",
        "deployed": barricade_deployed,
        "ally": actor_is_ally,
        "behind": ally_behind_barricade,
        "solar_or_kinetic_damage": None if damage_type is None else damage_type in {"solar", "kinetic"},
    }
    if False in conditions.values():
        status = "official_conditions_not_met"
    elif None in conditions.values():
        status = "insufficient_inputs"
    else:
        status = "official_text_conditions_met_not_gameplay_verified"
    return {
        "status": status,
        "conditions": conditions,
        "source_url": SOURCE_URL,
        "source_date": SOURCE_DATE,
        "reviewed_date": REVIEWED_DATE,
        "activation_measured": False,
        "scorch_stacks": None,
        "scorch_source_ownership": None,
        "damage_multiplier": None,
        "pvp_breakpoint": None,
        "artifact_synergy_certified": False,
        "weapon_roll_legality_certified": False,
    }
