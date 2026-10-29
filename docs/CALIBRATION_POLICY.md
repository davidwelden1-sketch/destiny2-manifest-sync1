# Evidence and calibration policy

This repository is an engineering framework, not a certified current-sandbox damage database.

## What the Bungie manifest establishes

Inventory item hashes, item metadata, socket definitions, fixed initial plugs, and referenced plug-set candidates are structural evidence. A candidate plug hash is **not** proof that a perk can currently roll on a weapon, that it can be enhanced, or that the weapon is obtainable.

## What a TTK result establishes

The simulator calculates a conditional result from supplied health, damage, RPM and multipliers. It assumes a constant firing cadence unless an explicit event sequence is supplied. It does not model Destiny network latency, burst timing, damage rounding, perk activation, falloff, resilience or special sandbox rules without calibrated inputs.

## Measurement intake requirements

Record the exact weapon hash, activity, target type and health or resilience assumptions, damage precision/body values, observed date, source URL, relevant perks, buffs/debuffs and Artifact status. Retain the raw observation separately from any inferred multiplier.

A sourced base damage value does **not** certify a composite build or stacking combination. Each interaction requires its own evidence. No official or measured label should be assigned to synthetic test values.

## Current blockers

Current-game measured damage, live Artifact effects, stack-group precedence, cooldown rates, and legal weapon rolls remain incomplete. Comparative rankings are provisional until calibrated and checked against current sandbox observations.
