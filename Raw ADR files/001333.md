# ADR-014: Auto-Reconnect Strategy

**Status:** Accepted
**Date:** 2024-10
**Updated:** 2025-11-11
**Deciders:** Development Team
**Related Issues:** #11 (Connection monitoring)
**Related Views:** `view-security-reliability.md`

---

## Context

Network connections fail due to:
- Air-Side restart (Docker, code update)
- Network issues (WiFi dropout, R16 interference)
- Ground-Side app backgrounding (Android kills connections)

**Requirements:**
- Auto-reconnect without user intervention
- Avoid flooding Air-Side with connection attempts
- Inform user of connection status

---

## Decision

**Exponential Backoff Auto-Reconnect Strategy**

**Algorithm:**
1. Detect failure (heartbeat timeout or TCP error)
2. Attempt reconnect immediately (0ms delay)
3. If fails, wait 1 second, retry
4. If fails again, wait 2 seconds, retry
5. Double delay each failure (1s → 2s → 4s → 8s → ...)
6. Cap max delay at 30 seconds
7. On success, reset delay to 1 second

**Why Exponential Backoff:**
- First retry fast (transient failures recover quickly)
- Later retries spaced out (avoid overwhelming Air-Side)
- Prevents reconnect storms

---

## Implementation

### Ground-Side (Kotlin)

```kotlin
class ConnectionManager {
    private var reconnectDelay = 1000L // Start at 1 second
    private val maxDelay = 30_000L // Cap at 30 seconds

    suspend fun reconnect() {
        while (!connected) {
            delay(reconnectDelay)

            try {
                connect()
                reconnectDelay = 1000L // Reset on success
                break
            } catch (e: Exception) {
                reconnectDelay = min(reconnectDelay * 2, maxDelay)
                Log.w("ConnectionManager", "Reconnect failed, retrying in ${reconnectDelay}ms")
            }
        }
    }
}
```

---

## Alternatives Considered

### Alternative 1: Fixed Interval Retry

**Approach:** Retry every 5 seconds

**Pros:** Simple, predictable

**Cons:**
- ❌ Too slow for transient failures (5 sec wait unnecessary)
- ❌ Too fast for sustained outages (floods Air-Side)

**Rejection:** Exponential backoff better balances responsiveness and resource usage

---

### Alternative 2: User-Initiated Reconnect Only

**Approach:** Show "Reconnect" button, user taps when ready

**Pros:** User in control

**Cons:**
- ❌ Poor UX (user must notice and tap button)
- ❌ Doesn't work if user away from device

**Rejection:** Auto-reconnect expected behavior for network apps

---

### Alternative 3: Immediate Retry Loop

**Approach:** Retry continuously with no delay

**Pros:** Fastest reconnection

**Cons:**
- ❌ Floods Air-Side with connection attempts (100+ per second)
- ❌ Wastes CPU on failing connects
- ❌ May trigger rate limiting or firewall rules

**Rejection:** Irresponsible network behavior

---

## Consequences

### Positive

✅ **Fast Recovery:** Transient failures reconnect in 1 second
✅ **Resource Friendly:** Sustained outages back off to 30 sec (not flooding)
✅ **User-Friendly:** Happens automatically, no user action required
✅ **Self-Healing:** System recovers from temporary network issues

### Negative

⚠️ **Max 30 Second Wait:** If Air-Side down long-term, user waits 30 sec between retries
- Acceptable: Air-Side restarts take ~10 sec, so 30 sec retry catches it

⚠️ **No Manual Retry Button:** User can't force immediate retry
- Future Enhancement: Add "Reconnect Now" button (resets backoff)

---

## Connection Status UI

**User Feedback:**
- Connected: Green indicator, hide status
- Disconnected: Red indicator, "Connecting..."
- Reconnecting: Yellow indicator, "Reconnecting in Xs..."

---

## Related Decisions

- **ADR-003:** TCP/UDP Protocol Split (reconnect applies to TCP)
- **ADR-007:** Stateless Air-Side (restart causes reconnect)
- **ADR-009:** Heartbeat Timeout (triggers reconnect)

---

## References

- Security & Reliability View: `view-security-reliability.md` (Network Disconnect handling)
- LESSONS_LEARNED.md: Network & Communication section
