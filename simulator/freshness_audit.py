"""Offline source-age triage; does not fetch live patch notes or Bungie manifest."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def freshness_report(root=ROOT, as_of=None, max_age_days=30):
    root = Path(root)
    today = date.fromisoformat(as_of) if isinstance(as_of, str) else (as_of or date.today())
    if type(max_age_days) is not int or max_age_days < 0:
        raise ValueError("nonnegative integer max_age_days required")
    catalog = json.loads((root / "data" / "research_source_catalog.json").read_text(encoding="utf-8"))
    items = []
    for src in catalog["sources"]:
        raw = src.get("reported_data_refreshed_on") or src.get("reported_updated_on")
        if src.get("explicitly_outdated") or src.get("explicitly_outdated_for_current_calibration"):
            status = "blocked_explicitly_outdated"
        elif not raw:
            status = "review_required_date_missing"
        else:
            try:
                updated = date.fromisoformat(raw)
            except (TypeError, ValueError):
                status = "review_required_date_invalid_or_partial"
            else:
                if updated > today:
                    status = "review_required_future_date"
                else:
                    status = "review_required_age_exceeded" if (today - updated).days > max_age_days else "recent_metadata_only"
        items.append({"id": src["id"], "reported_date": raw, "status": status,
                      "current_gameplay_verified": False})
    return {"checked_at": today.isoformat(), "max_age_days": max_age_days,
            "sources": items, "status": "offline_metadata_only_no_live_patch_or_manifest_fetch"}

def main():
    result = freshness_report()
    path = ROOT / "reports" / "freshness.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sources_checked": len(result["sources"]), "status": result["status"]}))

if __name__ == "__main__":
    main()
