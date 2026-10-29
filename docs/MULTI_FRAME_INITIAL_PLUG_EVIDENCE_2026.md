# Multiple frame-labelled initial plugs — game-wide evidence audit (29 October 2026)

## Why this audit exists
The prior live Bungie manifest run indexed **2,713** `plugCategoryIdentifier="frames"` initial-plug socket occurrences across **1,609** exact equippable weapon item hashes (2,208 weapon definitions total). Because occurrences exceed covered weapons by 1,104, at least some weapon hashes necessarily contain multiple such occurrences. This is a structural statement about manifest records, **not** a claim of multiple active intrinsic frames, multiple simultaneous perks, or Champion functionality.

The new audit in `scripts/audit_weapon_frame_candidates.py` reports the number of exact weapon hashes with two or more frame-labelled *initial-plug socket occurrences*, the number of those occurrences, and up to 30 examples with exact item hash, socket indexes, distinct plug hashes and names. Repeated plugs on different sockets are counted as separate occurrences but not distinct plug hashes. The live extended workflow establishes the exact distribution below; it is not safe to infer the multi-labelled weapon count from 2,713 minus 1,609 alone.

## Evidence status
- **Official API semantics:** `singleInitialItemHash` is the initially inserted plug; `plugCategoryIdentifier` is a category identifier. Neither proves the live active frame or a legal roll.
- **Synthetic software verification:** three new regression tests cover two different frame-labelled plugs on one item hash, repeated identical plug hash on two sockets, and zero-multiple cases. GitHub Actions run [40911049954](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40911049954) passed 152/152 tests on commit `9c90982f81e59a554d10b8a35b63daeebb67a7c2`.
- **Live manifest:** snapshot `245114.26.10.13.2000-1-bnet.66137`. GitHub Actions extended run [40911028324](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40911028324) passed and uploaded artifact ID `12912869719` (94,271,946 bytes). Direct job log: **1,104** exact weapon hashes each have **two** frame-labelled initial-plug socket occurrences (2,208 occurrences), **505** have one, **599** have zero. Total 2,208 equippable weapon definitions; 2,713 labelled occurrences across 1,609 covered hashes. These are socket-occurrence counts, not distinct frame identities.
- **Game testing:** none. No DPS, TTK, DR, cooldown, perk activation or runtime socket state is measured here.

## Buildcrafting consequence
Never collapse `frames` initial-plug records into one active intrinsic, assume two frame-labelled records are mutually exclusive, or infer an anti-Champion effect for an exact weapon hash. The official 9.7.0 weapon-frame anti-Champion rule still requires an independently verified weapon type and active frame. Preserve exact item hash, socket index, source, manifest version and evidence status when connecting weapon frames to Exotic armor, subclass and one active Artifact. Artifact perks are disabled in Competitive and Trials.

## Primary sources
- Bungie socket-entry schema: https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html
- Bungie plug-definition schema: https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html
- Bungie 9.7.0 patch, 9 June 2026: https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
- Prior live indexed run: https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40900145517

## Next evidence gates
Verify live multi-labelled counts; distinguish frame-labelled socket *roles* and actual runtime frame; validate acquisition and enhanced perk legality by exact item hash; then test damage ownership, stacking, regen and ability uptime. Preserve all 45 historical candidate shells and the prior research record.
