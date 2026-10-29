# Current sandbox measurement ingestion

## Sources discovered (2026-10-29)
- Clarity live research: https://github.com/Database-Clarity/Live-Clarity-Database (repository updated 2026-10-27)
- Clarity character stats: https://github.com/Database-Clarity/Character-Stats (updated 2026-10-26)
- Destiny Science directory: https://www.destiny2.science/
- Owl Sector: https://www.owlsector.net/ (underlying dataset last refreshed 2026-10-02)
- PvP damage: https://docs.google.com/spreadsheets/d/1b57Hb8m1L3daFfUckQQqvvN6VOpD03KEssvQLMFpC5I/edit

A listing or repository update date does NOT verify any specific damage value.
No external measurement rows have yet been imported.

## Export and import
1. Confirm a source's measurement methods, licensing and game-version applicability.
2. Export permissioned observations as CSV; do not scrape inaccessible sources.
3. Use `data/measurement_template.csv` for required columns.
4. Give each repeat a unique `sample_id`; use a precise `scenario` including weapon/item hash, perk state, target, distance, weapon stat, activity and buffs.
5. Run: `python -m simulator.measurement_import path/to/observations.csv`.
6. Review grouped averages, spread and evidence manually. The importer deliberately returns `verified_in_game: false`.

Three observations are the minimum for a summary, NOT a claim of statistically sufficient evidence.
For any calibration, hold back separate measurements not used to fit the model.

## Missing before strong claims
- Ingest licensed, current, attributable raw observations, not just web descriptions.
- Independently verify context, damage scaling, weapon stat, PvE power level, target classification and patch version.
- Calibrate per archetype and damage scenario with held-out observations.
- Link source-reviewed outputs to candidate metrics with uncertainty bounds.
- Obtain actual in-game reproduction for promising builds.
