# Project FORGE — Engineering Charter

Research & Development Director: FORGE (ChatGPT-based research and engineering assistant), working under user direction.\nProject: Project FORGE — Destiny 2 Intelligence & Build Engineering.\nLegacy name: Destiny 2 Build Lab (retained for historical references).
Scope: Destiny 2 PvE and PvP, all classes. Artifact-first synergy; exact legal combinations.

## Definition of done
- A GitHub Actions success receipt identifies run URL, commit SHA, test counts, and artifact provenance.
- Manifest metadata includes source, version, retrieval time, digest, and coverage.
- Measured gameplay values, sandbox documentation, and simulations have separate evidence labels.
- Every certified build passes legality, stacking, damage, cooldown, and rotation checks. Unverified fields prevent certification.
- Regressions open actionable failures; fixes require a subsequent successful run before closure.

## Delivery order
1. Audit receipts and artifact contents; validate required files and schema.
2. Pin sources and establish freshness/coverage thresholds.
3. Build weapon/perk/armor/subclass/artifact legality relationships.
4. Implement deterministic PvE and PvP simulators with test fixtures.
5. Run candidate search, rank by damage/survivability/uptime, and produce reproducible reports.
6. Add change detection and safe automated retry; escalate only irrecoverable permission/data problems.

## Non-negotiable controls
- A green CI run proves code execution, not live-game accuracy.
- Never fabricate measured values or call a simulated result measured.
- Keep reproducible inputs, source timestamps, confidence labels, and failed cases.
- Avoid claiming exhaustive enumeration until coverage is measured.
