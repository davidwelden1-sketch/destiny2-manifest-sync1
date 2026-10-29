"""Evidence-gated evaluation of hypothetical damage observations."""
from simulator.evidence import DamageObservation
from simulator.ttk import WeaponProfile, optimal_ttk

def evaluate_observation(observation: DamageObservation, rpm: float, health: float,
                         multiplier: float = 1.0):
    if not isinstance(observation, DamageObservation):
        raise TypeError("Expected a sourced damage observation")
    profile = WeaponProfile(rpm=rpm, precision_damage=observation.precision,
                            body_damage=observation.body)
    result = optimal_ttk(profile, health, multiplier)
    result["weapon_hash"] = observation.weapon_hash
    result["source_url"] = observation.evidence.source_url
    result["evidence_status"] = observation.evidence.status
    result["evidence_context"] = observation.evidence.context
    result["observed_at"] = observation.evidence.observed_at
    # A sourced base damage measurement does not certify a simulated perk stack.
    result["verified_in_game"] = False
    return result
