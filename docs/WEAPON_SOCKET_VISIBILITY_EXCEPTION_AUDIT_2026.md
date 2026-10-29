# Exact-hash randomized weapon socket visibility exception audit — 2026-10-29

## Why this exists
Bungie's `DestinyItemSocketEntryDefinition.defaultVisible` is only the *default* visibility of a socket. Bungie explicitly warns that instance runtime state may override it, and legacy sockets can remain in definitions for infrastructure. Therefore `randomizedPlugSetHash` membership, even when `currentlyCanRoll=true`, does not certify an equipped or selectable trait.

Official API schema: https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html

## Reproducible evidence
- `scripts/sync_extended.py` preserves item-hash-specific `socketEntries` metadata.
- `scripts/build_socket_candidates.py` preserves default visibility, source flags, randomized plug hashes and explicit current-roll status without promoting them to obtainability.
- NEW: `scripts/audit_weapon_socket_visibility.py` writes `output/weapon_socket_visibility_exceptions.json`, listing *exact item hashes*, socket indexes, plug-set hashes and plug candidates for every hidden-by-default or unknown-visibility randomized weapon socket. It excludes non-weapons and nonrandomized sockets.
- `tests/test_weapon_socket_visibility_audit.py` tests source provenance, sorting, count scope, empty sockets and the distinction between hidden and unknown using **synthetic fixtures**, not measured gameplay.
- `.github/workflows/sync-extended.yml` runs this audit after building the candidate index and uploads the resulting JSON with the other manifest outputs.

## Interpretation and test protocol
A `defaultVisible=false` entry is a definition-level **investigation target**, not an impossible weapon roll. Next steps for a specific hash: inspect Bungie `DestinyItemSocketsComponent` runtime socket state for a legitimate owned instance, distinguish collectible/quest and actual drop versions, verify two selectable trait columns and enhanced variants separately, and only then model perk activation and damage ownership.

Do not merge same-name item hashes, treat `currentlyCanRoll=true` as acquisition evidence, or interpret synthetic unit tests as in-game measurement. No certified damage, TTK, DR, cooldown or weapon build is implied.

Historical candidate shells S001–S285 and the 45 prior build candidates remain untouched. Artifact-dependent experiments must exclude Competitive and Trials (Bungie 9.7.0, June 9, 2026): https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0 .
