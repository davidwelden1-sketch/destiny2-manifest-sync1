# Exact-hash initial-plug frame evidence — 29 October 2026

## New evidence boundary
Bungie's `DestinyItemSocketEntryDefinition.singleInitialItemHash` points to the plug initially inserted when the item is created. It does **not** certify which frame is active on a live instance, whether a plug can be changed, or whether an item can currently drop. The plug's `plugCategoryIdentifier` is category metadata; the label `frames` is not by itself proof of a weapon's intrinsic frame or Champion behavior.

Official Bungie schema:
- https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html
- https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html
- https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0 (June 9, 2026, specific anti-Champion frame rules)

## Implementation
`scripts/audit_weapon_frame_candidates.py` joins exact-hash equippable weapon definitions with their initial plug definitions in the same manifest snapshot. It emits `weapon_initial_frame_candidates.json` including exact item hash, socket index, initial plug hash/name, category, default visibility, unresolved references and explicit unverified status. Different weapon versions sharing a display name are never merged. The report is uploaded with the extended GitHub Actions dataset.

Six synthetic regression tests verify exact-hash isolation, non-frame category exclusion, missing references, boolean/invalid hashes, and fail-closed active-frame/Champion status. These are **software tests**, not gameplay measurements.

## Follow-up certification gates
1. Read the generated report from a successful extended manifest run and count its candidates; do not assume counts before the job completes.
2. For each candidate, independently validate the actual intrinsic frame and weapon type on the exact item version, preferably with live item socket evidence.
3. Apply the official `simulator/champion.py` frame rule only after step 2; no automatic promotion of a `frames`-labelled plug.
4. Separately validate trait columns, enhanced availability, current acquisition and Artifact-enabled activity. Artifacts are disabled in Competitive and Trials.
5. Damage, DPS, TTK, damage resistance, cooldowns, kill attribution and uptime still require measured or separately sourced inputs.

The existing 45 historical candidates and prior research remain unchanged.

## Verified live manifest result (29 October 2026)

GitHub Actions extended sync [40900145517](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40900145517) **completed successfully** and uploaded artifact `destiny-extended-definitions` (artifact ID `12909575925`, 94,271,193 bytes). Its job log reports manifest `245114.26.10.13.2000-1-bnet.66137`, 2,208 equippable weapon definitions, **2,713 `frames`-labelled initial-plug socket occurrences across 1,609 distinct weapon hashes**, and **zero unresolved initial-plug references**. Multiple occurrences can belong to one weapon; these counts are not unique frame types, playable intrinsics, current drops, or Champion-certified weapons. The six new regression tests passed in [test run 40900128069](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40900128069), with **149/149 total tests** passing.

The remaining **599** indexed weapon definitions (2,208 minus 1,609) have no `frames`-labelled initial plug detected by this particular audit; this is an **evidence-coverage gap**, not evidence they lack intrinsic frames or Champion effects. The next investigation should sample both the multi-candidate and no-candidate populations against verified live frame information before using any exact-hash Champion classification.
