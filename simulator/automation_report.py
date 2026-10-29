"""Offline, deterministic automation summary.

Does not scrape external sites, fabricate metrics or certify build legality.
Designed for scheduled CI and human-readable check-ins.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from simulator.patch_import import load_patch_notes

ROOT = Path(__file__).resolve().parents[1]

def generate_report(root=ROOT):
    root = Path(root)
    source_catalog = json.loads((root / "data" / "research_source_catalog.json").read_text(encoding="utf-8"))
    patch = load_patch_notes(root / "data" / "official_sandbox_2026_06.json")
    sources = source_catalog.get("sources", [])
    historical = json.loads((root / "data" / "historical_damage_observations.json").read_text(encoding="utf-8"))
    quarantined = [s.get("id") for s in sources if s.get("explicitly_outdated") is True
                   or s.get("explicitly_outdated_for_current_calibration") is True]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_count": len(sources),
        "quarantined_sources": quarantined,
        "official_patch": {"version": patch["game_version"],
                           "published_on": patch["published_on"],
                           "historical_observation_count": len(patch["observations"])},
        "historical_damage_observation_count": len(historical.get("observations", [])),
        "current_verified_measurements": 0,
        "certified_builds": 0,
        "automated_candidate_search": "not_run_no_verified_current_inputs",
        "next_actions": [
            "Review new Bungie patch notes and manifest version",
            "Acquire licensed, repeatable current-game measurements",
            "Independently verify measurement contexts and Artifact legality",
            "Calibrate and rank only when required inputs are available"
        ],
        "status": "source_inventory_only_not_live_sandbox_verification"
    }

def main():
    report = generate_report()
    out = ROOT / "reports" / "latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
