# Measurement evidence ingestion specification

Status: engineering specification; not proof of in-game measurement.

Each observation MUST record:
- observation_id, game_build_or_manifest_version, observed_at_utc
- activity_mode (PvE/PvP), target_type, weapon_or_ability_id, exact configuration
- raw_damage_events or raw_timestamps, sample_count, test_conditions
- source_url, source_kind (first_party_capture / independently_reproducible / third_party)
- measurement_method, uncertainty, reviewer, validation_state
- applicable_patch_start and applicable_patch_end (nullable)

Validation rules:
1. Missing raw evidence, test conditions, or patch applicability => hypothesis only.
2. Historical values cannot certify current sandbox.
3. Simulation outputs cannot be re-imported as observations.
4. Independent repeated samples and a recorded methodology are required for measured certification.
5. All numerical comparisons retain source IDs and calculation version.
6. A green CI receipt certifies pipeline operation only.

Initial backlog:
- Build ingestion schema and parser with rejection tests.
- Import legally usable current measured trials with provenance.
- Compare predictions against measurements and publish error distributions.
- Prevent build certification when required legality, stacking or Artifact evidence is missing.
- Surface source freshness and evidence coverage in every automated report.
