"""Data contracts for sourced Destiny 2 sandbox measurements."""
from dataclasses import dataclass
from datetime import datetime
from math import isfinite

ALLOWED = {"official", "measured", "estimated", "hypothetical"}

@dataclass(frozen=True)
class Evidence:
    source_url: str
    observed_at: str
    status: str
    context: str

    def __post_init__(self):
        if self.status not in ALLOWED:
            raise ValueError("Unsupported evidence classification")
        if not self.source_url.startswith(("https://", "http://")):
            raise ValueError("Source URL required")
        if not self.context.strip():
            raise ValueError("Measurement context required")
        datetime.fromisoformat(self.observed_at.replace("Z", "+00:00"))

@dataclass(frozen=True)
class DamageObservation:
    weapon_hash: int
    precision: float
    body: float
    activity: str
    evidence: Evidence

    def __post_init__(self):
        if self.weapon_hash <= 0 or not self.activity.strip():
            raise ValueError("Weapon and activity required")
        if not all(isfinite(x) and x > 0 for x in (self.precision, self.body)):
            raise ValueError("Finite positive damage required")

    @property
    def certified(self):
        return self.evidence.status in {"official", "measured"}
