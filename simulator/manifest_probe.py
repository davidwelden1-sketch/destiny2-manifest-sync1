"""Read-only Bungie manifest version probe with fail-closed change classification.

No game-data download or automatic certification. Runs independently from
offline scenario calculations so network outages cannot corrupt stored evidence.
"""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = "https://www.bungie.net/Platform/Destiny2/Manifest/"

def classify_manifest(current, previous):
    if not isinstance(current, str) or not current.strip():
        raise ValueError("manifest version missing")
    if not isinstance(previous, str) or not previous.strip():
        return "baseline_unavailable_review_required"
    return "unchanged" if current == previous else "changed_invalidate_dependent_assumptions"

def probe_manifest(opener=urlopen, baseline_path=None):
    baseline_path = Path(baseline_path or ROOT / "data" / "manifest_version_baseline.json")
    try:
        req = Request(URL, headers={"User-Agent": "Destiny2-BuildLab-Research/1.0"})
        with opener(req, timeout=20) as response:
            payload = json.load(response)
        if payload.get("ErrorCode") != 1:
            raise ValueError("Bungie API returned non-success ErrorCode")
        current = payload["Response"]["version"]
        previous = json.loads(baseline_path.read_text(encoding="utf-8")).get("version") if baseline_path.exists() else None
        status = classify_manifest(current, previous)
        return {"status": status, "manifest_version": current, "baseline_version": previous,
                "source": URL, "current_gameplay_verified": False}
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return {"status": "probe_failed_manual_review_required", "error_type": type(exc).__name__,
                "source": URL, "current_gameplay_verified": False}

def main():
    result = probe_manifest()
    path = ROOT / "reports" / "manifest_probe.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "manifest_version": result.get("manifest_version")}))
    if result["status"] == "changed_invalidate_dependent_assumptions":
        print("::warning::Bungie manifest version changed; review perk legality, artifact and sandbox dependencies")
    elif result["status"] == "probe_failed_manual_review_required":
        print("::warning::Bungie manifest probe unavailable; offline audits remain valid but freshness unknown")

if __name__ == "__main__":
    main()
