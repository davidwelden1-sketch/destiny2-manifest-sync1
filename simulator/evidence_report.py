"""Classify simulation output without promoting estimates to measured facts."""
from collections import Counter

def evidence_summary(records):
    allowed = {"official", "measured", "estimated", "hypothetical"}
    counts = Counter()
    for record in records:
        status = record["evidence_status"]
        if status not in allowed:
            raise ValueError("Unknown evidence status")
        counts[status] += 1
    return {"total": sum(counts.values()), "counts": {k: counts[k] for k in sorted(allowed)},
            "verified_observations": counts["official"] + counts["measured"],
            "unverified_observations": counts["estimated"] + counts["hypothetical"]}
