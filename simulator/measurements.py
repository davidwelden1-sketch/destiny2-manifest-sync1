"""Activity-specific intake and validation for numerical sandbox observations."""
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from simulator.activity import ActivityContext

@dataclass(frozen=True)
class SandboxMeasurement:
    item_hash: int
    metric: str
    value: float
    unit: str
    context: ActivityContext
    source_url: str
    observed_at: str
    evidence_status: str
    conditions: str

    def __post_init__(self):
        if self.item_hash <= 0 or not self.metric.strip() or not self.unit.strip():
            raise ValueError("Item, metric and unit are required")
        if not isfinite(self.value):
            raise ValueError("Measurement must be finite")
        if not self.source_url.startswith(("https://", "http://")):
            raise ValueError("Source URL required")
        if not self.conditions.strip():
            raise ValueError("Measurement conditions required")
        if self.evidence_status not in {"official", "measured", "estimated", "hypothetical"}:
            raise ValueError("Unknown evidence status")
        datetime.fromisoformat(self.observed_at.replace("Z", "+00:00"))

def group_by_activity(measurements):
    result = {"pve": [], "pvp": []}
    for measurement in measurements:
        result[measurement.context.activity].append(measurement)
    return result
