"""Source-gated 9.7.0 weapon-family adjustments; arithmetic is NOT gameplay DPS/TTK.
Bungie, 2026-06-09: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
"""
from datetime import date
from decimal import Decimal

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
PATCH_DATE = date(2026, 6, 9)
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))

def _validate(activity, observation_date):
    if type(activity) is not str or activity not in ACTIVITIES:
        raise ValueError("Explicit supported activity required")
    if type(observation_date) is not str:
        raise ValueError("Canonical ISO date required")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid ISO date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("Canonical ISO date required")
    return day > PATCH_DATE

def rocket_pulse_patch(*, activity, target, observation_date):
    """Historical relative PvE adjustment only; not a measured current damage value."""
    after = _validate(activity, observation_date)
    if type(target) is not str or target not in ("base", "elite", "boss", "champion", "guardian"):
        raise ValueError("Explicit target category required")
    eligible = after and activity == "pve" and target != "guardian"
    multiplier = None
    if eligible:
        multiplier = Decimal("0.675") if target == "boss" else Decimal("0.90")
    return {
        "family": "rocket_pulse", "activity": activity, "target": target,
        "source_url": SOURCE_URL, "patch_version": "9.7.0",
        "evidence": "official_historical", "observation_date": observation_date,
        "historical_relative_damage_multiplier": str(multiplier) if multiplier is not None else None,
        "historical_general_special_elite_bonus_applies": False if eligible and target == "elite" else None,
        "combined_boss_adjustment_is_arithmetic": target == "boss" and eligible,
        "runtime_damage_verified": False, "current_manifest_weapon_hash_verified": False,
        "current_artifact_verified": False, "measured_boss_dps": None,
        "measured_guardian_ttk": None,
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "certified_for_app_build_recommendation": False,
    }

def adagio_patch(*, activity, weapon_family, observation_date):
    """Patch-described Adagio damage bonus, NOT a complete RPM/TTK or legal-roll model."""
    after = _validate(activity, observation_date)
    if type(weapon_family) is not str or weapon_family not in ("hand_cannon", "shotgun", "bow", "other"):
        raise ValueError("Explicit weapon family required")
    bonus = {"hand_cannon": 27, "shotgun": 30, "bow": 30}.get(weapon_family) if after else None
    return {
        "perk": "Adagio", "activity": activity, "weapon_family": weapon_family,
        "source_url": SOURCE_URL, "patch_version": "9.7.0",
        "evidence": "official_historical", "observation_date": observation_date,
        "published_damage_bonus_percent": bonus,
        "perk_active_verified": False, "current_weapon_perk_pool_verified": False,
        "enhanced_perk_eligibility_verified": False, "rpm_change_verified": False,
        "measured_guardian_ttk": None, "measured_boss_dps": None,
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "certified_for_app_build_recommendation": False,
    }
