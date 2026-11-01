"""Source-gated 9.7.0.2 rocket launcher roll correction.

Bungie reports Europa/Moon rocket launchers unintentionally dropped with
Lead from Gold, and says instances were updated to Impromptu Ammunition.
This does not certify exact item hashes, enhanced rolls, acquisition or damage.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 23)
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"
SOURCE_CHECKED_AT = "2026-11-01"
CLASSES = frozenset(("hunter", "titan", "warlock"))
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
DESTINATIONS = frozenset(("europa", "moon", "other", "unknown"))


def assess_rocket_roll_patch(*, guardian_class, activity, observation_date,
                             destination, weapon_type, perk_name,
                             item_hash=None, manifest_version=None,
                             artifact_name=None, artifact_perks=()):
    """Narrow official negative roll rule; no positive current-roll claim."""
    if guardian_class not in CLASSES or activity not in ACTIVITIES:
        raise ValueError("Unknown class or activity")
    if type(observation_date) is not str:
        raise ValueError("Canonical ISO observation date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical ISO observation date required")
    if destination not in DESTINATIONS:
        raise ValueError("Unknown destination")
    if type(weapon_type) is not str or not weapon_type.strip():
        raise ValueError("Weapon type must be nonempty")
    if type(perk_name) is not str or not perk_name.strip():
        raise ValueError("Perk name must be nonempty")
    if item_hash is not None and (type(item_hash) is not int or item_hash <= 0):
        raise ValueError("Exact item hash must be a positive integer")
    if manifest_version is not None and (type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Manifest version must be nonempty or None")
    if type(artifact_perks) not in (list, tuple) or len(artifact_perks) > 7:
        raise ValueError("At most seven perks from one Artifact")
    if any(type(p) is not str or not p.strip() for p in artifact_perks):
        raise ValueError("Artifact perks must be nonempty names")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Artifact perk selections must be unique")
    if artifact_name is not None and (type(artifact_name) is not str or not artifact_name.strip()):
        raise ValueError("Artifact name must be nonempty or None")
    if artifact_perks and artifact_name is None:
        raise ValueError("Selected perks require a named Artifact")

    in_scope = (observed >= PATCH_DATE and destination in ("europa", "moon")
                and weapon_type == "rocket_launcher")
    negative_lead_from_gold = in_scope and perk_name == "Lead from Gold"
    artifact_eligible = activity not in ("competitive", "trials")
    return {
        "id": "d2:patch-rule:9702:europa-moon-rocket-lead-from-gold",
        "guardian_class": guardian_class,
        "activity": activity,
        "observation_date": observation_date,
        "destination_reported_by_caller": destination,
        "weapon_type_reported_by_caller": weapon_type,
        "perk_name": perk_name,
        "item_hash_reported_by_caller": item_hash,
        "post_patch_scope": in_scope,
        "lead_from_gold_current_legality_supported": False if negative_lead_from_gold else None,
        "reported_replacement_perk": "Impromptu Ammunition" if negative_lead_from_gold else None,
        "replacement_on_this_exact_hash_verified": False,
        "current_acquisition_verified": False,
        "enhanced_perk_verified": False,
        "source_url": SOURCE_URL,
        "source_checked_at": SOURCE_CHECKED_AT,
        "patch_date": PATCH_DATE.isoformat(),
        "manifest_version": manifest_version,
        "evidence_grade": ("official_historical_patch_negative_roll_rule_not_live_verified"
                           if negative_lead_from_gold else "unresolved_no_positive_legality_claim"),
        "artifact_name": artifact_name,
        "selected_artifact_perks": tuple(artifact_perks),
        "artifact_mode_eligible": artifact_eligible,
        "artifact_effects_active": None if artifact_eligible else False,
        "artifact_allocation_legal_verified": False,
        "measured_pve_boss_dps": None,
        "measured_pvp_ttk": None,
        "measured_ammo_regeneration": None,
    }
