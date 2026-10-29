# Exact-hash frame socket outlier investigation — 29 October 2026

## Question
The previous live manifest audit found 1,104 exact weapon versions with two initial plugs labelled `frames`; 1,100 shared the same socket-type pair `1215804696,1215804697`. Four versions used another pair. Which exact hashes and initial-plug names should be independently investigated?

## Implementation and evidence limits
`scripts/audit_weapon_frame_candidates.py` now reports a uniquely most-common socket-type pair and lists exceptional **exact item hashes**, names, socket positions, socket-type hashes, initial-plug hashes and names. A tie or invalid socket-type hash fails closed instead of inventing a standard. At most 50 examples are printed, with an uncapped exception count.

Every exceptional record explicitly sets `active_frame_verified: false` and `current_acquisition_verified: false`. A different socket-type pair is a **definition-structure anomaly**, not proof of a distinct playable intrinsic, Champion effect, enhanced trait or obtainable roll.

Synthetic regression tests cover a unique dominant pair, a tie and a boolean socket-type hash. The live outlier identities must be read from the new extended synchronization artifact or a verified job log before being treated as observed.

## Official references
- [Bungie socket-entry definition](https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html)
- [Bungie item-plug definition](https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html)
- [Bungie Update 9.7.0, 9 June 2026](https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0) (frame-specific anti-Champion effects and Artifact rules)
- [Bungie Update 9.7.0.6, 20 October 2026](https://www.bungie.net/7/en/News/Article/destiny_2_update_9_7_0_6) (latest official hotfix found as of this audit; Eververse only)

## Next steps
1. Verify current GitHub Actions tests and extended manifest artifact; extract the four exact hashes and both initial-plug identities.
2. Compare the exceptional socket-type definitions with the dominant pair and independent weapon frame references.
3. Only promote a weapon to a legal Artifact-first synergy candidate when its active intrinsic, obtainable perk sockets, enhancement status and game-mode rules are independently supported.
4. Preserve the 45 historical candidates. Do not report theoretical damage/TTK/DR/cooldown outputs as gameplay measurements.

## Live exact-hash results — verified 29 October 2026, 18:17 UTC
[Extended workflow run 40929129319](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40929129319) completed **success** on source commit `2b3045f`. The job log reports manifest `245114.26.10.13.2000-1-bnet.66137`, dominant socket-type pair `1215804696,1215804697`, and **exactly four** exceptions. Uploaded artifact `12922400772` contains 94,273,196 bytes.

| Exact item hash | Weapon name | Socket indexes | Socket-type hashes | Initial plugs (manifest names) |
| --- | --- | --- | --- | --- |
| `534775659` | PLUG ONE.1 (Adept) | 3,4 | 1215804696 / 1215804696 | Bottomless Grief (`4252909580`); Backup Plan (`1600092898`) |
| `1681583613` | Ergo Sum | 4,6 | 3530202021 / 1215804696 | Wave Sword Frame (`289811733`); Transcendent Duelist (`2963428707`) |
| `2200470033` | Cull's Shadow | 1,4 | 63353896 / 1215804697 | Blades of Unmaking (`1980732122`); Soulforge (`695800688`) |
| `2816212794` | Bad Juju | 3,6 | 1215804697 / 1215804697 | Hip-Fire Grip (`1866048759`); Full Auto Trigger System (`4267945040`) |

**New interpretation:** This live result provides direct counterexamples to treating every `frames`-labelled initial plug as a weapon archetype. `Backup Plan`, `Hip-Fire Grip`, and `Full Auto Trigger System` are names of weapon traits or controls, not sufficient evidence of an intrinsic frame. `Ergo Sum` mixes `Wave Sword Frame` with `Transcendent Duelist` in different socket-type families. `Cull's Shadow` has two distinctly named initial plugs in a separate exceptional type pair. These are **manifest label/role ambiguity examples**, not proof that any of these plugs are simultaneously active or that a roll is currently obtainable.

[GitHub Actions test run 40929153342](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40929153342) completed successfully; direct job log reports **158/158 passing tests**, including three new regression tests. The four exact hashes are now priority manual frame-role cases, not newly certified builds.
