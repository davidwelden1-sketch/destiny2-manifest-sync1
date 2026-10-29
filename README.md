# Destiny 2 Manifest Sync

Official Bungie Destiny 2 manifest indexing pipeline for the Build Lab.

## Run
Open Actions > Sync Bungie Manifest > Run workflow. Also scheduled daily at 06:23 UTC. GitHub Actions must be enabled for the repository.

The Python script retrieves the public manifest, downloads English DestinyInventoryItemDefinition, and produces two files: `manifest_metadata.json` and `inventory_index.json`. GitHub Actions uploads them as a 30-day artifact rather than committing a large dataset. No Bungie API key required for the public manifest endpoint.

## Provenance and limits
Metadata includes manifest version, retrieval timestamp, source URL, SHA-256 checksum and item count. Inventory metadata is **not** measured PvP/PvE damage, cooldown, buff stacking, legal perk roll, or artifact selection evidence. Those need separate validated datasets and tests. A successful workflow run is required before considering the import verified.
