"""Bungie 9.7.0 Hunter aspect class-ability ownership, not gameplay certification.

The source says Trapper's Ambush now spends class-ability energy, while
Trapper's Ambush, Ascension and Ensnaring Slam count as class abilities.
That does NOT independently verify any individual perk's proc, final-blow
attribution, Guardian damage, damage resistance, or ability cooldown.
"""
from datetime import date

PATCH_VERSION = "9.7.0"
PATCH_DATE = date(2026, 6, 9)
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_CHECKED_AT = "2026-11-02"
ASPECTS = {
    "trappers_ambush": {"energy_pool": "class_ability", "scales_above_100": True},
    "ascension": {"energy_pool": None, "scales_above_100": True},
    "ensnaring_slam": {"energy_pool": None, "scales_above_100": False},
}
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
EVENTS = frozenset(("aspect_activation", "aspect_damage", "aspect_final_blow",
                    "weapon_final_blow"))


def assess_class_ability_ownership(*, aspect, guardian_class, activity,
                                   observation_date, event_kind,
                                   class_stat=None, manifest_version=None,
                                   artifact_name=None, artifact_perks=()):
    """Classify only Bungie's published source category and uncertainty gates."""
    if type(aspect) is not str or aspect not in ASPECTS:
        raise ValueError("Unknown aspect")
    if guardian_class not in ("hunter", "titan", "warlock"):
        raise ValueError("Unknown class")
    if activity not in ACTIVITIES or event_kind not in EVENTS:
        raise ValueError("Unknown activity or event")
    if type(observation_date) is not str:
        raise ValueError("Canonical ISO observation date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date:
        raise ValueError("Canonical ISO observation date required")
    if class_stat is not None and (type(class_stat) is not int or
                                   not 0 <= class_stat <= 200):
        raise ValueError("Class stat must be an integer in 0..200")
    if manifest_version is not None and (type(manifest_version) is not str or
                                          not manifest_version.strip()):
        raise ValueError("Invalid manifest version")
    if artifact_name is not None and (type(artifact_name) is not str or
                                      not artifact_name.strip()):
        raise ValueError("Invalid Artifact name")
    if type(artifact_perks) not in (tuple, list) or len(artifact_perks) > 7:
        raise ValueError("At most seven Artifact perks")
    if any(type(p) is not str or not p.strip() for p in artifact_perks):
        raise ValueError("Invalid Artifact perk")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Duplicate Artifact perks")
    if artifact_perks and artifact_name is None:
        raise ValueError("Artifact perks require one named Artifact")

    scoped = guardian_class == "hunter" and observed >= PATCH_DATE
    aspect_event = event_kind.startswith("aspect_")
    rule = ASPECTS[aspect]
    scaling = (class_stat > 100 if class_stat is not None else None)
    return {
        "id": f"d2:patch-rule:970:class-ability-ownership:{aspect}",
        "guardian_class": guardian_class,
        "activity": activity,
        "event_kind": event_kind,
        "observation_date": observation_date,
        "patch_version": PATCH_VERSION,
        "patch_date": PATCH_DATE.isoformat(),
        "source_url": SOURCE_URL,
        "source_checked_at": SOURCE_CHECKED_AT,
        "manifest_version": manifest_version,
        "evidence_grade": ("official_historical_patch_not_live_measured"
                           if scoped else "out_of_scope_or_pre_patch_unverified"),
        "post_patch_class_scope": scoped,
        "event_source_classification": (
            "class_ability" if scoped and aspect_event else
            "weapon" if scoped and not aspect_event else None),
        "class_ability_energy_pool_official": (
            "class_ability" if scoped and aspect == "trappers_ambush" else None),
        "above_100_class_stat_scaling_described": (
            scaling if scoped and rule["scales_above_100"] else None),
        "individual_perk_proc_verified": False,
        "final_blow_attribution_verified": False,
        "current_aspect_equipment_verified": False,
        "current_artifact_allocation_verified": False,
        "artifact_name": artifact_name,
        "selected_artifact_perks": tuple(artifact_perks),
        "artifact_effects_active": False if activity in ("competitive", "trials") else None,
        "measured_pve_dps": None,
        "measured_pve_damage_resistance": None,
        "measured_pvp_ttk": None,
        "measured_ability_cooldown": None,
        "current_runtime_verified": False,
    }
