# ADR-005: Session Memory Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-19
- **Feature:** Phase 3 - Todo AI Chatbot
- **Context:** The AI chatbot needs conversational context to understand follow-up messages like "delete that task" or "yes, do it". We must decide how to store session state: in-memory vs. persistent, TTL policy, context resolution strategy, and what data to retain.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ Yes - defines stateful behavior
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ Yes - in-memory, Redis, DB, stateless
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ Yes - affects all conversational flows
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We adopt an **in-memory session storage** strategy for Phase 3 with clear upgrade path:

| Component | Technology | Configuration |
|-----------|------------|---------------|
| **Storage** | In-memory HashMap | Python `dict[UUID, ChatSession]` |
| **TTL** | 30 minutes | Inactivity-based expiration |
| **Max Messages** | 20 per session | Rolling window of recent messages |
| **Context Types** | Messages, intents, task refs, confirmations | Structured context object |
| **Cleanup** | Lazy eviction | On access or periodic sweep |

### Session Data Structure

```python
class ChatSession:
    session_id: UUID
    user_id: UUID
    created_at: datetime
    last_activity: datetime
    context: SessionContext

class SessionContext:
    messages: list[ChatMessage]      # Last 20 messages (rolling)
    last_intent: str | None          # Most recent classified intent
    last_task_ids: list[UUID]        # Recently referenced task IDs
    pending_confirmation: Confirmation | None  # For destructive actions
```

### Context Resolution Rules

| User Says | Resolution Strategy | Example |
|-----------|---------------------|---------|
| "that task" | `last_task_ids[0]` | "Delete that task" → delete task from last response |
| "the one I mentioned" | Search message history | Fuzzy match in recent messages |
| "yes" / "do it" | Execute `pending_confirmation` | Confirm deletion |
| "cancel" / "no" | Clear `pending_confirmation` | Abort pending action |

### Session Lifecycle

```
User Message (no session_id)
    │
    ▼
Create new session (UUID generated)
    │
    ▼
Process message, update context
    │
    ▼
Return session_id to client
    │
    ▼
Subsequent messages include session_id
    │
    ▼
30 min inactivity → Session expired (lazy eviction)
```

## Consequences

### Positive

- **Zero infrastructure**: No Redis/DB dependency for Phase 3 MVP
- **Low latency**: In-memory access is sub-millisecond
- **Simple implementation**: Python dict with dataclasses
- **Conversational context**: Enables "that task", "yes", "no" interactions
- **Confirmation flow**: Pending confirmations prevent accidental deletions
- **Clear upgrade path**: Can migrate to Redis/DB in Phase 4 without API changes

### Negative

- **No persistence**: Sessions lost on server restart
- **No horizontal scaling**: Sessions bound to single server instance
- **Memory pressure**: 1000 active sessions × 20 messages = significant RAM
- **No cross-device continuity**: User can't continue conversation on another device
- **Race conditions**: Concurrent requests to same session need locking

### Mitigations

| Risk | Mitigation |
|------|------------|
| Memory pressure | 30-min TTL + 20-message limit + lazy eviction |
| Server restart | Acceptable for MVP; sessions are ephemeral by design |
| Scaling | Phase 4 will add Redis; API contract unchanged |
| Race conditions | Session operations are atomic (single-threaded Python GIL) |

## Alternatives Considered

### Alternative A: Stateless (No Session Memory)

- **Approach**: Each message is independent; no context retention
- **Pros**: Simplest, scales infinitely, no state management
- **Cons**: No "that task" resolution, no confirmation flow, poor UX
- **Why rejected**: Conversational context is essential for natural interaction

### Alternative B: Redis Session Store

- **Approach**: Store sessions in Redis with automatic TTL
- **Pros**: Persistent, scalable, built-in expiration, cluster support
- **Cons**: Additional infrastructure, network latency, operational overhead
- **Why rejected**: Overkill for Phase 3 MVP; planned for Phase 4

### Alternative C: Database-Backed Sessions

- **Approach**: Store sessions in PostgreSQL (Neon)
- **Pros**: Persistent, queryable, auditable, existing infrastructure
- **Cons**: Higher latency, schema management, not optimized for ephemeral data
- **Why rejected**: Database not designed for high-churn session data

### Alternative D: Client-Side Session (JWT Claims)

- **Approach**: Encode session context in JWT or client state
- **Pros**: Stateless server, scales infinitely
- **Cons**: Token size explosion, can't track pending confirmations securely
- **Why rejected**: Context too large for tokens; confirmation state must be server-side

## Phase 4 Upgrade Path

When scaling requires persistent sessions:

1. **Add Redis dependency**: `redis-py` with async support
2. **Implement `SessionStore` interface**: Abstract storage operations
3. **Swap implementation**: `InMemorySessionStore` → `RedisSessionStore`
4. **No API changes**: Session ID and context resolution unchanged

```python
# Phase 3 (current)
class InMemorySessionStore(SessionStore):
    sessions: dict[UUID, ChatSession] = {}

# Phase 4 (future)
class RedisSessionStore(SessionStore):
    redis: Redis
    ttl: int = 1800  # 30 minutes
```

## References

- Feature Spec: `specs/phase3-ai-chatbot/spec.md` (Section 4: Session Memory)
- Skill Definition: `.claude/skills/chat-session-memory/SKILL.md`
- Related ADRs: ADR-002 (ConversationAgent owns ChatSessionMemory skill)
- Constitution: `.specify/memory/constitution.md` (Phase 4 mentions DB-backed history)
