# ADR 001: Concurrent Vote Completion Handling

## Status

Accepted

## Context

When transitioning between game rounds, players vote for the next mystery. Once all active players have voted, the system needs to:
1. Tally the votes to determine the winning mystery
2. Distribute character roles for the new mystery
3. Update the session state to reflect the new round

### The Problem

When multiple players vote nearly simultaneously, each vote request independently checks if all players have voted. This creates a "thundering herd" scenario where multiple API calls see the condition as met and all attempt to trigger the next round transition:

- Player A votes → 2/3 players → does nothing ✓
- Player B votes → 3/3 players → triggers next-round ✓
- Player C votes → sees 3/3 players → ALSO triggers next-round ❌
- Player B's request completes → still sees 3/3 → ALSO triggers next-round ❌

This resulted in:
- Multiple concurrent calls to `/api/sessions/{id}/next-round`
- Multiple concurrent calls to `/api/sessions/{id}/distribute-roles`
- Database contention causing 500/503 errors
- Race conditions in role assignment

### Why Not Prevent Concurrent Calls?

**Option Rejected: Database lock on vote completion**
- Adding a `next_round_triggered` flag would require schema changes
- Would need careful cleanup if errors occur
- Adds complexity to handle edge cases (unvoting, vote changes)

**Option Rejected: Change vote threshold to exact match**
- Changing `>=` to `===` reduces but doesn't eliminate the problem
- Network timing means multiple requests can still see the exact threshold simultaneously
- Doesn't handle the fundamental concurrency issue

## Decision

We accept that multiple concurrent calls to `next-round` will occur when votes complete nearly simultaneously. Instead of preventing this, we make the entire flow **idempotent and graceful**:

### 1. Atomic Lock at Role Distribution Level

The `distribute-roles` endpoint already has an atomic database lock using conditional UPDATE:

```sql
UPDATE game_sessions 
SET status = 'playing', current_mystery_id = :mysteryId
WHERE id = :sessionId AND current_mystery_id != :mysteryId
```

Only one concurrent call succeeds; others get no rows updated and return early with "Already processing".

### 2. Graceful Failure Handling in next-round

The `next-round` endpoint now:
- Wraps `tally-votes` in try/catch to handle transient errors
- Checks for "Already processing" response from `distribute-roles`
- Returns success if another request is already handling the transition
- Logs all concurrent attempts for monitoring

### 3. Vote Counting Remains Idempotent

The `tally-votes` endpoint simply counts whatever votes exist at call time:
- No side effects
- Safe to call multiple times concurrently
- Returns snapshot of current vote state
- Handles unvoting gracefully (if votes decrease after threshold, returns no winner)

### 4. Vote Recording Never Blocks on Errors

The `vote-mystery` endpoint:
- Records the vote first
- Then checks if threshold met
- Catches and logs errors from next-round trigger
- **Always returns success** for the vote itself
- Doesn't fail the player's vote if round transition has issues

## Consequences

### Positive

- **Simple**: No new database schema needed
- **Robust**: Handles network delays, unvoting, and timing variations
- **Scalable**: Works with any number of concurrent voters
- **Observable**: Extensive logging tracks concurrent calls
- **Fault-tolerant**: Vote always succeeds even if round transition fails temporarily

### Negative

- **Multiple API calls**: When 5 players vote simultaneously, could trigger 5 calls to next-round
- **Wasted work**: Only 1 distribute-roles succeeds; others return early
- **Log noise**: Need to distinguish expected "Already processing" from real errors

### Monitoring

Watch for:
- Frequency of "Already processing" responses (indicates concurrent calls)
- Any 500/503 errors that persist despite idempotency
- Cases where all next-round calls fail (requires manual intervention)

## Implementation Notes

### Key Code Changes

1. **next-round/route.ts**: Added try/catch for tally-votes, check for "Already processing" response
2. **vote-mystery/route.ts**: Added unvote support and comment explaining concurrent calls are expected
3. **distribute-roles/route.ts**: No changes needed - atomic lock already present
4. **lobby/page.tsx**: Switched from `/vote` + `mark-ready` to unified `vote-mystery` endpoint
5. **Deleted**: `mark-ready/route.ts` and `vote/route.ts` - obsolete after consolidation

### Unified Flow

Both lobby (round 1) and play page (round 2+) now use the same flow:
```
vote-mystery → (when all voted) → next-round → tally-votes → distribute-roles
```

Ready state is now **derived from votes** - a player is "ready" when they've voted. No separate `player_ready_states` tracking for game start logic.

### Testing Considerations

- Simulate rapid concurrent votes using multiple browser tabs
- Monitor logs during vote completion to verify graceful handling
- Test unvoting scenario (player unvotes after threshold met)
- Verify no 500 errors appear when 3+ players vote within 100ms

## Alternatives Considered

**Database transaction with explicit lock**
- Requires BEGIN/COMMIT support in Supabase
- More complex error handling if transaction fails
- Doesn't prevent external calls from trying concurrently

**Rate limiting on next-round endpoint**
- Doesn't solve the fundamental problem
- Could delay legitimate retries
- Adds configuration complexity

**Client-side coordination**
- Unreliable due to network timing
- Vulnerable to client bugs or malicious actors
- Breaks if client disconnects mid-vote

## Related Issues

- Original bug report: "Could not determine current mystery" errors
- Supabase 503 errors on rounds table queries
- 500 errors on tally-votes during concurrent calls

## References

- Idempotency patterns: https://stripe.com/blog/idempotency
- Distributed systems: "Designing Data-Intensive Applications" by Martin Kleppmann
- Database conditional updates for distributed locks
