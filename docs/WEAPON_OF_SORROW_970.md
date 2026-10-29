# Weapon of Sorrow status ownership: 9.7.0 evidence gate

Source: Bungie, Destiny 2 Update 9.7.0 (2026-06-09):
https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0

## Official post-patch rules
- **Corruption**: short-duration, stackable damage-over-time, sourced by Thorn,
  Touch of Malice, and Necrochasm.
- **Potent corruption**: longer-duration, non-stacking damage-over-time that
  generally ramps, sourced by Necrotic Grip, Spirit of the Necrotic, and
  Osteo Striga.
- Both status families can coexist on the **same target**.
- Ordinary Corruption must **not** extend Potent corruption duration.
- Potent corruption must **not** erase ordinary Corruption stacks.
- Freezing a target must **not** erase Weapon of Sorrow Corruption.

These are official behavior constraints, **not** numerical damage measurements.
The source also says the new names clarify the distinction; they do not imply
a new base damage multiplier.

## Original cross-class control
- Warlock: equip Thorn (or Necrochasm) plus Necrotic Grip, and use a Stasis
  freeze source to test ordinary + potent coexistence across freeze.
  Confirm the actual armor trigger and weapon-kill propagation separately.
- Hunter/Titan: same weapon and freeze sequence without Necrotic Grip is a
  negative control. Do not invent cross-class access to Necrotic Grip.
- A single Guardian cannot equip Thorn and Osteo Striga simultaneously;
  they are both Exotic weapons. Do not treat their separate status sources as
  a legal dual-weapon loadout.
- Choose **one** active Artifact and no more than seven legal perks. No
  Artifact-triggered Corruption damage, freeze ownership, or subclass energy
  gain is certified from this patch. Artifact effects are disabled in
  Competitive and Trials from 9.7.0 onward.

## Reproducibility matrix
1. Ordinary Corruption alone; record tick damage, stacks, target and duration.
2. Potent corruption alone; record tick damage, ramp and duration.
3. Both applied in both orders; test independent durations and stack counts.
4. Freeze before, during, and after both statuses; confirm persistence.
5. Kill while each effect is active; distinguish weapon hit, DoT and
   spreading effect final-blow attribution.
6. Repeat with and without Necrotic Grip and with other eligible Weapons of
   Sorrow. Use dated PvE and PvP captures, target class, health and sandbox.
7. Do not multiply the two DoT families or infer proc-on-kill effects until
   measured and independently reproduced.

## Evidence status
Official: taxonomy, coexistence, no cross-extension/erasure, freeze persistence.
Unverified here: per-tick numbers, stacking cap, duration, damage ownership,
final-blow attribution, Artifact synergies, activity scaling and uptime.
