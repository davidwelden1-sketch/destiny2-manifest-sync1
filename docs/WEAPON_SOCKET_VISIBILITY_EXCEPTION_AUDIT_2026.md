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

## Live result — 29 October 2026, manifest 245114.26.10.13.2000-1-bnet.66137
The live extended workflow completed successfully: https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40864743059 . It uploaded `destiny-extended-definitions` artifact ID `12892364874` (93,896,971 bytes). The audit reports **6,561 visible**, **one hidden-by-default**, and **zero unknown** randomized weapon sockets among the indexed equippable weapon definitions.

**The single hidden socket is Ergo Sum**, exact weapon item hash `1681583613`, zero-based socket index `3`, socket type hash `1466776700`, randomized plug set hash `1915986194`. The three plug hashes resolve in the **same downloaded Bungie item-definition snapshot** to:
- `2273483223` — Solar Damage Mod
- `3728733956` — Void Damage Mod
- `4126105782` — Arc Damage Mod

All three are marked `currentlyCanRoll=true` in this snapshot, but that status does not prove player-selectable swapping or acquisition. **Critical correction:** This hidden randomized socket is an **element/damage-mod socket**, not evidence of an extra normal weapon trait column. Therefore it must never be combined with an ordinary weapon perk to claim a two-trait god roll. The audit does not establish how the live Ergo Sum damage type is selected, nor whether this socket is user-visible on any instance. Source is the exact-hash official manifest audit and workflow log above; Bungie's schema explains the runtime-visibility caveat.

This is a new **catalog-classification finding**, not an in-game measurement. Any future all-weapons perk-pair legality model needs a verified socket-role classifier (trait versus element/intrinsic/other) in addition to exact item hashes, randomized membership, visibility and current-roll flags.

CI: https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40864761378 passed **113/113** synthetic/unit tests including the manifest-only plug-name resolution test. Neither CI nor the manifest confirms a complete legal Exotic/subclass/Artifact build.
