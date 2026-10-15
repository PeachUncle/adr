## Context
nospeak uses a native Android foreground service to provide near-realtime background message delivery when background messaging is enabled. The service maintains one WebSocket connection per configured messaging relay and uses OkHttp WebSockets.

On Android 14+ devices, frequent background wakeups (for example, from aggressive WebSocket pings and from non-essential network fetches such as avatar downloads) can meaningfully impact battery life. At the same time, nospeak is a messaging app and must remain near-realtime; polling-based delivery is not acceptable as the primary mechanism.

This change introduces an **adaptive energy profile** for the foreground service:
- Use a shorter ping interval when the user is active (unlocked / charging).
- Use a longer ping interval when the device has been locked for a short grace period and is not charging.

## Goals
- Reduce background wakeups while keeping near-realtime delivery.
- Keep connections to **all** configured messaging relays (typically 1–3) while background messaging is enabled.
- Treat lockscreen-visible as locked until the user unlocks.
- Avoid notification floods and preserve existing backlog guard behavior.
- Provide minimal debug logging (debug builds only) to support tuning.

## Non-Goals
- Adding new UI settings for ping intervals.
- Switching to polling mode (WorkManager / AlarmManager) for message delivery.
- Introducing new delivery guarantees beyond existing relay best-effort behavior.

## Decisions
- Device-state detection:
  - Use Android OS signals in the foreground service to infer device lock state.
  - Treat the device as "unlocked" only when the OS indicates the user is present (e.g., `ACTION_USER_PRESENT`).
  - Use a 60-second grace window after `ACTION_SCREEN_OFF` before switching to the locked profile to avoid churn from quick screen toggles.
  - Use charging state to force the active profile (charging devices use the shorter ping interval).

- Energy profiles:
  - **Active profile** (unlocked OR charging OR within grace period): WebSocket ping interval = **120 seconds**.
  - **Locked profile** (screen off for >60 seconds AND not charging): WebSocket ping interval = **300 seconds**.

- Connection behavior:
  - OkHttp ping interval is configured per OkHttpClient instance; switching profiles requires rebuilding the client and restarting sockets.
  - Relay coverage remains unchanged: the service continues to connect to all configured relays.
  - Reconnection backoff behavior remains unchanged.

- Message correctness:
  - The service MUST NOT rely on a strict outer gift-wrap `created_at` `since` filter because gift-wrap timestamps may be backdated.
  - The existing notification baseline/backlog guard continues to prevent notification floods during reconnects.

- Background enrichment:
  - While in the locked profile, skip non-essential operations that can trigger extra network/CPU work (e.g., avatar fetching and shortcut publishing).
  - Continue decrypting and notifying as required for message delivery semantics.

- Debug logging:
  - Emit a single-line profile transition log message only when the profile actually changes (active↔locked), and only in debug builds (`BuildConfig.DEBUG`).

## Alternatives Considered
- Polling delivery (WorkManager / AlarmManager): rejected because near-realtime delivery is required.
- Connecting to fewer relays while locked: rejected because the project does not want to trade reliability for energy savings.
- Adding `since` filters on gift-wrap subscriptions: rejected due to backdated `created_at` behavior.

## Risks / Trade-offs
- Restarting sockets to change ping intervals can cause a brief reconnect window; this is acceptable because background messaging is best-effort and the service already includes reconnection logic.
- Some OEMs still restrict network in deep idle even for foreground services; this change reduces energy usage but does not guarantee delivery under all device policies.

## Migration Plan
- No migration steps are required. The behavior changes only when background messaging is enabled.
- Rollback is straightforward: revert to a single, fixed ping interval.

## Open Questions
- None.
