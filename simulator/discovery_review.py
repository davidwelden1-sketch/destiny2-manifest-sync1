"""Phase 5 discovery review queue: hypotheses, not certified discoveries."""
from math import isfinite

def review_queue(ranked, *, threshold=0.7):
    if type(threshold) not in (int, float) or not isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("threshold must be between zero and one")
    if not isinstance(ranked, (list, tuple)):
        raise TypeError("ranked candidates must be a sequence")
    queue = []
    for row in ranked:
        if not isinstance(row, dict) or row.get("certified_build") is not False:
            continue
        score = row.get("score")
        if type(score) not in (int, float) or not isfinite(score) or not 0 <= score <= 1:
            continue
        if score >= threshold:
            queue.append({"id": row.get("id"), "class": row.get("class"),
                          "score": score, "priority": "needs_controlled_testing",
                          "requirements": ["current_version", "source_provenance",
                                           "weapon_obtainability", "artifact_legality",
                                           "damage_and_stacking_measurements",
                                           "repeatability", "activity_context"],
                          "certified_build": False})
    return sorted(queue, key=lambda row: (-row["score"], str(row["id"])))
