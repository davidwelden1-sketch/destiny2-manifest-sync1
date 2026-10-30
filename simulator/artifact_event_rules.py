"""Historical Artifact event eligibility screens, not gameplay proc simulations.

Bungie Update 9.7.0 (2026-06-09), Slayer Baron Apothecary Satchel:
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
No proc probability, damage scalar, healing quantity, or current loadout
legality is inferred. PvE and PvP measurements must be calibrated separately.
"""
from simulator.artifact_screen import screen_one_active_artifact

SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_DATE = "2026-06-09"
ARTIFACT_ID = "Slayer Baron Apothecary Satchel"


def _screen(perk, activity, artifact_id, selected_perks, artifact_catalog, character_class):
    result = screen_one_active_artifact(
        character_class, activity, artifact_id, selected_perks, artifact_catalog
    )
    if not result["eligible"]:
        return {"status": "artifact_selection_blocked", "reason": result["reason"]}
    if artifact_id != ARTIFACT_ID:
        return {"status": "artifact_identity_mismatch", "reason": "different_artifact"}
    if perk not in selected_perks:
        return {"status": "perk_not_selected", "reason": "missing_required_perk"}
    return None


def kinetic_impacts_gl_screen(ammo_type, activity, artifact_id,
                              selected_perks, artifact_catalog, *, character_class="titan"):
    """Screen the *GL ammo-type* part of Kinetic Impacts, not its hit trigger.

    Heavy is a comparison baseline. Primary/Special GLs are supported by the
    June patch, but their shockwave damage is lower than Heavy GL shockwaves.
    """
    if not isinstance(ammo_type, str) or ammo_type.strip().lower() not in {
        "primary", "special", "heavy"
    }:
        raise ValueError("ammo_type must be primary, special, or heavy")
    blocked = _screen("Kinetic Impacts", activity, artifact_id,
                      selected_perks, artifact_catalog, character_class)
    if blocked:
        return {**blocked, "certified": False, "source_url": SOURCE_URL}
    ammo = ammo_type.strip().lower()
    return {
        "status": "official_historical_gl_ammo_eligibility",
        "ammo_type": ammo,
        "relative_shockwave_damage": (
            "lower_than_heavy_gl" if ammo != "heavy" else "heavy_gl_reference"
        ),
        "proc_condition": "not_established_by_this_screen",
        "damage_multiplier": None,
        "pve_damage_measured": False,
        "pvp_damage_measured": False,
        "current_artifact_verified": False,
        "certified": False,
        "source_url": SOURCE_URL,
        "source_date": SOURCE_DATE,
    }


def curative_orbs_tangle_screen(event, activity, artifact_id,
                               selected_perks, artifact_catalog, *, character_class="titan"):
    """Distinguish Tangle destruction from pickup without inventing healing."""
    if not isinstance(event, str) or not event.strip():
        raise ValueError("event must be a nonempty string")
    blocked = _screen("Curative Orbs", activity, artifact_id,
                      selected_perks, artifact_catalog)
    if blocked:
        return {**blocked, "certified": False, "source_url": SOURCE_URL}
    event = event.strip().lower()
    states = {
        "tangle_pickup": "explicitly_not_a_trigger",
        "tangle_destroy_shot": "official_historical_trigger",
        "tangle_destroy_impact": "official_historical_trigger",
    }
    return {
        "status": states.get(event, "event_not_established"),
        "event": event,
        "healing_amount": None,
        "pve_healing_measured": False,
        "pvp_healing_measured": False,
        "current_artifact_verified": False,
        "certified": False,
        "source_url": SOURCE_URL,
        "source_date": SOURCE_DATE,
    }
