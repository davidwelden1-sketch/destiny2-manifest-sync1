"""Compare sourced PvP damage observations under explicit assumptions."""
from simulator.evaluate import evaluate_observation

def compare_observations(observations, rpm_by_hash, health, multiplier=1.0):
    results = []
    for observation in observations:
        rpm = rpm_by_hash.get(observation.weapon_hash)
        if rpm is None:
            continue
        row = evaluate_observation(observation, rpm, health, multiplier)
        row["activity"] = observation.activity
        results.append(row)
    return sorted(results, key=lambda r: (r["ttk_seconds"], r["shots"], r["weapon_hash"]))
