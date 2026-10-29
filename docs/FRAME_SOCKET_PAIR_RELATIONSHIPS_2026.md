# Frame-labelled socket-pair relationships — evidence audit (29 October 2026)

## Research question
S291 found 1,104 exact weapon hashes with two `frames`-labelled initial-plug socket occurrences, but did not establish whether the two sockets have the same or different socket-type definitions, share initial plugs, or appear at consistent socket positions. These distinctions are prerequisites for any defensible active-frame mapping.

## Implementation
`scripts/audit_weapon_frame_candidates.py` now emits:
- `multi_frame_socket_index_patterns`: counts exact socket-index tuples without merging weapon names or versions.
- `multi_frame_socket_type_relationships`: `same_socket_type`, `different_socket_types`, or `unknown_socket_type`; missing, zero, negative, and boolean socket-type hashes fail closed.
- `multi_frame_plug_identity_relationships`: same versus different initial-plug hashes.
- `multi_frame_socket_type_pairs_top` and `multi_frame_relationship_examples`: provenance for manual follow-up, with exact weapon hash and socket indexes.

These are **structural relationships among initial-plug records**, not active frame identities, roll legality, or a classification of which frame grants intrinsic anti-Champion behavior. An equal socket-type hash does not establish mutually exclusive frames; differing hashes do not establish simultaneous active frames.

## Verification
Commits `a979cd2ca93f924a794b2c2e531a87d85bdfea3e` (audit) and `3dbc202564c1acf7b3db95ee04b5d9dbaa491b7e` (three synthetic regression tests).
[GitHub Actions test run 40920022750](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40920022750): completed success; direct logs show **155/155 tests passed**.
[Extended manifest run 40919995741](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40919995741): triggered by audit commit; live counts and artifact must be verified from logs before reporting.

## Official sources
- [Bungie socket-entry schema](https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html): `singleInitialItemHash` and socket type definitions.
- [Bungie plug-definition schema](https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html): category identifiers.
- [Bungie 9.7.0, June 9, 2026](https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0): intrinsic anti-Champion frame rules and Artifact restrictions.

## Next evidence gates
Validate the live distribution by socket-type relationship and socket-index pattern, inspect exact hashes in each category, independently identify active intrinsic frames, and then check exact-hash acquisition and enhanced perk eligibility. Only then test Artifact-first Hunter/Titan/Warlock interactions, activation, ownership, stacking, damage, TTK, DR and cooldowns. Keep all 45 historical candidates and previous entries unchanged.

## Live manifest verification — 29 October 2026, 17:19 UTC
[Extended run 40919995741](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40919995741) **completed successfully**. Direct job logs show manifest `245114.26.10.13.2000-1-bnet.66137`, 2,208 equippable weapon definitions, 2,713 frame-labelled initial-plug occurrences, and 1,104 exact weapon hashes with two labelled occurrences. Uploaded artifact ID `12916744860`, 94,272,776 bytes.

**New relationship evidence** (per exact weapon hash, not distinct rolls):
- Socket-index pairs: `3,4` = **1,072**; `2,3` = **27**; `1,4`, `2,4`, `3,12`, `3,6`, `4,6` = **1 each**.
- Socket-type relationships: **1,102 different**, **2 same**, **0 unknown**.
- Initial-plug identities: **1,104 different**, **0 same**.
- Exact socket-type hash pair `1215804696,1215804697` accounts for **1,100** of 1,104 multi-labelled weapons. The remaining four socket-type pairs each occur once: `1215804696,1215804696`, `1215804696,3530202021`, `1215804697,1215804697`, `63353896,1215804697`.
- **0 unresolved initial-plug references** in this snapshot.

**Interpretation:** The 1,100 repeated socket-type pairs are a strong structural regularity, and the four outliers deserve exact-hash follow-up. Neither the type hashes nor the `frames` category proves which socket is a live intrinsic, an ordinary trait, or a Champion-granting frame. No gameplay performance or current acquisition was measured. The 45 historical candidates remain preserved.
