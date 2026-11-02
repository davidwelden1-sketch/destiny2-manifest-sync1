"""Deterministic PvP weapon TTK arithmetic. Damage and health must be sourced separately.

Exact decimal-rational comparisons prevent a tiny below-threshold damage value
from being rounded into an impossible two-tap or three-tap. This is a model,
not a claim of measured damage, legal rolls, or live-game TTK.
"""
from dataclasses import dataclass\nfrom decimal import Decimal, localcontext
from fractions import Fraction
from math import ceil, isfinite


def _positive_fraction(value, label):
    if type(value) not in (int, float) or not isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be positive and finite")
    # Decimal string conversion preserves the supplied measurement's stated
    # precision instead of injecting binary-float arithmetic at breakpoints.
    return Fraction(str(value))


@dataclass(frozen=True)
class WeaponProfile:
    rpm: float
    precision_damage: float
    body_damage: float
    first_shot_delay: float = 0.0

    def __post_init__(self):
        for name in ("rpm", "precision_damage", "body_damage"):
            _positive_fraction(getattr(self, name), name)
        delay = self.first_shot_delay
        if type(delay) not in (int, float) or not isfinite(delay) or delay < 0:
            raise ValueError("First shot delay cannot be negative or nonfinite")


def shots_to_kill(health: float, damage: float) -> int:
    """Ceiling of the exact ratio of caller-supplied decimal quantities."""
    return max(1, ceil(_positive_fraction(health, "health") /
                       _positive_fraction(damage, "damage")))


def ttk_seconds(rpm: float, shots: int, first_shot_delay: float = 0.0) -> float:
    _positive_fraction(rpm, "rpm")
    if type(shots) is not int or shots < 1:
        raise ValueError("shots must be a positive integer")
    if type(first_shot_delay) not in (int, float) or not isfinite(first_shot_delay) or first_shot_delay < 0:
        raise ValueError("First shot delay cannot be negative or nonfinite")
    result = first_shot_delay + (shots - 1) * 60.0 / rpm
    if not isfinite(result):
        raise ValueError("Calculated TTK is nonfinite")
    return result


def optimal_ttk(profile: WeaponProfile, health: float, multiplier: float = 1.0) -> dict:
    # Do not multiply binary floats before comparing damage to a health
    # threshold; even a sub-nanodamage discrepancy can flip the shot count.
    h = _positive_fraction(health, "health")
    precision = _positive_fraction(profile.precision_damage, "precision_damage")
    mult = _positive_fraction(multiplier, "multiplier")
    shots = max(1, ceil(h / (precision * mult)))
    # Each input is a Python float or integer rendered as a finite decimal.\n    # Fifty decimal digits exceed the product precision of two float reprs.\n    with localcontext() as ctx:\n        ctx.prec = 50\n        exact_display = format(Decimal(str(profile.precision_damage)) *\n                               Decimal(str(multiplier)), "f")\n    return {"shots": shots, "ttk_seconds": ttk_seconds(profile.rpm, shots, profile.first_shot_delay),
            "precision_damage_after_multiplier": profile.precision_damage * multiplier,\n            "precision_damage_after_multiplier_exact": exact_display,\n            "shot_breakpoint_uses_exact_decimal_fractions": True,
            "model": "constant-rate, instant-hit, first-shot-at-t0; no burst cadence or travel time",
            "verified_in_game": False}


def minimum_precision_hits(profile: WeaponProfile, health: float, total_shots: int,
                           multiplier: float = 1.0) -> int | None:
    """Minimum precision hits in exactly total_shots; caller-supplied inputs only."""
    if type(total_shots) is not int or total_shots < 1:
        raise ValueError("total_shots must be a positive integer")
    h = _positive_fraction(health, "health")
    mult = _positive_fraction(multiplier, "multiplier")
    precision = _positive_fraction(profile.precision_damage, "precision_damage") * mult
    body = _positive_fraction(profile.body_damage, "body_damage") * mult
    if precision < body:
        raise ValueError("Precision damage cannot be below body damage in this model")
    for crits in range(total_shots + 1):
        if crits * precision + (total_shots - crits) * body >= h:
            return crits
    return None
