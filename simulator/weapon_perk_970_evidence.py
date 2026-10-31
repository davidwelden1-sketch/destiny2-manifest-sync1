"""Official June 9 2026 weapon-perk patch parameters, not gameplay calibration.

Source: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
The patch specifies conditional damage bonuses, not absolute damage, legal
weapon rolls, stacking groups, or observed PvP TTK. Never use these parameters
as measured current gameplay or multiply them into an unverified build.
"""

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_DATE = "2026-06-09"
PATCH_VERSION = "9.7.0"

# Patch values are fractions of base damage, not multipliers.
# The bonus for Full Court is a MAXIMUM on its EXPLOSIVE component, not
# a constant bonus to impact + splash. No enhanced Full Court value is given.
_PATCH_RULES = {
    "focused_fury": {
        "standard_bonus": 0.25,
        "bonus_scope": "conditional_weapon_damage",
        "activation": {"magazine_hit_fraction": 0.35},
        "prior_bonus": 0.20,
    },
    "full_court": {
        "standard_bonus": 0.35,
        "bonus_scope": "maximum_explosive_component_only",
        "activation": {"range_to_maximum": None, "distance_curve": None},
        "prior_bonus": 0.25,
    },
    "lasting_impression": {
        "standard_bonus": 0.35,
        "bonus_scope": "explosive_component_only",
        "activation": {"detonation_timing": None},
        "prior_bonus": 0.25,
    },
    "reservoir_burst": {
        "standard_bonus": 0.30,
        "enhanced_bonus": 0.33,
        "bonus_scope": "conditional_weapon_damage",
        "activation": {"trigger_requirements": None},
        "prior_bonus": 0.25,
        "prior_enhanced_bonus": 0.275,
    },
}

# Official patch says these hit counts were REDUCED; it does not establish
# exact hit registration, enemy targeting, orb ownership or in-game uptime.
_ORB_HITS = {"wave_frame_grenade_launcher": (4, 10),
             "rocket_launcher": (3, 6)}


def patch_weapon_perk_parameter(perk, *, activity, enhanced=False,
                                source_patch_version=PATCH_VERSION):
    """Report sourced PvE patch parameters; leave PvP and unknowns uncalibrated."""
    if not isinstance(perk, str) or not perk.strip():
        raise ValueError("perk must be nonempty")
    if activity not in ("pve", "pvp", "competitive", "trials"):
        raise ValueError("activity must be explicit")
    if type(enhanced) is not bool:
        raise ValueError("enhanced must be boolean")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version must be nonempty")
    name = perk.strip().casefold().replace(" ", "_")
    base = {
        "perk": name, "activity": activity, "enhanced": enhanced,
        "source_url": SOURCE_URL, "source_date": SOURCE_DATE,
        "source_patch_version": PATCH_VERSION,
        "evidence_grade": "official_historical_patch_parameter",
        "gameplay_measured": False, "current_game_verified": False,
        "current_roll_certified": False, "enhanced_roll_certified": False,
        "artifact_legality_certified": False,
        "absolute_damage": None, "boss_dps": None, "guardian_ttk": None,
        "bonus_fraction": None, "prior_bonus_fraction": None,
        "bonus_scope": None, "activation": None,
    }
    rule = _PATCH_RULES.get(name)
    if rule is None:
        return {**base, "status": "unsupported_perk"}
    if source_patch_version.strip() != PATCH_VERSION:
        return {**base, "status": "source_patch_version_mismatch"}
    if activity != "pve":
        return {**base, "status": "pvp_not_independently_calibrated"}
    if enhanced and "enhanced_bonus" not in rule:
        return {**base, "status": "enhanced_variant_not_sourced",
                "bonus_scope": rule["bonus_scope"]}
    return {
        **base, "status": "historical_pve_patch_parameter_only",
        "bonus_fraction": (rule["enhanced_bonus"] if enhanced
                           else rule["standard_bonus"]),
        "prior_bonus_fraction": (rule["prior_enhanced_bonus"] if enhanced
                                 else rule["prior_bonus"]),
        "bonus_scope": rule["bonus_scope"],
        "activation": dict(rule["activation"]),
        "interpretation": ("Patch-relative conditional parameter, not an "
                           "always-active total damage multiplier or a "
                           "currently certified weapon roll."),
    }


def attrition_orbs_patch_hit_count(weapon_family, *, activity,
                                   source_patch_version=PATCH_VERSION):
    """Historical activation hit count, never an observed orb generation rate."""
    if not isinstance(weapon_family, str) or not weapon_family.strip():
        raise ValueError("weapon_family must be nonempty")
    if activity not in ("pve", "pvp", "competitive", "trials"):
        raise ValueError("activity must be explicit")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version must be nonempty")
    family = weapon_family.strip().casefold()
    base = {"weapon_family": family, "activity": activity,
            "source_url": SOURCE_URL, "source_date": SOURCE_DATE,
            "source_patch_version": PATCH_VERSION,
            "gameplay_measured": False, "current_game_verified": False,
            "current_roll_certified": False, "hits_to_activate": None,
            "prior_hits_to_activate": None, "orb_rate_measured": None}
    if family not in _ORB_HITS:
        return {**base, "status": "unsupported_family"}
    if source_patch_version.strip() != PATCH_VERSION:
        return {**base, "status": "source_patch_version_mismatch"}
    if activity != "pve":
        return {**base, "status": "pvp_not_independently_calibrated"}
    now, prior = _ORB_HITS[family]
    return {**base, "status": "historical_pve_patch_hit_threshold_only",
            "hits_to_activate": now, "prior_hits_to_activate": prior,
            "limitations": "Hit counts do not certify actual hits, orbs, ownership, cooldown, weapon rolls or Artifact effects."}
