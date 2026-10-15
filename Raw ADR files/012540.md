## Context
This change introduces client-side NIP-05 verification for user profiles and integrates verification status into contact search ranking and profile-related UI. It touches both the messaging experience (contacts and profile views) and the settings experience (profile editing), but reuses existing data storage primitives.

## Goals / Non-Goals
- Goals:
  - Follow the NIP-05 specification for verifying internet identifiers against pubkeys using \/.well-known\/nostr.json.
  - Persist verification status so that UI components can read a single, consistent source of truth.
  - Prefer verified identities when presenting contact search results and clearly mark invalid identifiers.
  - Avoid implying verification where none has occurred, especially in profile views.
- Non-Goals:
  - Implement server-side NIP-05 verification or any relay-side changes.
  - Replace existing profile resolution or relay discovery logic beyond adding verification hooks.
  - Add new settings for NIP-05 management beyond display and existing profile editing.

## Decisions
- Perform NIP-05 verification in the browser using standard fetch requests to \/.well-known\/nostr.json, accepting that CORS failures will appear as network failures and be treated as "unknown" verification status.
- Cache verification results in the profile storage layer alongside existing metadata, using a TTL aligned with profile metadata TTL to balance freshness with network cost.
- Use a small in-memory cache in the verifier to avoid repeated lookups during a single session, especially for top search results.
- Treat  as a special case in UI, displaying it as , while preserving the raw identifier in storage and verification logic.
- In Manage Contacts search, verify NIP-05 for only the top N results and re-rank results so that verified identifiers appear first, followed by unknown, then invalid.
- In the Profile modal, show NIP-05 as plain text without a checkmark to avoid overstating trust; in search results, use a green checkmark for verified NIP-05 and an explicit "not verified" icon for identifiers proven invalid for that key.

## Risks / Trade-offs
- NIP-05 verification depends on third-party domains correctly serving CORS headers; failures will surface as "unknown" status, which may confuse users if their identifier is actually valid.
- Additional HTTP requests for NIP-05 verification can increase latency and bandwidth usage, especially during search; limiting verification to top results and caching mitigates this.
- Caching verification status in profile storage can serve slightly stale information until TTL expiry, but this is acceptable for identity hints that are not security guarantees.

## Migration Plan
- Introduce new profile fields for NIP-05 verification status in the client-side store without requiring schema migrations that break existing IndexedDB data.
- Default previously cached profiles to an "unknown" verification state; verification will be performed lazily on profile resolution or when search interacts with a profile.
- Roll out UI changes that read from the new verification fields but degrade gracefully when the status is missing.

## Open Questions
- Should we surface NIP-05 verification status elsewhere in the UI (e.g., chat headers or contact list rows) beyond search results and settings, or keep the scope to the locations described here?
- What TTL window is acceptable for cached NIP-05 verification (e.g., 24 hours vs. shorter), given the trade-off between freshness and network cost?
