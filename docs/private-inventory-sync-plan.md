# Private Bungie inventory synchronisation (setup specification)

Status: NOT CONNECTED. No Bungie OAuth application, user consent, credentials or automatic inventory refresh has been configured.

## Security boundary
This repository is PUBLIC. Never commit Bungie membership IDs, item-instance inventory snapshots, access tokens, refresh tokens, client secrets, or private API responses. Do not upload private snapshots as public GitHub Actions artifacts or paste tokens into issues or chat.

## Proposed architecture
1. User registers a Bungie developer application and authorises the inventory-reading OAuth scopes. DIM's authorisation is separate and cannot be reused.
2. A scheduled GitHub Actions job uses GitHub Actions encrypted secrets for the app client credentials and refresh token. Use least-privilege scopes, rotate refreshed credentials securely, and stop with an explicit failure if token rotation cannot be persisted. GitHub Actions secrets are not automatically mutable by a running workflow.
3. Call Bungie's authenticated Destiny 2 profile and character inventory endpoints with the necessary inventory/equipment/instance/socket/stat components. Respect throttling, privacy settings, maintenance and component errors.
4. Store encrypted, timestamped inventory snapshots in a PRIVATE destination. Do not store them in this repository. Google Drive uploads require a separate, authorised service identity or OAuth connection; the ChatGPT Drive connector alone does not grant GitHub Actions access.
5. Track sync time, manifest version, completeness, item counts, and error status. Do not overwrite a valid snapshot with partial data. Alert when OAuth expires or data is stale.
6. Prometheus reads the most recent successfully verified snapshot and distinguishes it from live inventory.

## Activation blockers
- Bungie developer application registration and OAuth redirect configuration
- One-time user consent
- Safe token refresh persistence (not merely an expiring access token)
- A private destination with suitable service credentials
- A working scheduled workflow with verified successful end-to-end read/write

No live inventory is being synchronised by this specification alone.
