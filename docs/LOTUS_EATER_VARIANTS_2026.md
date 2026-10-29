# Lotus-Eater 2026 variant and Void Breach dual-trigger audit (2026-10-29)

## Provenance and scope

This is an **unranked research experiment**, not a measured build. The official Bungie manifest was retrieved by successful [extended GitHub Actions run 40811578505](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40811578505), manifest version `245114.26.10.13.2000-1-bnet.66137`. Source-separated `item_socket_candidates.json` and `items_extended.json` were read from that run's uploaded artifact, not inferred from the player's inventory.

- **2026 S29 Lotus-Eater:** item hash `837298567` (UPGRADED) and `924095500` (non-upgraded). Both have identical *randomized socket membership* in the downloaded manifest. See [light.gg 837298567](https://www.light.gg/db/items/837298567/lotus-eater/) and [light.gg 924095500](https://www.light.gg/db/items/924095500/lotus-eater/).
- **2025 S26 Lotus-Eater:** item hash `3922217119`, with **different** randomized trait pools. See [light.gg 3922217119](https://www.light.gg/db/items/3922217119/lotus-eater/) and [Godroll.tv 3922217119](https://godroll.tv/3922217119/lotus-eater).
- New S29 trait socket 3 includes `Dimensional Shift` (plug hashes `1767911158`, `3182497402`); socket 4 includes `Collective Action` (`2562668800`, `3324494224`). Both memberships are in *different* randomized sockets. [Godroll.tv 837298567](https://godroll.tv/837298567/lotus-eater) independently indexes the same pairing.
- S26 has `Shoot to Loot` (socket 3) and `Reverberation` (socket 4); **neither is in the S29 randomized trait pools**. Conversely, S26 lacks `Dimensional Shift` and `Collective Action`. Do not combine S26 and S29 traits into an invented Lotus-Eater roll.
- The two S29 variants have identical indexed randomized socket membership; that does **not** prove identical acquisition routes, enhancement availability, or selectable rolls.

## Game-wide pair scan

The same two plug hashes (`1767911158` and `2562668800`) appear in **distinct randomized sockets on 16 weapon definitions representing 14 distinct display names**. Names: Elsie's Rifle, Seventh Seraph SI-2, Forthcoming Deviance, Forthcoming Deviance (Adept), Lotus-Eater (two S29 variants), Chivalric Fire, Vikala SMG4 (two variants), Reckless Oracle, Likely Suspect, IRONWOOD 03, Basso Ostinato, A Sudden Death, Vouchsafe, The Recluse. This is a **structural manifest candidate scan**, not 16 certified obtainable or enhanced rolls. The reproducible query is `python scripts/query_weapon_pairs.py --plug-a 1767911158 --plug-b 2562668800`.

## New activation hypothesis

A Void Breach pickup can **potentially activate two independent traits** on S29 Lotus-Eater: `Collective Action` grants a temporary damage bonus on elemental pickup, while `Dimensional Shift` makes **subsequent final blows** grant a Void Overshield after a Void Breach is collected. The pickup is not itself proof of an immediate overshield. Test both buff icons and exact timing independently; neither stacking nor uptime has been measured. [Godroll.tv](https://godroll.tv/837298567/lotus-eater) and [Shard or Keep](https://shardorkeep.com/db/items/lotus-eater-924095500) describe the perk triggers.

### Artifact-first PvE test (one active NPA Repulsion Regulator)

Seven *tier-legal* selections, **three T1 / two T2 / two T3**, according to [October 2, 2026 artifact index](https://totalapexentertainment.com/destiny-2-mot-artifacts/):

- T1: **Volatile Flow**, **Unto the Breach**, **Shatter Orbs**.
- T2: **Bricks from Beyond**, **Overload Grenades**.
- T3: **Supernova**, **Void Weapon Channeling**.

Conditional loop: apply Void debuff -> defeat debuffed target -> `Unto the Breach` may create Void Breach -> pick up Breach -> arm both weapon traits and `Supernova` -> secure a *subsequent* Lotus-Eater final blow -> check Overshield; separately test whether `Collective Action` and `Void Weapon Channeling` stack, conflict, or require different triggers. `Shatter Orbs` needs a matching shield; `Bricks from Beyond` needs its own powerful-combatant condition; `Overload Grenades` needs a Void grenade/Overload Champion. None is a guaranteed loop from a single kill. Avoid counting Volatile damage or a secondary explosion as a weapon kill without event evidence.

Three **unranked Exotic controls**: Hunter Nightstalker + Orpheus Rig (Tether-debuff control); Titan Sentinel + Second Chance (Shield Throw weaken/Breach control); Warlock Voidwalker + Nezarec's Sin (Void-final-blow regeneration control). Their ability cooldowns, kill attribution, damage ownership and Overshield behavior must be separately verified before calling any setup a complete build.

## Testing and limitations

Record: exact item hash; equipped Artifact and seven selections; source of initial Void debuff; Void Breach creation/pickup timestamp; buff icons; weapon final blow source (direct projectile vs explosion vs Volatile); Overshield application time/strength; Collective Action duration and damage with controlled target; Void Weapon Channeling state; class-specific Exotic trigger and ICD; reserve ammo spent; and PvE activity/difficulty. Compare no Artifact, one-perk and both-perk controls. **No gameplay measurement, TTK, DPS, DR or cooldown is claimed.**

Official [Bungie Update 9.7.0, June 9, 2026](https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0) disables Artifact effects in Competitive and Trials. Latest located [9.7.0.6, October 20, 2026](https://www.bungie.net/7/en/News/Article/destiny_2_update_9_7_0_6) addresses Eververse only. Current acquisition and enhanced socket eligibility remain blockers.
