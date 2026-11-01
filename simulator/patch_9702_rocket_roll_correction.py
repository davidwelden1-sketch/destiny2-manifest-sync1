"""Conservative official 9.7.0.2 weapon-roll correction evidence.

Official Bungie source, 2026-06-23:
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2

This module identifies *family-level* historical roll corrections. It does
not infer item hashes, manifest socket paths, enhanced perks, present-day
acquisition, or gameplay damage from a weapon-family patch note.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 23)
PATCH_VERSION = "9.7.0.2"
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"
ORIGINS = frozenset(("europa", "moon"))
PERKS = frozenset(("Lead from Gold", "Impromptu Ammunition"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))


def review_rocket_roll_correction(*, origin, perk, observation_date,
                                  activity="pve", source_patch_version=PATCH_VERSION):
    """Triage a *named-family* roll claim, never certify an exact item roll.

    Bungie corrected Europa and Moon Rocket Launchers that could drop with
    Lead from Gold, a perk reserved for Special-ammo weapons, by updating
    affected instances to Impromptu Ammunition. The patch does not list exact
    weapon hashes or which historical variant sockets were affected.
    """
    if not isinstance(origin, str) or origin not in ORIGINS:
        raise ValueError("origin must be europa or moon")
    if not isinstance(perk, str) or perk not in PERKS:
        raise ValueError("unsupported perk")
    if not isinstance(activity, str) or activity not in ACTIVITIES:
        raise ValueError("unsupported activity")
    if not isinstance(source_patch_version, str) or not source_patch_version.strip():
        raise ValueError("source_patch_version required")
    if not isinstance(observation_date, str):
        raise ValueError("observation_date must be canonical ISO date")
    try:
        day = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("invalid observation_date") from exc
    if day.isoformat() != observation_date:
        raise ValueError("observation_date must be canonical ISO date")

    if source_patch_version != PATCH_VERSION:
        status = "source_patch_version_mismatch"
    elif day < PATCH_DATE:
        status = "pre_patch_roll_observation_requires_versioned_review"
    elif day == PATCH_DATE:
        status = "patch_day_deployment_time_unknown"
    elif perk == "Lead from Gold":
        status = "official_historical_unintended_drop_corrected"
    else:
        status = "official_historical_replacement_named"

    return {
        "origin": origin,
        "weapon_family": "Rocket Launcher",
        "perk": perk,
        "activity": activity,
        "status": status,
        "patch_version": PATCH_VERSION,
        "patch_date": PATCH_DATE.isoformat(),
        "source_url": SOURCE_URL,
        "evidence_grade": "official_historical_family_level_not_manifest_hash",
        "official_intended_replacement": "Impromptu Ammunition",
        "lead_from_gold_reserved_for": "Special ammo weapons",
        "exact_item_hash": None,
        "affected_socket_index": None,
        "current_manifest_version": None,
        "current_manifest_socket_verified": False,
        "current_drop_observed": False,
        "current_obtainability": "unverified",
        "enhanced_perk_legality": "unverified",
        "artifact_effects_enabled": False if activity in ("competitive", "trials") else None,
        "gameplay_measured": False,
        "boss_dps": None,
        "guardian_ttk": None,
    }
