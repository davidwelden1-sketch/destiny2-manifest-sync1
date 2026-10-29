"""Deterministic PvP weapon TTK calculations. All damage inputs must be sourced separately."""
from dataclasses import dataclass
from math import ceil, isfinite

@dataclass(frozen=True)
class WeaponProfile:
    rpm: float
    precision_damage: float
    body_damage: float
    first_shot_delay: float = 0.0

    def __post_init__(self):
        if not all(isfinite(v) and v > 0 for v in (self.rpm, self.precision_damage, self.body_damage)):
            raise ValueError("RPM and damage must be positive")
        if not isfinite(self.first_shot_delay) or self.first_shot_delay < 0:
            raise ValueError("First shot delay cannot be negative")

def shots_to_kill(health: float, damage: float) -> int:
    if not all(isfinite(v) and v > 0 for v in (health, damage)):
        raise ValueError("Health and damage must be positive")
    # Avoid floating-point rounding near an exact threshold.
    return max(1, ceil((health - 1e-9) / damage))

def ttk_seconds(rpm: float, shots: int, first_shot_delay: float = 0.0) -> float:
    if not all(isfinite(v) for v in (rpm, first_shot_delay)) or rpm <= 0 or shots < 1 or first_shot_delay < 0:
        raise ValueError("Invalid firing inputs")
    return first_shot_delay + (shots - 1) * 60.0 / rpm

def optimal_ttk(profile: WeaponProfile, health: float, multiplier: float = 1.0) -> dict:
    if not isfinite(multiplier) or multiplier <= 0:
        raise ValueError("Damage multiplier must be positive")
    shots = shots_to_kill(health, profile.precision_damage * multiplier)
    return {"shots": shots, "ttk_seconds": ttk_seconds(profile.rpm, shots, profile.first_shot_delay),
            "precision_damage_after_multiplier": profile.precision_damage * multiplier,
            "model": "constant-rate, instant-hit, first-shot-at-t0; no burst cadence or travel time",
            "verified_in_game": False}

def minimum_precision_hits(profile: WeaponProfile, health: float, total_shots: int,
                           multiplier: float = 1.0) -> int | None:
    """Minimum precision hits among exactly total_shots fired, assuming uniform multiplier."""
    if not all(isfinite(v) for v in (health, multiplier)) or health <= 0 or total_shots < 1 or multiplier <= 0:
        raise ValueError("Invalid inputs")
    precision = profile.precision_damage * multiplier
    body = profile.body_damage * multiplier
    if precision < body:
        raise ValueError("Precision damage cannot be below body damage in this model")
    for crits in range(total_shots + 1):
        if crits * precision + (total_shots - crits) * body + 1e-9 >= health:
            return crits
    return None
