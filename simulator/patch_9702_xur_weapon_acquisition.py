"""Historical, source-gated Xur weapon acquisition leads, not roll certification.

Bungie Update 9.7.0.2 (2026-06-23):
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2

The four named weapons may appear as direct Xur offers or in Strange
Engrams. They are un-tiered; patterns can be unlocked via Deepsight
Harmonizers. No exact item hash, class eligibility, currently obtainable
instance, enhanced perk pool or guaranteed purchase is established here.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 23)
PATCH_VERSION = "9.7.0.2"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"
WEAPONS = frozenset(("Imperial Decree", "Goldtusk", "Death's Razor", "Throne-Cleaver"))
CHANNELS = frozenset(("xur_direct_offer", "xur_strange_engram"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))


def review_xur_weapon_lead(*, weapon_name, channel, observation_date,
                           activity="pve", source_patch_version=PATCH_VERSION):
    """Return a conservative acquisition lead, never an obtainable-roll claim."""
    if not isinstance(weapon_name, str) or weapon_name not in WEAPONS:
        raise ValueError("weapon_name must be one of the four official names")
    if not isinstance(channel, str) or channel not in CHANNELS:
        raise ValueError("unsupported Xur acquisition channel")
    if not isinstance(activity, str) or activity not in ACTIVITIES:
        raise ValueError("unsupported activity")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version required")
    if not isinstance(observation_date, str):
        raise ValueError("observation_date must be ISO YYYY-MM-DD")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("invalid observation_date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("observation_date must be canonical ISO YYYY-MM-DD")

    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif day < PATCH_DATE:
        status = "pre_patch_acquisition_not_established"
    elif day == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    else:
        status = "official_historical_possible_acquisition_channel"

    return {
        "weapon_name": weapon_name,
        "channel": channel,
        "activity": activity,
        "status": status,
        "source_url": SOURCE_URL,
        "source_patch_version": PATCH_VERSION,
        "source_date": PATCH_DATE.isoformat(),
        "weapon_gear_tier": "un-tiered_in_official_patch",
        "deepsight_harmonizer_pattern_unlock": "officially_supported",
        "drop_guaranteed": False,
        "live_xur_inventory_checked": False,
        "current_acquisition_verified": False,
        "exact_item_hash": None,
        "current_manifest_socket_verified": False,
        "enhanced_perk_legality": "unverified",
        "class_eligibility": "unverified",
        "artifact_effects_active": False if activity in ("competitive", "trials") else None,
        "gameplay_measured": False,
        "pve_boss_dps": None,
        "pvp_guardian_ttk": None,
        "evidence_grade": "official_historical_acquisition_family_only",
    }
