"""Historical 9.7.0 Titan Exotic eligibility gates; no gameplay simulation claims."""
from decimal import Decimal, InvalidOperation

MAX_POINT_CONTACT_LIGHTNING_CHARGE_MULTIPLIER = Decimal("2")

def point_contact_charge_lightning_multiplier(value):
    """Reject unsupported numeric multipliers; this is a range guard, not a charge curve."""
    if isinstance(value, bool):
        raise ValueError("Multiplier must be a finite decimal")
    try:
        v = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Multiplier must be a finite decimal") from None
    if not v.is_finite() or not Decimal("1") <= v <= MAX_POINT_CONTACT_LIGHTNING_CHARGE_MULTIPLIER:
        raise ValueError("Multiplier outside published charge-only range")
    return v

def acd0_pvp_melee_damage_resistance_claim_allowed(against_player: bool):
    """Forbid carrying removed player-melee DR into PvP; PvE magnitude remains unknown."""
    if not isinstance(against_player, bool):
        raise TypeError("Mode target must be boolean")
    if against_player:
        return False
    return None
