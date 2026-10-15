nospeak uses `nostr-tools` relay connections for both real-time subscriptions and for publishing NIP-17/NIP-59 DM gift-wrap events. The current connection layer explicitly skips relay authentication and therefore cannot interoperate with relays that enforce NIP-42.

This change introduces NIP-42 client authentication in a way that is:
- Demand-driven (only performed when required by the relay).
- Bounded (no infinite retry loops).
- Observable (auth state is visible in the connection UI).

## Goals / Non-Goals
- Goals:
  - Support NIP-42 relay authentication for both reads (subscriptions) and writes (publishes).
  - Authenticate only when a relay challenges or rejects an operation with `auth-required:`.
  - Preserve existing messaging behavior (delivery confirmation windows, retry queue) while enabling auth-required relays to succeed.
  - Expose relay auth state to users so failures are diagnosable.
  - Use the existing session signer; if no signer exists, fail explicitly with `lastAuthError="Missing signer"`.
- Non-Goals:
  - Proactively authenticate to every relay on connect.
  - Add per-relay user configuration (allow/deny lists, manual auth toggles).
  - Persist auth state across app restarts (initially).
  - Update the Android-native background messaging service (if any) to support NIP-42; this may be addressed in a follow-up change.

## Decisions
### Use nostr-tools built-in NIP-42 support
`nostr-tools` `AbstractRelay` already implements the NIP-42 mechanism:
- The relay emits `['AUTH', <challenge>]`.
- The client responds with `['AUTH', <signed kind=22242 event>]`.
- `AbstractRelay` exposes `relay.onauth` (sign callback) and `relay.auth(...)`.

We will use these primitives rather than implementing raw websocket message handling.

### Demand-driven triggers
We will attempt authentication only when required:
- Primary: on receiving an `AUTH` challenge message from the relay.
- Secondary: when an operation fails with `auth-required:` (publish `OK false` reason or subscription `CLOSED` reason).

### Sticky auth requirement state (runtime)
Once a relay is observed to require auth, it remains marked as requiring auth across reconnects.
- Important nuance: on reconnect, relays generally require a new challenge before the client can send `AUTH`. `nostr-tools` resets the stored challenge on each `connect()`.
- Therefore a relay can be marked `required` even while the client cannot yet authenticate; the state remains `required` until a challenge arrives and authentication succeeds.

### Retry and loop prevention
- Publish flows: on `auth-required`, attempt auth (when possible) and retry the publish once.
- Subscription flows: on `auth-required` close reason, attempt auth (when possible) and re-subscribe once.
- A per-operation guard ensures we do not retry repeatedly on a misbehaving relay.

### Missing signer behavior
If authentication is required and there is no signer available for the current session:
- Set `authStatus='failed'`.
- Set `lastAuthError="Missing signer"`.

This provides a clear UI signal and avoids silent failures.

## UI / Observability
We will represent a relay’s auth state with one of:
- `not_required`
- `required`
- `authenticating`
- `authenticated`
- `failed`

The Relay Connections modal will show per-relay auth status and any last auth error.

The connection status control will:
- Use a green/yellow/red indicator.
- Display auth counts for connected relays only (for example, `Auth: 1/2`).

## Alternatives Considered
- Proactive auth on connect: simpler to reason about but increases signer prompts and violates the requirement to only auth when needed.
- Persisting auth status in localStorage: could be useful but risks stale UI state and is unnecessary for the initial interoperability goal.
- Manual per-relay auth toggles: adds UI and configuration complexity; postpone unless users request it.

## Risks / Trade-offs
- Some signers may prompt users when signing kind 22242 auth events, potentially increasing friction.
- Not all relays send `AUTH` challenges reliably; in that case, the client may record `required`/`failed` states and continue to fail on that relay.
- Retries consume time from bounded publish confirmation windows; we will treat auth+retry as part of the existing confirmation window, not as an extension.

## Migration Plan
- This is a client-only change.
- After implementation, test against at least one relay known to require NIP-42 for reads/writes (manual verification).

## Open Questions
- Should auth status be persisted across app restarts (per device) to make failures visible earlier?
- Should the Android-native background messaging service also implement NIP-42 (if it connects directly to relays)?
