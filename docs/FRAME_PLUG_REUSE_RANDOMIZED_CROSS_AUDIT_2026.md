# Frame-labelled initial plug reuse and randomized membership — 29 October 2026

## Research question
Previous game-wide audits established that `plugCategoryIdentifier = frames` is not a sufficient active-frame classifier: e.g. Bad Juju's Hip-Fire Grip and Full Auto Trigger System occur as initial plugs with that category. Can the **same exact initial plug hash** also be reused across weapon hashes/subtypes or appear in a randomized weapon socket? If so, treating a category-labelled initial plug as an exclusive intrinsic is particularly unsafe.

## Implementation
`scripts/audit_frame_plug_reuse.py` joins the same Bungie manifest's exact-hash equippable weapon definitions, initial plug references, and the source-separated randomized socket index. It counts distinct plug identities reused across multiple exact weapon hashes, multiple numeric weapon subtypes, any randomized weapon socket, and randomized sockets on one of the same weapons. Reports retain a bounded set of exact plug hashes and names.

These are four **separate** counts of plug identities, not item totals or legal roll counts. An overlap or reuse is a structural signal, not evidence of actual equippability, a live frame, a weapon trait, current acquisition, enhanced eligibility, or damage attribution. No result automatically maps a frame to Bungie's intrinsic anti-Champion effects.

Five synthetic regression tests check cross-subtype reuse, same-versus-other-weapon overlap, non-weapon/non-frame exclusion, malformed boolean hashes, and stale/unmatched index weapon hashes. Cross-index membership requires an exact weapon hash present in the same supplied manifest, not merely in an arbitrary socket index. The audit is integrated into the extended live sync; its `frame_initial_plug_reuse_audit.json` report is uploaded with the dataset.

## Evidence
- [Official Bungie socket entry definition](https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html) — initial plug and runtime socket caveats.
- [Official Bungie plug definition](https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html) — category identifier semantics.
- [Bungie Update 9.7.0, 9 June 2026](https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0) — frame-based anti-Champion rules; Artifacts disabled in Competitive and Trials.
- [Bungie Update 9.7.0.6, 20 October 2026](https://www.bungie.net/7/en/News/Article/destiny_2_update_9_7_0_6) — latest official patch located in 29 October search, Eververse only.
- [GitHub test run 40939453865](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40939453865) — direct job log confirms 162/162 passing synthetic and software tests before the additional stale-index test; verify the subsequent CI run separately.
- [Extended sync run 40939473203](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40939473203) — check completion and artifact before citing live reuse counts.

## Next
Read live audit counts and exact-hash examples; investigate any overlaps against runtime socket evidence and independently verified frame descriptions. Maintain strict provenance in Hunter/Titan/Warlock Artifact-first PvE and ordinary 6v6 candidate studies. Do not claim a playable roll or measured DPS, TTK, DR, cooldown or uptime from this index. Preserve the 45 historical candidate shells.

## Live audit readback — 29 October 2026, 19:24 UTC
[Extended GitHub Actions run 40939473203](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40939473203) **completed successfully** on source commit `5e19dc31`; artifact `destiny-extended-definitions` ID `12927255313` uploaded (94,289,949 bytes). The direct job log identifies Bungie manifest `245114.26.10.13.2000-1-bnet.66137`, 2,208 equippable weapon definitions and:

| Exact-hash plug identity metric | Observed count |
| --- | ---: |
| Distinct `frames`-labelled initial plug hashes | 325 |
| Those reused across more than one weapon item hash | 187 |
| Those spanning more than one numeric weapon subtype | 149 |
| Those also in at least one weapon's randomized socket pool | 207 |
| Those also randomized on a weapon where they are an initial `frames` plug | 204 |

The counts **overlap** and must not be added together. They refer to distinct plug hashes, not weapon counts, active frame counts or legal trait pairs. The direct log includes `Iron Grip` plug hash `11551321` and `Adrenaline Junkie` plug hash `11612903` as concrete examples. These are named weapon traits represented by the ambiguous `frames` initial-plug category, further demonstrating that category alone cannot assign an intrinsic.

After this run, commits `a5ffb577` and `cc352719` additionally fail closed when a socket index refers to a weapon hash missing from the same supplied manifest, with a fifth synthetic regression test. [GitHub Actions test run 40939652720](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40939652720) **completed successfully: 163/163 tests**. A subsequent extended live synchronization incorporating the stale-index fix was in progress at this note; do not claim it succeeded until readback.

**Inference boundary:** These counts show structural role ambiguity and cross-socket reuse, not that a weapon can equip a specific trait, that an intrinsic frame is active, or that any enhanced perk or Artifact interaction is legal. The next validation requires runtime socket instances and independent acquisition/weapon-frame evidence.
