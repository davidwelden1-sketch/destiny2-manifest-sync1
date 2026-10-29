"""Conservative source coverage audit for activity-scoped measurements."""
from collections import defaultdict
from simulator.measurements import SandboxMeasurement

def coverage_report(measurements):
    groups = defaultdict(lambda: {"total": 0, "official": 0, "measured": 0,
                                  "estimated": 0, "hypothetical": 0, "item_hashes": set()})
    for row in measurements:
        if not isinstance(row, SandboxMeasurement):
            raise TypeError("Expected SandboxMeasurement")
        key = (row.context.activity, row.context.mode, row.metric,
               row.context.sandbox_version, row.context.artifact_enabled)
        bucket = groups[key]
        bucket["total"] += 1
        bucket[row.evidence_status] += 1
        bucket["item_hashes"].add(row.item_hash)
    result = []
    for key in sorted(groups, key=str):
        bucket = groups[key]
        result.append({"activity": key[0], "mode": key[1], "metric": key[2],
                       "sandbox_version": key[3], "artifact_enabled": key[4],
                       "total": bucket["total"], "unique_items": len(bucket["item_hashes"]),
                       "verified_source_records": bucket["official"] + bucket["measured"],
                       "estimated_records": bucket["estimated"],
                       "hypothetical_records": bucket["hypothetical"]})
    return result
