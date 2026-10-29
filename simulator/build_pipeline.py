"""Fail-closed preliminary build screening across Artifact, loadout and metrics."""
from simulator.artifact_screen import screen_one_active_artifact
from simulator.loadout_completeness import loadout_gaps
from simulator.candidate_comparison import compare_candidates

def evaluate_candidates(builds, artifact_catalog, weights):
    accepted, rejected = [], []
    for index, build in enumerate(builds):
        ident = build.get("id", index) if isinstance(build, dict) else index
        if not isinstance(build, dict):
            rejected.append((ident, "malformed_build"))
            continue
        if not loadout_gaps(build)["complete_fields"]:
            rejected.append((ident, "incomplete_loadout"))
            continue
        try:
            result = screen_one_active_artifact(build["class"], build["activity"],
                build.get("artifact_id"), build["artifact_perks"], artifact_catalog)
        except (ValueError, TypeError, KeyError):
            rejected.append((ident, "invalid_artifact_input"))
            continue
        if not result["eligible"]:
            rejected.append((ident, result["reason"]))
            continue
        if build.get("weapon_legality_checked") is not True:
            rejected.append((ident, "weapon_legality_not_checked"))
            continue
        accepted.append({"id": ident, "class": build["class"], "legal": True,
                         "artifact_checked": True, "metrics": build.get("metrics")})
    ranked = compare_candidates(accepted, weights)
    ids = {r["id"] for r in ranked}
    rejected.extend((r["id"], "invalid_metrics") for r in accepted if r["id"] not in ids)
    return {"ranked": ranked, "rejected": rejected, "certified_builds": 0}
