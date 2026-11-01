"""Official 9.7.0 negative-proc evidence: Crossbow Charged Bolt kills vs Osteo catalyst.

This is a source-gated rule, not a measured gameplay simulation. Bungie fixed
Crossbow Charged Bolt kills incorrectly triggering the Osteo Striga catalyst.
No assumption is made about other Crossbow kills, damage, ammo, or subclass
interactions. PvE and PvP must be evaluated separately.
"""
from datetime import date

PATCH_DATE = date(2026, 6, 9)
SOURCE_URL = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
SOURCE_CHECKED_AT = "2026-11-01"
ACTIVITIES = frozenset(("pve", "pvp", "competitive", "trials"))
CLASSES = frozenset(("hunter", "titan", "warlock"))


def assess_crossbow_osteo_catalyst(*, guardian_class, activity,
                                  observation_date, kill_source,
                                  artifact_name=None, artifact_perks=(),
                                  manifest_version=None):
    """Grade the catalyst trigger, without inventing proc or damage numbers.

    For a post-patch Charged Bolt kill, the official fix contradicts the
    catalyst-trigger claim. All other kill sources are unresolved here.
    """
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
    if type(kill_source) is not str or not kill_source.strip():
        raise ValueError("Kill source must be nonempty")
    if type(artifact_perks) not in (list, tuple) or len(artifact_perks) > 7:
        raise ValueError("Select at most seven perks from one Artifact")
    if any(type(p) is not str or not p.strip() for p in artifact_perks):
        raise ValueError("Artifact perks must be nonempty names")
    if len(set(artifact_perks)) != len(artifact_perks):
        raise ValueError("Artifact perk selections must be unique")
    if artifact_name is not None and (
            type(artifact_name) is not str or not artifact_name.strip()):
        raise ValueError("Artifact name must be nonempty or None")
    if artifact_perks and artifact_name is None:
        raise ValueError("Selected perks require one named Artifact")
    if manifest_version is not None and (
            type(manifest_version) is not str or not manifest_version.strip()):
        raise ValueError("Manifest version must be nonempty or None")

    is_charged_bolt = kill_source == "crossbow_charged_bolts"
    post_patch = observed >= PATCH_DATE
    # False means the official patch explicitly excludes this proc; None
    # means this source does not certify a proc either way.
    proc_supported = False if is_charged_bolt and post_patch else None
    artifact_eligible = activity not in ("competitive", "trials")
    return {
        "guardian_class": guardian_class,
        "activity": activity,
        "kill_source": kill_source,
        "observation_date": observation_date,
        "patch_date": PATCH_DATE.isoformat(),
        "osteo_catalyst_trigger_supported": proc_supported,
        "evidence_grade": ("official_patch_negative_proc_rule_not_measured"
                           if proc_supported is False
                           else "unresolved_no_positive_proc_claim"),
        "source_url": SOURCE_URL,
        "source_checked_at": SOURCE_CHECKED_AT,
        "manifest_version": manifest_version,
        "artifact_name": artifact_name,
        "selected_artifact_perks": tuple(artifact_perks),
        "artifact_mode_eligible": artifact_eligible,
        "artifact_effects_active": None if artifact_eligible else False,
        "artifact_allocation_legal_verified": False,
        "exact_weapon_roll_verified": False,
        "measured_pve_boss_dps": None,
        "measured_pvp_ttk": None,
        "measured_kill_attribution": None,
        "measured_cooldown_seconds": None,
    }
