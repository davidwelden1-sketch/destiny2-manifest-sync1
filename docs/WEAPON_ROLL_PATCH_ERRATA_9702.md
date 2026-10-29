# Bungie 9.7.0.2 roll corrections — catalog legality guardrails

**Official source:** Bungie, *Destiny 2 Update 9.7.0.2*, 23 June 2026:
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2

**Evidence class:** official patch text. Not manifest item-hash validation,
not measured gameplay, and not proof of present drop eligibility.

## Why this matters for the game-wide index

1. Bungie fixed **Europa and Moon Rocket Launchers** dropping with **Lead from Gold**.
   The perk was unintended for those weapons (reserved for Special-ammo weapons);
   affected instances were updated to **Impromptu Ammunition**. Do not recommend
   a currently obtainable Europa/Moon rocket roll with Lead from Gold merely
   because an archived database or old item version lists it.
2. Bungie fixed some **Adept raid weapons** dropping with trait pools out of
   sync with their base versions, and updated the affected Adepts, including
   instances already in player inventories. An old observed roll or static
   item hash is insufficient evidence of current legality.
3. Bungie fixed **Cynosure Rocket Launcher** high-tier versions not dropping
   extra traits. Socket membership alone does not establish the count or
   tier-dependent availability of extra trait selections.
4. Bungie fixed **Lingering Dread** not benefiting from **Discord**.
   This is a runtime activation correction, not a change that can be inferred
   from static socket membership.
5. Bungie fixed **Unto the Breach** not granting its Artifact benefits on
   Prismatic and fixed an Artifact duplicate-selection bypass. Historical
   activation reports before 23 June must be versioned; only one active
   Artifact with legal perk selections is modeled. Competitive and Trials
   disable Artifacts under Bungie 9.7.0 (9 June 2026):
   https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0

## Research protocol

- First resolve exact item hash, variant and randomized socket membership
  from the downloaded manifest, **not** a merged display-name pool.
- Then resolve **current drop source**, enhancement sockets and trait
  selection constraints from dated, corroborated evidence.
- For a named roll affected by this errata, demand post-fix evidence.
- For Adepts, compare the matching base/Adept *same-era* definitions rather
  than assuming they share sockets or are permanently different.
- For runtime perk effects, test event ownership, timing and actual damage
  separately; structural roll evidence cannot prove activation.
- Record explicit `unverified` where current availability, enhancements or
  activation are missing. Do not synthesize DPS, PvP TTK or cooldowns.

**Live evidence blocker as of 29 October 2026:** no per-hash post-fix
drop-table and enhancement-socket certification is included in this
document. The October 13 manifest can establish structural definitions,
not current acquisition and measured gameplay.

**Latest official update located:** Bungie 9.7.0.6, 20 October 2026
(Eververse-only fix):
https://www.bungie.net/7/en/News/Article/destiny_2_update_9_7_0_6
