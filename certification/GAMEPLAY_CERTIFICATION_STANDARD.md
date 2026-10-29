# Prometheus Gameplay Certification Standard v1

No simulated or API-only build may be called gameplay-certified.

## Gates
G1 Data: record game build, manifest hash/version, source URLs, dates, PvE/PvP context and exact equipment/perks.
G2 Legality: verify slots, obtainable perk combinations, subclass fragment count, Artifact unlock and activity applicability.
G3 Simulation: reproduce damage, DR, cooldown, stacking and uptime with explicit assumptions and confidence bounds. Label SIMULATED.
G4 Measurement: attach raw footage/logs, timestamps, health/shield baseline, sample counts, control trials, measurement method and observed vs predicted deltas.
G5 Reproduction: independent repeat, same-patch repeat, failure cases, activity-specific validation, and reviewer signoff.

## Required result fields
build_id, game_version, manifest_version, activity, equipment, artifact_perks, expected_effect, observed_effect, trial_count, controls, evidence_urls, timestamp, uncertainty, stacking_rules, reproducibility, reviewer, certification_level, blockers, expiry_trigger.

## Hard failures
Missing evidence => at most G3. Missing legal perk proof => at most G1. PvE tests cannot certify PvP. Patch touching any dependency => STALE_PENDING_RETEST. A workflow success/green check does not certify gameplay. Never substitute synthetic logs for actual gameplay.

## Priority repair backlog
1. Add schema validation and mandatory evidence fields to certification outputs.
2. Make CI reject gameplay-certified status without G4/G5 evidence.
3. Split simulation, source-verification and in-game evidence into separate reports.
4. Add patch/manifest dependency invalidation.
5. Run known positive/negative fixtures and publish pass/fail reports.

Status: policy established, implementation and real gameplay testing still pending.
