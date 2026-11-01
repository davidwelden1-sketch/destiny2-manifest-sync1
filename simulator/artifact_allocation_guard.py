"""Fail-closed structural checks for one active Destiny 2 Artifact allocation.

Bungie 9.7.0 (2026-06-09): Artifact effects disabled in Competitive/Trials.
Bungie 9.7.0.2 (2026-06-23): fixed an Artifact no-duplicates bypass.
Sources:
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2

This is NOT a current Artifact manifest, an unlock check, or a legal build
certificate. A caller-provided perk pool is not independent official evidence.
"""
MODES = frozenset(("pve", "pvp", "competitive", "trials"))
MAX_SELECTED_PERKS = 7


def audit_artifact_allocation(*, artifact_id, perk_ids, activity,
                              candidate_perk_pool=None):
    """Validate selection shape without inventing current perk availability."""
    if not isinstance(artifact_id, str) or not artifact_id.strip() or artifact_id != artifact_id.strip():
        raise ValueError("one nonempty, trimmed artifact ID is required")
    if not isinstance(activity, str) or activity not in MODES:
        raise ValueError("unsupported activity")
    if not isinstance(perk_ids, (list, tuple)):
        raise ValueError("perk_ids must be an ordered list or tuple")
    if any(not isinstance(p, str) or not p.strip() or p != p.strip()
           for p in perk_ids):
        raise ValueError("perk IDs must be nonempty trimmed strings")
    if candidate_perk_pool is not None:
        if not isinstance(candidate_perk_pool, (list, tuple, set, frozenset)):
            raise ValueError("candidate_perk_pool must be a collection")
        if any(not isinstance(p, str) or not p.strip() or p != p.strip()
               for p in candidate_perk_pool):
            raise ValueError("candidate perk IDs must be nonempty trimmed strings")

    normalized = [p.casefold() for p in perk_ids]
    duplicates = len(set(normalized)) != len(normalized)
    over_limit = len(perk_ids) > MAX_SELECTED_PERKS
    enabled = activity not in ("competitive", "trials")
    shape_valid = not duplicates and not over_limit and bool(perk_ids)
    pool_membership = None if candidate_perk_pool is None else (
        set(normalized).issubset({p.casefold() for p in candidate_perk_pool})
    )
    if not enabled:
        status = "artifact_effects_disabled_in_activity"
    elif not perk_ids:
        status = "empty_selection"
    elif duplicates:
        status = "duplicate_perks_rejected"
    elif over_limit:
        status = "over_seven_perks"
    elif pool_membership is False:
        status = "not_in_supplied_candidate_pool"
    elif pool_membership is True:
        status = "structural_only_supplied_pool_not_certified"
    else:
        status = "structural_only_current_pool_unknown"

    return {
        "artifact_id": artifact_id,
        "activity": activity,
        "selected_perk_count": len(perk_ids),
        "artifact_mode_eligible": enabled,
        "artifact_effects_active": None if enabled else False,
        "no_duplicates": not duplicates,
        "within_seven_perks": not over_limit,
        "structural_selection_valid": shape_valid,
        "candidate_pool_membership": pool_membership,
        "status": status,
        "evidence_grade": "structural_guard_not_current_manifest",
        "current_artifact_rotation_verified": False,
        "single_active_artifact_verified_in_game": False,
        "enhanced_weapon_roll_verified": False,
        "gameplay_measured": False,
        "source_urls": (
            "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0",
            "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2",
        ),
    }
