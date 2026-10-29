# Frame-labelled initial plug reuse and randomized membership — 29 October 2026

## Research question
Previous game-wide audits established that `plugCategoryIdentifier = frames` is not a sufficient active-frame classifier: e.g. Bad Juju's Hip-Fire Grip and Full Auto Trigger System occur as initial plugs with that category. Can the **same exact initial plug hash** also be reused across weapon hashes/subtypes or appear in a randomized weapon socket? If so, treating a category-labelled initial plug as an exclusive intrinsic is particularly unsafe.

## Implementation
`scripts/audit_frame_plug_reuse.py` joins the same Bungie manifest's exact-hash equippable weapon definitions, initial plug references, and the source-separated randomized socket index. It counts distinct plug identities reused across multiple exact weapon hashes, multiple numeric weapon subtypes, any randomized weapon socket, and randomized sockets on one of the same weapons. Reports retain a bounded set of exact plug hashes and names.

These are four **separate** counts of plug identities, not item totals or legal roll counts. An overlap or reuse is a structural signal, not evidence of actual equippability, a live frame, a weapon trait, current acquisition, enhanced eligibility, or damage attribution. No result automatically maps a frame to Bungie's intrinsic anti-Champion effects.

Four synthetic regression tests check cross-subtype reuse, same-versus-other-weapon overlap, non-weapon/non-frame exclusion, and malformed boolean hashes. The audit is integrated into the extended live sync; its `frame_initial_plug_reuse_audit.json` report is uploaded with the dataset.

## Evidence
- [Official Bungie socket entry definition](https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html) — initial plug and runtime socket caveats.
- [Official Bungie plug definition](https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html) — category identifier semantics.
- [Bungie Update 9.7.0, 9 June 2026](https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0) — frame-based anti-Champion rules; Artifacts disabled in Competitive and Trials.
- [Bungie Update 9.7.0.6, 20 October 2026](https://www.bungie.net/7/en/News/Article/destiny_2_update_9_7_0_6) — latest official patch located in 29 October search, Eververse only.
- [GitHub test run 40939453865](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40939453865) — direct job log confirms 162/162 passing synthetic and software tests.
- [Extended sync run 40939473203](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40939473203) — check completion and artifact before citing live reuse counts.

## Next
Read live audit counts and exact-hash examples; investigate any overlaps against runtime socket evidence and independently verified frame descriptions. Maintain strict provenance in Hunter/Titan/Warlock Artifact-first PvE and ordinary 6v6 candidate studies. Do not claim a playable roll or measured DPS, TTK, DR, cooldown or uptime from this index. Preserve the 45 historical candidate shells.
