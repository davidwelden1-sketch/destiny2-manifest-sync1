# Weapon randomized socket plug-category whitelist audit — 2026-10-29

## Source and purpose
Bungie's official DestinySocketTypeDefinition schema defines a `plugWhitelist` of category hashes. A plug item's `DestinyInventoryItemDefinition.plug.plugCategoryHash` is compared with that whitelist. **An empty whitelist permits any category.** This is distinct from `randomizedPlugSetHash`, `currentlyCanRoll`, `defaultVisible`, and live item socket state.

Official schema: https://bungie-net.github.io/multi/schema_Destiny-Definitions-Sockets-DestinySocketTypeDefinition.html
Official plug definition: https://bungie-net.github.io/multi/schema_Destiny-Definitions-Items-DestinyItemPlugDefinition.html

## New pipeline
- `scripts/sync_extended.py` exports the Bungie `DestinySocketTypeDefinition` family to `socket_types.json` and each inventory plug's category hash and identifier to `items_extended.json`.
- `scripts/audit_weapon_socket_categories.py` evaluates randomized weapon socket plug memberships against the socket-type whitelist.
- It separates whitelisted, unrestricted (empty whitelist), non-whitelisted, missing plug definition, missing plug category, and missing or malformed socket-type evidence.
- It reports plug-category identifiers and the single hidden-default-socket example(s), so elemental sockets can be distinguished from trait-like sockets without guessing from position.
- Seven synthetic regression tests cover each evidence state and exclude armor. GitHub CI validates tests. The extended manifest workflow runs the live audit and uploads its JSON artifact.

## Interpretation and blockers
A whitelisted plug is **category-compatible in the definition**; it is not necessarily a currently obtainable roll or a selectable enhanced trait. Non-whitelisted membership is a precise **definition-evidence conflict**, not proof of a game bug or impossible existing item. A socket can be overridden by live instance data; enhancement and acquisition require separate sources. Do not claim measured damage, DPS, TTK, DR or uptime from this audit.

The October 2026 source register preserves the 45 historical candidate shells; this audit expands evidence across the full game-wide weapon index. Artifact selection remains one active Artifact, at most seven legal perks; Bungie disables Artifact effects in Competitive and Trials.

Relevant Bungie update (June 9, 2026): https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0
Latest located patch (October 20, 2026): https://www.bungie.net/7/en/News/Article/destiny_2_update_9_7_0_6
