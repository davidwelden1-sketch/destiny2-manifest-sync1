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

## Live Bungie manifest results — 2026-10-29 12:23 UTC

GitHub Actions extended sync run [40872545511](https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/actions/runs/40872545511) **completed successfully**, uploaded artifact `12895719930` (94,194,661 bytes), and retrieved manifest `245114.26.10.13.2000-1-bnet.66137`. The newly downloaded `DestinySocketTypeDefinition` family contains **1,874 definitions**.

The direct workflow log reports **97,283 randomized weapon plug memberships classified `compatible_whitelist`**, with no missing, malformed, non-whitelisted, or unrestricted memberships reported in this scope. This means the socket whitelist is **non-discriminating for the currently indexed randomized weapon membership population**, not that all rolls are obtainable or all memberships are trait perks.

Top raw plug category identifiers by *membership occurrences* (not unique plugs or weapon rolls): `frames` 37,411; `magazines` 23,669; `barrels` 23,524; `tubes` 3,129; `magazines_gl` 2,469; `batteries` 2,084. These are Bungie metadata identifiers, not independently validated gameplay slot roles. In particular, **do not assume every `frames` membership is a weapon frame or every randomized plug is a damage trait** without additional per-plug inspection.

The hidden Ergo Sum item `1681583613`, socket index 3, socket type `1466776700`, has three compatible plug entries: Solar `2273483223`, Void `3728733956`, Arc `4126105782`. All share plug category hash `1466776700` and category identifier `v300.weapon.damage_type.energy`. This is strong manifest-level evidence of an **elemental damage-type socket**, not a normal perk trait column. Runtime visibility and swapping remain unverified.

The audit successfully separates source categories, but **does not yet certify two active trait columns, enhanced perks, acquisition, damage ownership, or measured combat output**. Next step: examine plug categories and socket indices for known trait hash pairs and classify socket role with exact-hash and live-instance corroboration.
