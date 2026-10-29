# Game-wide weapon-roll status: official `currentlyCanRoll` evidence (2026-10-29)

## Newly identified evidence gap

Bungie's published API schema for `DestinyItemSocketEntryPlugItemRandomizedDefinition` explicitly defines `currentlyCanRoll`: whether that plug can be rolled on the **current version of the item**, distinguishing historical/retired combinations from current ones. The previous extended index flattened each `DestinyPlugSetDefinition.reusablePlugItems[]` entry to its `plugItemHash`, discarding this status flag. Consequently, same-item-hash and distinct-randomized-socket membership was **necessary but insufficient** evidence for a current perk roll, even before checking acquisition or enhancement.

Primary documentation: https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryPlugItemRandomizedDefinition.html
Socket schema: https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html

## Implemented data correction

- `scripts/sync_extended.py` preserves `plugset_roll_flags.json` with `plugItemHash` and explicit `currentlyCanRoll` values alongside the unchanged historical `plugsets.json`.
- `scripts/build_socket_candidates.py` now separates each randomized socket's plugs into **explicit true**, **explicit false**, and **unknown** (missing or contradictory flag) groups. A missing flag is never inferred true. Original randomized candidates remain available for historical research.
- `scripts/query_weapon_pairs.py --currently-rollable-only` requires both plugs to have explicit `currentlyCanRoll=true` in distinct randomized sockets **on the same exact item hash**. The ordinary query remains a historical structural query. Summary reports count memberships by status.
- The extended GitHub workflow publishes the strict query alongside the historical dual-trait Lotus-Eater investigation. Synthetic tests cover current, retired, unknown, conflicting, same-socket, and malformed hash cases.

## Evidence tiers and unresolved blockers

**Official schema (high confidence):** The `currentlyCanRoll` field exists and is explicitly intended to distinguish current-version from older-version rolls. **Code-tested:** The filter respects true/false/unknown semantics on synthetic inputs. **Manifest-dependent:** Real-game status counts and the Lotus-Eater strict query must be read from the successful current CI artifact, not guessed. **Not proven:** Vendor/drop obtainability, enhanced socket compatibility, crafting unlocks, patch migrations, Exotic/Artifact interactions, damage ownership, cooldowns, or gameplay performance.

The earlier 58,756 cross-variant phantom-pair occurrences are a **separate** name-merging issue and must not be relabelled as retired-perk counts. The new flag check adds an independent legality filter, not a replacement for exact item-hash grouping.

## Artifact-first experiment

Retest 2026 Lotus-Eater Dimensional Shift + Collective Action against the strict roll-status output before comparing Void Breach pickup -> Collective Action activation -> conditional Void Overshield final blow. In an Artifact-enabled PvE activity, separately test Unto the Breach / Volatile Flow effects and distinguish the physical Void Breach from Heavy-ammo-bar progress granted by Bricks from Beyond. Hunter, Titan and Warlock Exotic comparisons remain hypotheses until attribution and measured damage are available. Do not use Artifact-enabled simulations for Competitive or Trials (Bungie Update 9.7.0, June 9, 2026: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0).

This document does not certify any current obtainable roll, enhanced combination, or complete build.

## Live manifest result, 2026-10-29 09:25 UTC

Connected GitHub Actions extended sync [40849229722](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40849229722) completed successfully on commit `55cbd92b545d17f5b3c4530731994141f2582a1e`. The official retrieved manifest version is `245114.26.10.13.2000-1-bnet.66137`. Its direct job log reports **97,283 randomized weapon plug memberships explicitly marked `currentlyCanRoll=true`**, **zero explicitly false**, and **zero unknown**, for the indexed equippable weapon scope. The exact-hash Dimensional Shift + Collective Action structural query returns **16** candidates in both the ordinary and strict-flag mode. The new extended dataset artifact `12886427175` uploaded successfully (92,750,895 bytes).

**Critical interpretation:** The flag is present, but **non-discriminating in this particular indexed snapshot**. It does not identify any retired plug memberships here. This is a precise evidence blocker, not proof that all historical rolls are obtainable or that the 16 candidates are valid drops. Future work must inspect vendor/loot pool, crafting, socket plug-category, and instance-level evidence rather than using `currentlyCanRoll=true` alone as a certification.

The latest repository change also makes the summary report this no-false/zero-unknown condition explicitly, with a synthetic regression test. Its later CI status must be verified separately.
