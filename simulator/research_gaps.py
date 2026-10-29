"""Generate research priorities from measurement coverage, without inventing observations."""
from simulator.coverage import coverage_report

PRIORITY_METRICS = {
    "pve": ("boss_dps", "burst_damage", "damage_resistance", "ability_cooldown", "ammo_economy"),
    "pvp": ("precision_damage", "body_damage", "damage_falloff", "ability_cooldown", "damage_resistance"),
}

def missing_research(measurements, activity, mode, sandbox_version, artifact_enabled=None):
    if activity not in PRIORITY_METRICS:
        raise ValueError("Unsupported activity")
    covered = {
        row["metric"] for row in coverage_report(measurements)
        if row["activity"] == activity and row["mode"] == mode
        and row["sandbox_version"] == sandbox_version
        and row["artifact_enabled"] == artifact_enabled
        and row["verified_source_records"] > 0
    }
    return [{"metric": metric, "status": "needs_official_or_measured_evidence"}
            for metric in PRIORITY_METRICS[activity] if metric not in covered]
