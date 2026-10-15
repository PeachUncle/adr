## Context
The 2025-12-22 energy profiles change introduced adaptive ping intervals (120s active, 300s locked) to reduce battery drain. However, the implementation triggers full WebSocket connection restarts when energy profiles change, including:
- Screen-off → locked profile (after 60s grace period)
- Screen-on/user present → active profile
- Power connected/disconnected → profile switches

Each connection restart requires TLS handshakes and network initialization, which consumes more energy than maintaining stable connections with longer ping intervals.

The original spec correctly prohibits connection restarts during the 60-second grace period but does not extend this prohibition to all profile changes. This causes worse battery drain than the previous fixed 30-second ping implementation.

## Goals
- Eliminate connection restarts triggered by energy profile changes
- Maintain stable WebSocket connections across device state transitions
- Reduce battery drain by avoiding unnecessary TLS handshakes
- Apply ping interval changes lazily to new connections only
- Preserve existing reconnection backoff behavior

## Non-Goals
- Removing energy profile concept entirely
- Changing ping interval values (120s active, 300s locked remain correct)
- Modifying notification behavior or message delivery semantics
- Adding new UI or user-visible settings

## Decisions
- **Lazy profile application**: When energy profile changes, update the `OkHttpClient` reference to use the new ping interval. Existing WebSocket connections continue using their current interval until they naturally disconnect and reconnect (due to network issues, relay restart, etc.). New connections created via `onSocketClosedOrFailed` retry logic will use the updated client and therefore get the new ping interval.

- **Preserve existing client lifecycle**: The `buildOkHttpClient()` method and client rebuilding pattern remain unchanged. Only the call to `startRelayConnections()` from `evaluateAndApplyEnergyProfile()` is removed.

- **Grace period unchanged**: The 60-second grace period before entering locked profile is preserved. Profile evaluation still respects charging state and device lock state.

## Alternatives Considered
- **Immediate ping interval update on existing connections**: Rejected because OkHttp `pingInterval` is configured per `OkHttpClient` instance and cannot be changed on existing WebSocket connections without restarting them.
- **Force periodic connection rotation**: Rejected because this would cause more frequent restarts than necessary.
- **Revert to fixed 30-second ping**: Considered, but loses energy savings during long idle periods. The lazy application approach preserves energy benefits without expensive restarts.
- **Increase ping interval further without profiles**: Rejected because adaptive profiles provide flexibility for different device states.

## Risks / Trade-offs
- **Delayed ping interval application**: New ping interval applies only when connections naturally reconnect, which could take minutes or hours in stable network conditions. This is acceptable because:
  - The alternative (forced restarts) causes worse battery drain
  - Connections will eventually adopt the correct interval during normal operation
  - Users can manually disable/enable background messaging to force connection restarts if needed
- **Mixed ping intervals during transition**: Some connections may temporarily use different ping intervals during profile transitions. This is acceptable and resolves naturally.

## Migration Plan
- No migration steps required. The behavior changes only when energy profile conditions change.
- Rollback is straightforward: restore the `startRelayConnections()` call in `evaluateAndApplyEnergyProfile()`.

## Open Questions
- None.
