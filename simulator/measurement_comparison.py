"""Conservative comparison of independently supplied measurement summaries."""
from math import isfinite, sqrt

def compare_measurement_summaries(a, b):
    if not isinstance(a, dict) or not isinstance(b, dict):
        raise TypeError("summaries must be mappings")
    for key in ("game_version", "activity", "scenario", "metric", "unit"):
        if a.get("context", {}).get(key) != b.get("context", {}).get(key):
            raise ValueError("incompatible measurement context: " + key)
    for summary in (a, b):
        if summary.get("count", 0) < 2 or any(
            type(summary.get(k)) not in (float, int) or not isfinite(summary[k])
            for k in ("mean", "standard_error")
        ) or summary["standard_error"] < 0:
            raise ValueError("invalid summary")
    difference = a["mean"] - b["mean"]
    combined_se = sqrt(a["standard_error"]**2 + b["standard_error"]**2)
    return {"difference": difference, "combined_standard_error": combined_se,
            "signal_to_noise": abs(difference) / combined_se if combined_se else None,
            "statistical_significance_claim": False,
            "verified_in_game": False,
            "note": "Descriptive comparison only; independence, sample quality and confidence not established"}
