"""Artifact-first candidate screening, not full build validation."""

RESTRICTED = {"competitive", "competitive crucible", "glory", "glory playlist", "trials", "trials of osiris"}
CLASSES = {"hunter", "titan", "warlock"}

def screen_candidate(character_class, activity, artifact_perks, allowed_perks, max_selected=7):
    if not isinstance(character_class, str) or character_class.lower() not in CLASSES:
        raise ValueError("unknown class")
    if not isinstance(activity, str) or not activity.strip():
        raise ValueError("activity required")
    if not isinstance(artifact_perks, (list, tuple, set, frozenset)) or not isinstance(allowed_perks, (list, tuple, set, frozenset)):
        raise TypeError("perk pools must be collections")
    if not isinstance(max_selected, int) or max_selected < 0:
        raise ValueError("invalid selection limit")
    if len(artifact_perks) != len(set(artifact_perks)):
        return {"eligible": False, "reason": "duplicate_perks"}
    if len(artifact_perks) > max_selected:
        return {"eligible": False, "reason": "artifact_limit"}
    if not set(artifact_perks).issubset(set(allowed_perks)):
        return {"eligible": False, "reason": "perk_not_in_active_artifact"}
    if activity.lower().strip() in RESTRICTED and artifact_perks:
        return {"eligible": False, "reason": "artifact_disabled_activity"}
    return {"eligible": True, "reason": "preliminary_screen_only",
            "certified_build": False}

def screen_one_active_artifact(character_class, activity, artifact_id,
                               selected_perks, artifact_catalog, max_selected=7):
    """Reject cross-Artifact perk mixes using one explicitly selected catalog entry.

    Catalog provenance must be checked separately against current game data.
    """
    if not isinstance(artifact_catalog, dict):
        raise TypeError("artifact_catalog must be a mapping")
    if not isinstance(artifact_id, str) or not artifact_id.strip():
        return {"eligible": False, "reason": "artifact_id_required"}
    if artifact_id not in artifact_catalog:
        return {"eligible": False, "reason": "artifact_not_in_catalog"}
    result = screen_candidate(character_class, activity, selected_perks,
                              artifact_catalog[artifact_id], max_selected)
    if result["eligible"]:
        result["reason"] = "single_artifact_preliminary_screen_only"
        result["catalog_independently_verified"] = False
    return result
