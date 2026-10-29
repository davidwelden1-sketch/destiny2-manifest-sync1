# Exact-hash socket source provenance — 29 October 2026

## New source-level blocker

Bungie's `DestinyItemSocketEntryDefinition.plugSources` is a bitmask, not a
single source label. Official `Destiny.SocketPlugSources` values are:
inventory-sourced 1, reusable runtime 2, profile plug set 4, character plug
set 8. One socket can require multiple sources. A manifest
`randomizedPlugSetHash` alone therefore cannot establish the complete set
of currently insertable or obtainable plugs.

Bungie also distinguishes `singleInitialItemHash` (initial plug),
`reusablePlugSetHash` (reusable plug set), and `randomizedPlugSetHash`
(randomized set). A `DestinyPlugSetDefinition` may have `isFakePlugSet`.
None of these fields alone proves a live active frame or a legal obtainable
enhanced roll.

## Implementation

`simulator/socket_provenance.py` returns exact item-hash, socket-index,
source flags, missing plug-set references, fake-set flags, and initial-plug
hashes. It always sets `certified_roll=False`. Synthetic tests cover
profile+character flags, fake sets, unresolved references, missing exact
hashes and malformed source flags.

Follow-up: connect this audit to the current extended manifest sync,
separately index runtime/profile/character sources where legitimately
available, and test exact weapon versions. Preserve existing 45 historical
candidate shells.

## Official references

- https://bungie-net.github.io/multi/schema_Destiny-SocketPlugSources.html
- https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html
- https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0

Update 9.7.0 (9 June 2026) moved anti-Champion capability to weapon
intrinsics and disabled Artifact perks in Glory and Trials. Update 9.7.0.6
(20 October 2026) lists an Eververse fix only; it does not establish new
damage or frame values.

No in-game measurement, complete legal-roll certification, or best-build
ranking is claimed.
