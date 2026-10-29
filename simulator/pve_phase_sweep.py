"""PvE damage-phase and ability-uptime scenario sweep.

Purely synthetic inputs: not actual weapon DPS, ability cooldowns or
verified live-game buff stacking.
"""
import json
from math import isfinite
from pathlib import Path
from simulator.ability_timing import cooldown_seconds, uptime_fraction

ROOT = Path(__file__).resolve().parents[1]

def run_pve_sweep(base_dps=(1000, 2000), phase_seconds=(15, 30, 45),
                  damage_multiplier=(1.0, 1.25), ability_cycle=(20, 40),
                  ability_duration=10):
    for sequence in (base_dps, phase_seconds, damage_multiplier, ability_cycle):
        if not sequence or any(type(x) not in (int, float) or not isfinite(x) or x <= 0 for x in sequence):
            raise ValueError("all scenario inputs must be positive finite numbers")
    if type(ability_duration) not in (int, float) or not isfinite(ability_duration) or ability_duration <= 0:
        raise ValueError("ability duration must be positive finite")
    rows = []
    for dps in base_dps:
        for phase in phase_seconds:
            for multiplier in damage_multiplier:
                for cycle in ability_cycle:
                    uptime = uptime_fraction(ability_duration, cycle)["fraction"]
                    rows.append({"base_dps": dps, "phase_seconds": phase,
                        "hypothetical_multiplier": multiplier, "ability_cycle_seconds": cycle,
                        "ability_uptime_fraction": uptime,
                        "phase_damage_if_multiplier_always_active": round(dps * phase * multiplier, 4),
                        "phase_damage_if_multiplier_only_during_ability": round(dps * phase * (1 + (multiplier - 1) * uptime), 4),
                        "verified_in_game": False})
    return {"scenario_count": len(rows), "scenarios": rows,
        "status": "synthetic_pve_phase_model_no_measured_dps_or_verified_buff_rules"}

def main():
    report = run_pve_sweep()
    out = ROOT / "reports" / "pve_phase_sweep.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scenario_count": report["scenario_count"], "status": report["status"]}))

if __name__ == "__main__":
    main()
