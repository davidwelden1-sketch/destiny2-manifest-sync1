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
