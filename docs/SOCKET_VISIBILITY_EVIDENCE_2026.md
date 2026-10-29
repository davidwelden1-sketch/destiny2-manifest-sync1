# Socket default visibility and runtime evidence gate — 2026-10-29

## Newly sourced structural limitation

Bungie's official `DestinyItemSocketEntryDefinition` schema says `defaultVisible` is the *default* socket visibility. The documentation explicitly warns that an item **instance's runtime state can override it** and that legacy sockets can remain defined for infrastructure purposes. Therefore even exact-hash, distinct-randomized-socket, `currentlyCanRoll=true` pairs may include hidden/legacy socket candidates and cannot be called playable rolls.

Primary: https://bungie-net.github.io/multi/schema_Destiny-Definitions-DestinyItemSocketEntryDefinition.html

Bungie's `Destiny.SocketPlugSources` enum further says plug availability can depend on inventory, character/profile plug sets, and runtime reusable plugs; in some cases runtime `DestinyItemSocketsComponent.sockets.reusablePlugs` is the only authoritative source. Do not equate manifest plugset membership with instance selectable plugs.

Primary: https://bungie-net.github.io/multi/schema_Destiny-SocketPlugSources.html

## Code change and conservative query

- `scripts/sync_extended.py` preserves `defaultVisible`, `plugSources`, and `preventInitializationOnVendorPurchase` from each Bungie socket definition, without changing historical rows.
- `scripts/build_socket_candidates.py` propagates those fields, preserving unknown values as `null` rather than assuming visible or vendor-initialized.
- `scripts/query_weapon_pairs.py --default-visible-only` requires both candidate randomized sockets to be **explicitly** `defaultVisible=true`; it can be combined with `--currently-rollable-only`. The result still reports runtime state, roll legality, enhanced legality and acquisition as **unverified**. The normal historical query remains available.
- The summary counts true, false and unknown default visibility across randomized weapon socket entries. Five synthetic regression tests cover explicit visibility, hidden/unknown filtering, malformed metadata, counts and invalid options.
- Extended GitHub Actions publishes a separate strict visibility + current-roll report for Dimensional Shift + Collective Action (plug hashes 1767911158 and 2562668800). Its live candidate count must be read from a completed workflow, not predicted.

## Practical effect on three-class build research

This is an evidence-quality improvement, **not** a discovered damage increase. Reassess Lotus-Eater, Keraunios, and all game-wide trait-pair candidates against both current-roll flags and socket visibility. Before a Hunter, Titan or Warlock build is certified, check runtime sockets, acquisition, enhanced traits, Artifact legality and observed activation/kill attribution. In PvP, Competitive and Trials disable Artifacts per Bungie 9.7.0 (2026-06-09): https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0 .

As of the research pass, the latest located Bungie update is 9.7.0.6 (2026-10-20; Eververse fix): https://www.bungie.net/7/en/News/Article/destiny_2_update_9_7_0_6 .

No new measured DPS, TTK, damage resistance, cooldowns or playable roll certification is asserted. Historical 45 candidates remain unchanged.
