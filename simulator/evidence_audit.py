"""Check the status of evidence sources and their machine-readable limitations.

This is metadata triage, not web retrieval or independent gameplay verification.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def audit_evidence(root=ROOT):
    root = Path(root)
    catalog = json.loads((root / "data" / "research_source_catalog.json").read_text(encoding="utf-8"))
    leads = json.loads((root / "data" / "measurement_source_leads_2026_10_29.json").read_text(encoding="utf-8"))
    corroborated = json.loads((root / "data" / "officially_corroborated_defense_values.json").read_text(encoding="utf-8"))
    blocked = []
    for source in catalog["sources"]:
        if source.get("explicitly_outdated") or source.get("explicitly_outdated_for_current_calibration"):
            blocked.append({"id": source["id"], "reason": "outdated"})
        elif source.get("reuse_permission_confirmed") is False:
            blocked.append({"id": source["id"], "reason": "permission_unconfirmed"})
    return {"catalog_sources": len(catalog["sources"]),
            "measurement_leads": len(leads["sources"]),
            "historical_official_mechanics": len(corroborated["entries"]),
            "blocked_sources": blocked,
            "raw_measurement_trials": corroborated["raw_measurement_trials"],
            "verified_current_observations": 0,
            "status": "metadata_audit_not_current_gameplay_validation"}

def main():
    result = audit_evidence()
    path = ROOT / "reports" / "evidence_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
