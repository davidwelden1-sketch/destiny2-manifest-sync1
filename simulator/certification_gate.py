"""Fail-closed evidence gates for the four Build Lab phases.

A passing unit test is not measured gameplay evidence.
"""
REQUIRED = {
  1: ("manifest", "exact_hash", "active_frame", "legal_traits", "obtainability", "enhancement"),
  2: ("damage", "stacking", "attribution", "cooldowns", "resistance", "ttk", "calibration"),
  3: ("hunter", "titan", "warlock", "artifact", "activation", "comparison"),
  4: ("loadout", "mods", "rotation", "provenance", "validation"),
}

def phase_status(phase, evidence):
    """Return explicit gaps; never infer verified status from missing fields."""
    if phase not in REQUIRED:
        raise ValueError("unknown phase")
    if not isinstance(evidence, dict):
        raise TypeError("evidence must be a dict")
    gaps = tuple(k for k in REQUIRED[phase] if evidence.get(k) != "verified")
    return {"complete": not gaps, "gaps": gaps}

def build_certified(phases, activity, artifact_selected=False):
    """Public fail-closed certification entry point; legacy strings never certify.

    The old status-only implementation could approve a build based solely on
    user-supplied 'verified' strings. Route all certification through sourced
    evidence records instead.
    """
    return build_certified_with_sources(phases, activity, artifact_selected)


def build_certified_with_sources(phases, activity, artifact_selected=False):
    """Require sourced evidence for every phase, not just status strings.

    Structural source checks cannot prove the source's factual accuracy.
    """
    from simulator.source_evidence import sourced_phase_status
    if not isinstance(phases, dict):
        raise TypeError("phases must be a dict")
    if not isinstance(activity, str) or not activity.strip():
        raise ValueError("activity required")
    if activity.strip().lower() in {"trials", "trials of osiris", "competitive"} and artifact_selected:
        return False
    return all(
        p in phases and not sourced_phase_status(p, phases[p])["gaps"]
        for p in REQUIRED
    )
