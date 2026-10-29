"""Conservative weapon-stat scenario calculation.

Uses caller-supplied, source-attributed damage and RPM. A computed TTK is
not a measurement, and a third-party reference is not independently verified.
"""
from math import isfinite
from simulator.ttk import WeaponProfile, optimal_ttk, minimum_precision_hits

def evaluate_pvp_reference(reference, *, target_health):
    if not isinstance(reference, dict):
        raise TypeError("reference must be a mapping")
    required = ("weapon", "rpm", "precision_damage", "body_damage",
                "source_url", "game_version", "activity", "scenario")
    if any(not reference.get(key) for key in required):
        raise ValueError("missing source or weapon context")
    if reference["activity"] != "pvp":
        raise ValueError("PvP scenario required")
    if not isinstance(reference["source_url"], str) or not reference["source_url"].startswith("https://"):
        raise ValueError("HTTPS source required")
    if reference.get("explicitly_outdated") is True:
        raise ValueError("outdated source excluded")
    if any(type(reference[key]) not in (int, float) or not isfinite(reference[key]) or reference[key] <= 0
           for key in ("rpm", "precision_damage", "body_damage")):
        raise ValueError("invalid numerical inputs")
    profile = WeaponProfile(reference["rpm"], reference["precision_damage"],
                            reference["body_damage"])
    ttk = optimal_ttk(profile, target_health)
    return {"weapon": reference["weapon"], "game_version": reference["game_version"],
            "scenario": reference["scenario"], "source_url": reference["source_url"],
            "target_health": target_health, "optimal": ttk,
            "minimum_precision_hits": minimum_precision_hits(
                profile, target_health, ttk["shots"]),
            "measurement_imported": False, "certified_current": False,
            "status": "source_attributed_model_scenario"}
