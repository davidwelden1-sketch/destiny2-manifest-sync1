# Intrinsic anti-Champion weapon-frame rules — 2026-10-29

**Source (official Bungie, 2026-06-09):** https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0

## New evidence and why it matters

Update 9.7.0 removes anti-Champion Artifact mods and assigns intrinsic anti-Champion behavior by weapon archetype, with more-specific weapon-frame exceptions. This is a **game-wide legality dimension** independent of weapon perk sockets. The frame-specific rule must override the generic archetype rule; e.g. an Adaptive-class Vortex sword has **Overload** by the named Vortex sword exception, not Barrier by the generic Adaptive rule. This example is a rule illustration, **not a claim that any particular item has that exact combination of labels**.

Base archetypes: Aggressive/High Impact → Unstoppable; Precision/Adaptive → Barrier; Lightweight/Rapid-Fire → Overload. The patch lists 19 weapon-type-specific frame combinations plus Dynamic Heat Weapons and Balanced Heat Weapons as Overload. The repository's `simulator/champion.py` is a strict, pure lookup over these patch rules. It does not query the manifest or claim a particular item actually possesses a frame.

**Crucial evidence blocker:** `itemSubType`, a randomized plug set, and a plug-category label are not sufficient to certify the weapon's active frame. Exact-hash item intrinsic/frame identification and live item state are required before assigning an actual weapon its champion behavior. Unknown frame/type combinations fail closed; base archetype results without verified frame are marked provisional. No damage, stun duration, cooldown, TTK, DPS or uptime is inferred.

**Artifact scope:** Bungie says Artifacts are disabled in Competitive and Trials. Intrinsic weapon anti-Champion capabilities do not establish Artifact perk legality or any damage bonus.

**Preservation:** Historical 45 candidate shells and S001–S288 findings are unchanged. Future work: build exact-item-hash intrinsic frame evidence map and compare actual current acquisition and enhanced trait availability; use frame rules only after verifying weapon-type/frame pair.
