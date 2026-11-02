"""Historical 9.7.0 ability-rule conditions; not a live damage/uptime simulator."""
from decimal import Decimal, InvalidOperation

ARC_SOUL_MAX_ACQUISITION_M = Decimal("24")
ARC_SOUL_PREVIOUS_MAX_ACQUISITION_M = Decimal("30")


def offensive_bulwark_energy_trigger(void_overshield_active: bool, final_blow: bool):
    """Return conditionally eligible energy types; amounts are intentionally unknown."""
    if not isinstance(void_overshield_active, bool) or not isinstance(final_blow, bool):
        raise TypeError("Conditions must be explicit booleans")
    if not (void_overshield_active and final_blow):
        return ()
    return ("grenade", "melee")


def arc_soul_acquisition_zone(distance_metres):
    """Classify distance without inventing exact boundary or tracking behaviour."""
    if isinstance(distance_metres, bool):
        raise ValueError("Distance must be a nonnegative finite number")
    try:
        distance = Decimal(str(distance_metres))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Distance must be a nonnegative finite number") from None
    if not distance.is_finite() or distance < 0:
        raise ValueError("Distance must be a nonnegative finite number")
    if distance < ARC_SOUL_MAX_ACQUISITION_M:
        return "within_published_max"
    if distance > ARC_SOUL_MAX_ACQUISITION_M:
        return "beyond_published_max"
    return "boundary_unverified"
