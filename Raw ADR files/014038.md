# ADR-051: Unified User Session Context

**Status**: APPROVED
**Date**: 2026-01-13
**Authors**: Lead Developer (Claude Code)
**Approved By**: Chief Architect (2026-01-13)
**Issue**: #584
**Deciders**: Chief Architect

## Context

### Problem Statement

The codebase has accumulated significant technical debt around identity and context management. Investigation (Issue #584) revealed:

1. **14 different ID concepts** scattered across the codebase
2. **Type inconsistencies** for `user_id` (UUID in DB, str in routes, mixed in services)
3. **Semantic overloading** of `session_id` for three different purposes
4. **Broken propagation** where `user_id` doesn't flow through call chains

This has caused multiple bugs (#490, #582) and will continue to cause bugs as features are added.

### Root Cause Analysis

The issues stem from three interrelated problems:

**1. Model Problem (Foundational)**
Three distinct domain concepts are conflated:
- **User Identity**: Who is making the request (permanent)
- **Session Context**: Ephemeral request context (per-request)
- **Conversation Context**: Multi-turn state (per-conversation)

**2. Naming Problem (Semantic)**
`session_id` is used for:
- Request-level ephemeral context in routes
- Persistent conversation identity in ConversationManager
- User-context cache key in UserContextService

**3. Implementation Problem (Type System)**
`user_id` has 5+ different type representations:
- `UUID` in database models
- `UUID` in `JWTClaims.user_id` field
- `str` in `JWTClaims.sub` field (canonical JWT claim)
- `str` when extracted in routes (`current_user.sub`)
- Mixed `str`/`UUID` in service layer parameters

### Historical Context

This pattern emerged from:
1. Initial single-user architecture where `session_id` == user context
2. Multi-user retrofit (Issue #280) that added fallbacks rather than proper propagation
3. Feature accretion (onboarding, portfolio, standup) each handling IDs inconsistently
4. No unified identity layer as a single source of truth

### Current State Evidence

| File | Issue | Severity |
|------|-------|----------|
| `web/api/routes/intent.py:221` | Uses `.sub` instead of `.user_id` | HIGH |
| `services/user_context_service.py:49` | Falls back to session_id as user ID | CRITICAL |
| `services/intent/intent_service.py:140` | Uses session_id as conversation_id | MEDIUM |
| `services/intent_service/canonical_handlers.py:126` | `user_id: str = None` (wrong type) | HIGH |
| `services/intent_service/todo_handlers.py:37` | `user_id: UUID` (conflicting type) | HIGH |

## Decision

### Approved Solution: Unified `RequestContext` Model

Create a single, immutable context object that flows through the entire request lifecycle.

**Chief Architect Decision**: Single `RequestContext` approved. The three concepts have different lifecycles but same scope of need - always needed together for request processing.

```python
# services/domain/models.py

@dataclass(frozen=True)
class RequestContext:
    """
    Unified context for all request processing.

    This is the single source of truth for identity and context.
    Passed through all service calls - never optional, never reconstructed.
    """
    # Core identity (required)
    user_id: UUID                    # Authenticated user's database PK
    conversation_id: UUID            # Database PK for conversation record
    request_id: UUID                 # Unique per-request for tracing

    # Denormalized for convenience
    username: str                    # Display name (saves lookup cost on logs)
    timestamp: datetime              # Request timestamp

    # Future-proofing
    workspace_id: Optional[UUID] = None  # For future multi-tenant support

    @classmethod
    def from_jwt_and_request(
        cls,
        claims: JWTClaims,
        conversation_id: str,
        request_id: Optional[UUID] = None,
    ) -> "RequestContext":
        """Factory method to create context from JWT claims and request data."""
        # Validation - fail fast on malformed input
        if not claims.sub:
            raise ValueError("JWT claims missing 'sub' field")
        if not conversation_id:
            raise ValueError("conversation_id is required")

        return cls(
            user_id=UUID(claims.sub),  # str → UUID at boundary
            conversation_id=UUID(conversation_id),  # str → UUID at boundary
            request_id=request_id or uuid4(),
            username=claims.username,
            timestamp=datetime.utcnow(),
            workspace_id=UUID(claims.workspace_id) if claims.workspace_id else None,
        )

    def __str__(self) -> str:
        """String representation for logging/debugging."""
        return f"RequestContext(user={self.user_id}, conv={self.conversation_id}, req={self.request_id})"
```

### Type Strategy (APPROVED)

**Decision**: UUID internally, str at boundaries

| Layer | Type | Rationale |
|-------|------|-----------|
| Routes | Accept `str`, convert via factory | Boundary conversion |
| Services | Always `UUID` | Type safety |
| Repositories | Always `UUID` | Type safety |
| Responses | Convert to `str` at serialization | API contract |

### Session_id Resolution (APPROVED)

| Current Usage | Becomes |
|---------------|---------|
| Ephemeral request context | `request_id` |
| Conversation identity | `conversation_id` |
| User-context cache key | `user_id` (cache was using wrong key) |

### Scope (APPROVED)

**Core four IDs in RequestContext**:
- `user_id` - Who is making the request
- `conversation_id` - Which conversation this is
- `request_id` - This specific request (for tracing)
- `workspace_id` - Which workspace (optional, future multi-tenant)

**Domain entities (NOT in RequestContext)**:
`project_id`, `intent_id`, `workflow_id`, `task_id`, etc. - these are processed BY requests, not context FOR requests.

### Propagation Pattern

```python
# In routes - create context once at boundary
@router.post("/intent")
async def process_intent(
    request: IntentRequest,
    current_user: JWTClaims = Depends(get_current_user),
):
    # Create context at request boundary - single source of truth
    context = RequestContext.from_jwt_and_request(
        claims=current_user,
        conversation_id=request.conversation_id,
    )

    # Pass context through all calls
    result = await intent_service.process(context, request.message)
    return result

# In services - always receive context, never reconstruct
class IntentService:
    async def process(self, ctx: RequestContext, message: str) -> IntentResult:
        # Use ctx.user_id for user-scoped operations
        user_context = await self.context_service.get(ctx.user_id)

        # Use ctx.conversation_id for conversation operations
        history = await self.conversation_repo.get_turns(ctx.conversation_id)

        # Pass context to downstream services
        return await self._route_intent(ctx, classified_intent)
```

### Migration Strategy (APPROVED - Compressed Timeline)

**Chief Architect Guidance**: Incremental but compressed to 2-3 focused days. Do NOT let Phase 2 become permanent.

| Phase | Scope | Target |
|-------|-------|--------|
| 1 | Add `RequestContext` model, factory, documentation | Day 1 AM |
| 2 | Update routes to create context, pass alongside old params | Day 1 PM |
| 3 | Update services to use context, update tests | Day 2 |
| 4 | Remove old patterns, enforce consistency | Day 2-3 |

**CRITICAL WARNING**: Do NOT leave Phase 2 (dual patterns) as permanent state. This is exactly how the current mess happened.

## Alternatives Considered

### Alternative A: Request-Scoped Dependency Injection
Use FastAPI's dependency injection to provide context automatically.

**Pros**: Less explicit passing, cleaner signatures
**Cons**: Hidden dependencies, harder to test, magic behavior

**Decision**: Rejected - explicit is better than implicit for critical context

### Alternative B: Thread-Local / Context Variables
Use Python's `contextvars` for implicit context propagation.

**Pros**: No parameter passing needed
**Cons**: Hidden state, harder to reason about, async complexity

**Decision**: Rejected - explicit passing is more maintainable

### Alternative C: Keep Current Pattern, Just Document
Document the existing inconsistencies and establish conventions.

**Pros**: No code changes, immediate
**Cons**: Doesn't fix the bugs, conventions will drift

**Decision**: Rejected - documentation alone hasn't prevented bugs

### Hybrid Option (Optional Enhancement)
Create context in middleware, attach to `request.state`, but still pass as explicit parameter:

```python
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request.state.context = RequestContext.from_jwt_and_request(...)
    return await call_next(request)
```

**Decision**: Not required for current scale, but valid for future consideration.

## Consequences

### Positive
- Single source of truth for identity/context
- Type-safe ID handling
- Eliminates class of bugs around `user_id` propagation
- Clear audit trail (request_id tracing)
- Foundation for multi-tenant support

### Negative
- Significant refactoring effort (mitigated by compressed timeline)
- All services need signature updates
- Tests need updates
- Learning curve for new pattern

### Risks
- Incomplete migration leaves two patterns (mitigated by compressed timeline)
- Breaking changes during migration (mitigated by phased approach)

## Chief Architect Review

**Questions Asked**:
1. Single `RequestContext` vs split abstractions? → **Single approved**
2. Type standardization? → **UUID internal, str at boundary approved**
3. Migration approach? → **Incremental, compressed to 2-3 days**
4. Scope? → **Core four IDs only**
5. Alternative patterns? → **Explicit passing approved**

**Additional Recommendations Incorporated**:
- Validation in factory (fail fast)
- `__str__` for logging
- Optional enforcement decorator for critical paths

## References

- Issue #584 - Original tech debt identification
- Issue #582 - Bug caused by missing `user_id` propagation
- Issue #490 - Portfolio onboarding bug (related to session/user confusion)
- ADR-049 - Conversational State (related context management)
- Chief Architect Memo - `dev/active/memo-lead-dev-identity-model-response.md`

---

_ADR created: 2026-01-13_
_Status: APPROVED by Chief Architect (2026-01-13)_
_Implementation: Scheduled as focused 2-3 day sprint_
