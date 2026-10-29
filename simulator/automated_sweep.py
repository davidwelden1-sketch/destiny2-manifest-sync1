"""Automated regression scenario sweep using historical official patch inputs.

Outputs theoretical damage outcomes; neither current-game measurements
nor proof that Frost Armor applies to Void Overshield.
"""
import json
from pathlib import Path
from simulator.shield_damage_model import stacking_hypotheses

ROOT = Path(__file__).resolve().parents[1]
def run_sweep(incoming_hits=(50, 100, 150, 200, 300, 500), frost_dr=(0.0, 0.35, 0.50)):
    results = []
    for frost in frost_dr:
        for hit in incoming_hits:
            scenario = stacking_hypotheses(hit, frost_dr=frost)
            a = scenario["frost_on_shield"]
            b = scenario["frost_not_on_shield"]
            results.append({"incoming": hit, "frost_dr": frost,
                "health_damage_frost_on_shield": round(a["health_damage"], 5),
                "health_damage_frost_not_on_shield": round(b["health_damage"], 5),
                "health_damage_difference": round(b["health_damage"] - a["health_damage"], 5),
                "certified_current": False})
    return {"scenarios": results, "scenario_count": len(results),
            "assumptions": {"overshield_hp": 45, "overshield_dr": 0.70,
                            "frost_dr_options": list(frost_dr)},
            "status": "hypothetical_regression_sweep_not_verified_gameplay"}

def main():
    report = run_sweep()
    out = ROOT / "reports" / "shield_sweep.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scenario_count": report["scenario_count"], "status": report["status"]}))

if __name__ == "__main__":
    main()
