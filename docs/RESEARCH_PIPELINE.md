# Five-stage research pipeline: status and evidence contract

## 1. Source ingestion
- Bungie manifest and exact-hash socket indexes: existing pipeline.
- `data/official_sandbox_2026_06.json`: historical 9.7.0 patch-note values.
- `simulator/patch_import.py`: schema and provenance checks.
- Patch-note values are **not** live-game measurements. Never infer a patch value is current without reviewing subsequent changes.

## 2. Measurement and calibration
- `simulator/measurement_aggregation.py`: group comparable observations, compute spread.
- `simulator/measurement_comparison.py`: descriptive comparison only.
- `simulator/calibration.py`: prediction residuals, MAE, RMSE.
- No automated capture from Destiny 2 exists. Repeated observations need documented testers, method, game version, target, activity, source and independent review.

## 3. Comparison
- `simulator/candidate_comparison.py`: normalized damage, survival and uptime.
- `simulator/build_pipeline.py`: Artifact and exact-hash socket-membership screening.
- Rankings remain **hypotheses**, not fully legal builds; socket membership alone does not certify obtainability.

## 4. Build completeness and certification
- `simulator/loadout_completeness.py` checks required fields.
- `simulator/certification_gate.py` and `simulator/source_evidence.py` require sourced evidence.
- Structural source checks do not prove evidence authenticity. No fully certified build is claimed.

## 5. Controlled verification
- `simulator/discovery_review.py` prioritizes model candidates for controlled gameplay testing.
- Queue requirements: current version, provenance, obtainable roll, legal Artifact, stacking and damage evidence, repeatability, activity.
- Promotion to certified requires independent review, not merely a high ranking score.

## Next blockers
1. Acquire contemporary, repeatable PvP and PvE measurements with primary evidence.
2. Build complete frame/trait/obtainability constraints from manifest and authoritative sources.
3. Encode current Artifact tree with prerequisite, point-limit and activity restrictions.
4. Implement ability-specific timing and stacking rules, calibrate against gameplay.
5. Execute GitHub CI and inspect results before asserting tests pass.

Reference: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
