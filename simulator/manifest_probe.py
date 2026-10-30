"""Read-only Bungie manifest version probe with fail-closed change classification.

No game-data download or automatic certification. Runs independently from
offline scenario calculations so network outages cannot corrupt stored evidence.
"""
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = "https://www.bungie.net/Platform/Destiny2/Manifest/"

def classify_manifest(current, previous):
    if not isinstance(current, str) or not current.strip():
        raise ValueError("manifest version missing")
    if not isinstance(previous, str) or not previous.strip():
        return "baseline_unavailable_review_required"
    return "unchanged" if current == previous else "changed_invalidate_dependent_assumptions"

def probe_manifest(opener=urlopen, baseline_path=None, max_attempts=2):
    """Retry only bounded transport/server failures; never certify a failed probe.

    A non-success Bungie API response, invalid payload, and HTTP 4xx (including
    rate limits) require review rather than immediate repeated requests.
    """
    if type(max_attempts) is not int or not 1 <= max_attempts <= 3:
        raise ValueError("max_attempts must be an integer between 1 and 3")
    baseline_path = Path(baseline_path or ROOT / "data" / "manifest_version_baseline.json")
    req = Request(URL, headers={"User-Agent": "Destiny2-BuildLab-Research/1.0"})
    for attempt in range(1, max_attempts + 1):
        try:
            with opener(req, timeout=20) as response:
                payload = json.load(response)
            if payload.get("ErrorCode") != 1:
                raise ValueError("Bungie API returned non-success ErrorCode")
            current = payload["Response"]["version"]
            previous = (json.loads(baseline_path.read_text(encoding="utf-8")).get("version")
                        if baseline_path.exists() else None)
            status = classify_manifest(current, previous)
            return {"status": status, "manifest_version": current,
                    "baseline_version": previous, "source": URL,
                    "attempts": attempt, "current_gameplay_verified": False}
        except (OSError, ValueError, KeyError, TypeError) as exc:
            http_code = exc.code if isinstance(exc, HTTPError) else None
            retryable = (isinstance(exc, HTTPError) and http_code in (500, 502, 503, 504)
                         or isinstance(exc, OSError) and not isinstance(exc, HTTPError))
            if retryable and attempt < max_attempts:
                continue
            result = {"status": "probe_failed_manual_review_required",
                      "error_type": type(exc).__name__, "attempts": attempt,
                      "source": URL, "current_gameplay_verified": False}
            if http_code is not None:
                result["http_status"] = http_code
            return result


def main():
    result = probe_manifest()
    path = ROOT / "reports" / "manifest_probe.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "manifest_version": result.get("manifest_version"),
                      "attempts": result.get("attempts"), "error_type": result.get("error_type"),
                      "http_status": result.get("http_status")}))
    if result["status"] == "changed_invalidate_dependent_assumptions":
        print("::warning::Bungie manifest version changed; review perk legality, artifact and sandbox dependencies")
    elif result["status"] == "probe_failed_manual_review_required":
        print("::warning::Bungie manifest probe unavailable; offline audits remain valid but freshness unknown")

if __name__ == "__main__":
    main()
