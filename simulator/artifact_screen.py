"""Artifact-first candidate screening, not full build validation."""

RESTRICTED = {"competitive", "trials", "trials of osiris"}
CLASSES = {"hunter", "titan", "warlock"}

def screen_candidate(character_class, activity, artifact_perks, allowed_perks, max_selected=7):
    if character_class.lower() not in CLASSES:
        raise ValueError("unknown class")
    if not isinstance(activity, str) or not activity.strip():
        raise ValueError("activity required")
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
