"""Shield-aware PvE damage model for explicitly supplied DR fractions.

Frost Armor's DR applies to the Guardian and may affect shield damage,
but shield interaction is not yet independently measured: compare both
hypotheses rather than claiming stacking is established.
"""
from math import isfinite

def damage_through_layers(incoming, *, frost_dr, overshield_hp=45.0,
                          overshield_dr=0.70, frost_affects_shield=None):
    values = (incoming, frost_dr, overshield_hp, overshield_dr)
    if any(type(v) not in (int, float) or not isfinite(v) for v in values):
        raise ValueError("all values must be finite numbers")
    if incoming < 0 or overshield_hp < 0 or not 0 <= frost_dr < 1 or not 0 <= overshield_dr <= 1:
        raise ValueError("invalid damage or resistance")
    if type(frost_affects_shield) is not bool:
        raise ValueError("shield stacking hypothesis must be explicit")
    if not overshield_hp:
        return {"shield_hp_lost": 0.0, "health_damage": incoming * (1 - frost_dr),
                "hypothesis": "no_overshield", "verified_in_game": False}
    shield_multiplier = (1 - overshield_dr) * ((1 - frost_dr) if frost_affects_shield else 1)
    if shield_multiplier == 0:
        return {"shield_hp_lost": 0.0, "health_damage": 0.0,
                "hypothesis": "invulnerable_shield_limit", "verified_in_game": False}
    raw_absorbed = min(incoming, overshield_hp / shield_multiplier)
    shield_lost = raw_absorbed * shield_multiplier
    remaining = max(0.0, incoming - raw_absorbed)
    return {"shield_hp_lost": shield_lost, "health_damage": remaining * (1 - frost_dr),
            "hypothesis": "multiplicative_frost_on_shield" if frost_affects_shield else "shield_only_dr",
            "verified_in_game": False}

def stacking_hypotheses(incoming, *, frost_dr=0.35, overshield_hp=45.0, overshield_dr=0.70):
    return {"frost_on_shield": damage_through_layers(
                incoming, frost_dr=frost_dr, overshield_hp=overshield_hp,
                overshield_dr=overshield_dr, frost_affects_shield=True),
            "frost_not_on_shield": damage_through_layers(
                incoming, frost_dr=frost_dr, overshield_hp=overshield_hp,
                overshield_dr=overshield_dr, frost_affects_shield=False),
            "model_only": True, "stacking_not_verified": True}
