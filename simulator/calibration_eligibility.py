"""Gate measurement summaries against explicit review metadata and sandbox version.

This does not assert that a reviewed source is factually correct.
"""
from datetime import date
from simulator.source_freshness import source_suitability

def calibration_eligibility(summary, review, *, current_game_version, as_of):
    if not isinstance(summary, dict) or not isinstance(review, dict):
        raise TypeError("summary and review must be mappings")
    if not isinstance(current_game_version, str) or not current_game_version:
        raise ValueError("current game version required")
    if summary.get("status") != "reported_measurements_not_independently_verified":
        return {"eligible": False, "reason": "not_a_measurement_summary"}
    context = summary.get("context")
    if not isinstance(context, dict) or context.get("game_version") != current_game_version:
        return {"eligible": False, "reason": "sandbox_version_mismatch"}
    if not summary.get("source_urls"):
        return {"eligible": False, "reason": "missing_provenance"}
    if not isinstance(review.get("source_urls"), list) or not set(summary["source_urls"]).issubset(set(review["source_urls"])):
        return {"eligible": False, "reason": "source_review_mismatch"}
    if review.get("reuse_permission_confirmed") is not True:
        return {"eligible": False, "reason": "reuse_permission_unconfirmed"}
    suitability = source_suitability(review, as_of)
    if not suitability["usable_for_current_calibration"]:
        return {"eligible": False, "reason": suitability["reason"]}
    if review.get("game_version") != current_game_version:
        return {"eligible": False, "reason": "review_version_mismatch"}
    if summary.get("count", 0) < 3:
        return {"eligible": False, "reason": "insufficient_samples"}
    return {"eligible": True, "reason": "metadata_eligible_not_gameplay_certified",
            "certified_build": False, "independently_reproduced": False}
