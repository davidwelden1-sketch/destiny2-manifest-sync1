"""Phase 3: conservative multi-objective candidate comparison.

Candidates are hypothetical model outputs, never certified builds.
The caller must provide normalized [0,1] metrics derived from a consistent
scenario. Missing metrics exclude a candidate rather than becoming zero.
"""
from math import isfinite

METRICS = ("damage", "survivability", "uptime")
CLASSES = {"hunter", "titan", "warlock"}

def compare_candidates(candidates, weights):
    if not isinstance(weights, dict) or set(weights) != set(METRICS):
        raise ValueError("all three objective weights required")
    if any(type(v) not in (float, int) or not isfinite(v) or v < 0 for v in weights.values()):
        raise ValueError("weights must be finite and nonnegative")
    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise ValueError("at least one weight must be positive")
    ranked = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        if candidate.get("class") not in CLASSES:
            continue
        if candidate.get("legal") is not True or candidate.get("artifact_checked") is not True:
            continue
        metrics = candidate.get("metrics")
        if not isinstance(metrics, dict) or any(
            type(metrics.get(k)) not in (float, int)
            or not isfinite(metrics[k]) or not 0 <= metrics[k] <= 1
            for k in METRICS
        ):
            continue
        score = sum(weights[k] * metrics[k] for k in METRICS) / total_weight
        ranked.append({"id": candidate.get("id"), "class": candidate["class"],
                       "score": score, "certified_build": False,
                       "status": "model_candidate_only"})
    return sorted(ranked, key=lambda row: (-row["score"], str(row["id"])))
