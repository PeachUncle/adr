## Context

The initial history sync flow runs after login and blocks the UI with a modal until completion. Currently:
- Individual batch fetches have 30s timeouts
- Relay connection waits have 10s timeouts
- But there's no overall flow timeout - it can run indefinitely
- No error UI exists - failures close the modal silently
- Users cannot dismiss the modal or retry

This causes poor UX when relays are slow, unresponsive, or the user has network issues.

## Goals / Non-Goals

**Goals:**
- Provide a 5-minute hard limit on the sync flow
- Display actionable error information including which relays failed
- Allow users to retry failed syncs
- Allow users to skip sync and proceed to use the app
- Allow users to dismiss the modal after 2 minutes and let sync continue in background
- Notify users when background sync completes

**Non-Goals:**
- Redesign the sync flow architecture
- Add per-step timeouts (existing timeouts are sufficient)
- Implement sophisticated retry strategies per relay
- Add persistent error logging/reporting

## Decisions

### Decision: Global timeout via Promise.race
The sync flow will be wrapped in `Promise.race` with a 5-minute timeout promise. This keeps the timeout logic isolated from the step-by-step sync logic.

**Alternatives considered:**
- Per-step cumulative timeout tracking: More complex, harder to reason about total time
- AbortController pattern: Overkill for this use case, harder to integrate with existing async patterns

### Decision: Track relay errors during sync
Each step that interacts with relays will catch errors and accumulate them in the sync store. Errors include the relay URL, error message, and which step failed.

**Alternatives considered:**
- Only track overall error message: Less useful for debugging, users can't identify problematic relays
- Track in AuthService only: Less reactive, harder to update UI in real-time

### Decision: Background mode via store flag
When user clicks "Continue in background", the sync store sets `isBackgroundMode: true` and the modal closes. The sync flow checks this flag and continues silently.

**Alternatives considered:**
- Cancel sync on dismiss: Poor UX, user loses progress
- Web Worker: Overkill, sync already runs async

### Decision: New minimal toast system
Create a simple toast store and component for in-app notifications. Toasts auto-dismiss after configurable duration.

**Alternatives considered:**
- Browser notifications: Too intrusive for "sync complete" messages
- No notification: Users won't know background sync finished
- Use existing modal system: Toasts are less intrusive and more appropriate

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| 5 minutes may be too long for impatient users | 2-minute dismiss option addresses this |
| 5 minutes may be too short for slow networks | Skip option lets users proceed; sync can be manually triggered later |
| Relay errors may be cryptic | Include step context ("during history fetch") |
| Toast system adds code | Keep it minimal (<100 lines total) |

## Migration Plan

No migration needed. This is additive functionality that improves existing behavior:
1. Existing sync flows will now have a timeout safety net
2. Users who previously waited indefinitely can now recover
3. No data model changes, no breaking changes

## Open Questions

None - requirements have been clarified with the user.
