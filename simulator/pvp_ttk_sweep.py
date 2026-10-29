"""Deterministic historical PvP adaptive auto-rifle TTK sweep.

Uses official June 2026 9.7.0 patch-note damage only; not a current
weapon roll, measured TTK or claim of live-game validity.
"""
import json
from pathlib import Path
from simulator.patch_import import load_patch_notes

ROOT = Path(__file__).resolve().parents[1]

def run_pvp_sweep(path=None, health_values=(200, 210, 220, 230), rpm=600):
    data = load_patch_notes(path or ROOT / "data" / "official_sandbox_2026_06.json")
    values = {row["id"]: row for row in data["observations"]}
    crit = values["adaptive_auto_crit"]["new_value"]
    body = values["adaptive_auto_body"]["new_value"]
    if any(type(h) not in (int, float) or h <= 0 for h in health_values):
        raise ValueError("positive health values required")
    if type(rpm) not in (int, float) or rpm <= 0:
        raise ValueError("positive rpm required")
    rows = []
    for health in health_values:
        for precision in range(0, 20):
            for bodyshots in range(0, 20):
                shots = precision + bodyshots
                if shots == 0 or precision * crit + bodyshots * body < health:
                    continue
                if (precision * crit + bodyshots * body - min(crit if precision else float("inf"),
                                                              body if bodyshots else float("inf"))) >= health:
                    continue
                rows.append({"target_health": health, "precision_hits": precision,
                             "body_hits": bodyshots, "shots": shots,
                             "ttk_seconds": round((shots - 1) * 60 / rpm, 6),
                             "certified_current": False})
    return {"game_version": data["game_version"], "source_url": data["source_url"],
            "assumed_rpm": rpm, "results": rows, "result_count": len(rows),
            "status": "historical_patch_note_theoretical_ttk_not_current_verified"}

def main():
    report = run_pvp_sweep()
    out = ROOT / "reports" / "pvp_ttk_sweep.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result_count": report["result_count"], "status": report["status"]}))

if __name__ == "__main__":
    main()
