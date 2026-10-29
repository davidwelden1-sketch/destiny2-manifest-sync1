"""Fail-closed source-backed candidate interval ingestion.

Input JSON schema: {"game_version":"...", "source_reviews":{id: review},
"candidates":[{"id":"...", "class":"hunter", "artifact_perks":["..."],
"artifact_reviewed":true, "metrics": {"damage":{"low":0.3,"high":0.5,
"source_ids":["id"]}, ...}}]}.
This is an evidence-routing stage, NOT independent verification of gameplay.
"""
import json
from pathlib import Path
from simulator.sensitivity_search import robust_rank

METRICS = ("damage", "survivability", "uptime")

def evaluate_sourced_candidates(document, weights, current_game_version):
    if not isinstance(document, dict) or document.get("game_version") != current_game_version:
        return {"ranked": [], "rejected": [{"reason": "version_mismatch"}], "certified_builds": 0}
    reviews = document.get("source_reviews", {})
    ranked_input, rejected = [], []
    for c in document.get("candidates", []):
        if not isinstance(c, dict):
            rejected.append({"reason": "invalid_candidate"})
            continue
        reason = None
        if c.get("artifact_reviewed") is not True or not c.get("artifact_perks"):
            reason = "artifact_evidence_missing"
        ranges = {}
        if not reason:
            for metric in METRICS:
                record = c.get("metrics", {}).get(metric, {})
                ids = record.get("source_ids", [])
                if not isinstance(ids, list) or not ids:
                    reason = "missing_metric_sources"
                    break
                for sid in ids:
                    review = reviews.get(sid, {})
                    if (review.get("game_version") != current_game_version
                        or review.get("independent_review_complete") is not True
                        or review.get("reuse_permission_confirmed") is not True
                        or review.get("explicitly_outdated") is True
                        or review.get("explicitly_outdated_for_current_calibration") is True):
                        reason = "unapproved_metric_source"
                        break
                if reason:
                    break
                ranges[metric] = (record.get("low"), record.get("high"))
        if reason:
            rejected.append({"id": c.get("id"), "reason": reason})
        else:
            ranked_input.append({"id": c.get("id"), "class": c.get("class"),
                                 "artifact_perks": c["artifact_perks"],
                                 "metric_ranges": ranges})
    ranked = robust_rank(ranked_input, weights)
    included = {r["id"] for r in ranked}
    for c in ranked_input:
        if c["id"] not in included:
            rejected.append({"id": c["id"], "reason": "invalid_metric_range_or_class"})
    return {"ranked": ranked, "rejected": rejected, "certified_builds": 0,
            "status": "metadata_screened_predictions_not_gameplay_certified"}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--game-version", required=True)
    args = parser.parse_args()
    doc = json.loads(args.input_json.read_text(encoding="utf-8"))
    weights = {k: 1 for k in METRICS}
    print(json.dumps(evaluate_sourced_candidates(doc, weights, args.game_version), indent=2))

if __name__ == "__main__":
    main()
