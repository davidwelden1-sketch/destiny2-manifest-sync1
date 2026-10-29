"""Offline scenario sensitivity search for hypothetical Artifact-first candidates.

The ranges below are synthetic normalized scores, not in-game damage,
and must never be reported as certified or measured build performance.
"""
from simulator.candidate_comparison import compare_candidates

def robust_rank(candidates, weights):
    if not isinstance(candidates, (list, tuple)):
        raise TypeError("candidates must be a sequence")
    prepared = []
    for c in candidates:
        if not isinstance(c, dict) or not c.get("artifact_perks"):
            continue
        ranges = c.get("metric_ranges")
        if not isinstance(ranges, dict) or set(ranges) != {"damage", "survivability", "uptime"}:
            continue
        try:
            lows = {k: ranges[k][0] for k in ranges}
            highs = {k: ranges[k][1] for k in ranges}
            if any(type(lows[k]) not in (int, float) or type(highs[k]) not in (int, float)
                   or not 0 <= lows[k] <= highs[k] <= 1 for k in ranges):
                continue
        except (TypeError, ValueError, IndexError, KeyError):
            continue
        prepared.append((c, lows, highs))
    results = []
    for c, low, high in prepared:
        low_scores = compare_candidates([{"id": c.get("id"), "class": c.get("class"),
            "legal": True, "artifact_checked": True, "metrics": low}], weights)
        high_scores = compare_candidates([{"id": c.get("id"), "class": c.get("class"),
            "legal": True, "artifact_checked": True, "metrics": high}], weights)
        if not low_scores or not high_scores:
            continue
        results.append({"id": c.get("id"), "class": c["class"],
                        "artifact_perks": c["artifact_perks"],
                        "worst_case_score": low_scores[0]["score"],
                        "best_case_score": high_scores[0]["score"],
                        "certified_build": False, "data_type": "synthetic_sensitivity_only"})
    return sorted(results, key=lambda x: (-x["worst_case_score"], -x["best_case_score"], str(x["id"])))
