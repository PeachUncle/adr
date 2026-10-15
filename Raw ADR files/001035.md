# ADR-001: Hybrid Architecture - Backend Owns State, n8n Owns LLM

> **Date:** 2025-11-29
> **Status:** Accepted
> **Decision Makers:** Architecture Review (Phase 2 Design)

---

## Context

### The Problem

The current `DungeonMaster_Main.json` workflow contains **34 nodes** performing tasks across business logic, data fetching, LLM orchestration, and database writes. This creates several critical issues:

1. **Dual Write Paths:** Both backend and n8n write to MongoDB independently, causing state sync issues
2. **Business Logic in Workflow:** Decisions about scene creation and skill checks happen in n8n instead of backend
3. **Context Assembly Overhead:** 7 nodes + 3 sub-workflows just to fetch data the backend already has
4. **No Transaction Safety:** Scene/chapter creation can fail partway with no rollback
5. **Synchronous Blocking:** 60-second timeout with no async processing
6. **Maintainability:** Complex workflows are fragile and hard to modify

### Why Change Now

- State synchronization bugs are increasing as complexity grows
- No way to implement proper error recovery
- Testing requires full n8n stack
- Cannot scale horizontally (n8n is bottleneck)
- Frontend has no progress indication during long LLM calls

---

## Decision

Implement a **hybrid architecture** that clearly separates concerns:

### Backend Responsibilities (FastAPI)
- **Owns ALL MongoDB writes** - Single source of truth for state
- **Assembles complete context bundle** - Campaign, scene, characters, lore, skill checks
- **Handles business logic** - Skill check detection, scene/chapter creation, validation
- **Async processing** - Returns immediately, uses callback pattern
- **Real-time notifications** - Socket.IO events for turn completion

### n8n Responsibilities (Workflow Orchestration)
- **LLM orchestration ONLY** - Narrative generation, transition detection
- **Simplified workflows** - Target: 5-6 nodes (down from 34)
- **No database writes** - Returns results to backend via callback
- **No data fetching** - Receives pre-assembled context from backend

### Key Architectural Patterns

1. **Async Callback Pattern:**
   ```
   Frontend → Backend (returns immediately) → n8n (processes async) → Backend callback → Socket.IO → Frontend
   ```

2. **Context Bundle:** Backend sends complete context to n8n in single payload

3. **LLM-Driven Transitions:** LLM detects scene/chapter transitions during narrative generation

4. **Transaction Safety:** Backend wraps scene creation + turn update in transaction

---

## Consequences

### Positive

#### Reliability
- ✅ Single source of truth for state (backend owns MongoDB)
- ✅ Transactional scene/chapter creation (rollback on failure)
- ✅ Proper error recovery (backend controls retries)
- ✅ No race conditions from dual writes

#### Maintainability
- ✅ Simpler n8n workflows (5-6 nodes vs 34)
- ✅ Business logic in testable Python code
- ✅ Can change logic without redeploying workflows
- ✅ Clear separation of concerns

#### User Experience
- ✅ No blocking on slow LLM calls (up to several minutes)
- ✅ Real-time progress updates via Socket.IO
- ✅ Frontend remains responsive during processing
- ✅ Better error messages to users

#### Development Velocity
- ✅ Unit testable backend services
- ✅ Can test turn processing without n8n
- ✅ Easier debugging (centralized logging)
- ✅ Can cache context assembly

### Negative

#### Implementation Effort
- ❌ Need to write new backend services (ContextAssembly, SkillCheck, Transition)
- ❌ Need to rebuild DungeonMaster workflow from scratch
- ❌ Migration requires feature flag and gradual rollout
- ❌ Estimated effort: 10-15 development days

#### Latency
- ❌ Additional round-trip for callback (adds ~50-100ms)
- ❌ Slightly slower than synchronous (acceptable tradeoff)

#### Complexity Shift
- ❌ More backend code to maintain
- ❌ Need to monitor callback success rate
- ❌ Need recovery tools for failed callbacks

### Trade-offs Accepted

| Trade-off | Why Acceptable |
|-----------|----------------|
| More backend code | Better testability and maintainability outweighs complexity |
| Callback latency | 50-100ms negligible compared to 60s+ LLM processing time |
| Migration effort | One-time cost, long-term benefit |
| Need recovery tools | Already needed for current architecture |

---

## Assumptions Made

1. **Ollama LLM latency** is the dominant factor (2-5 minutes typical)
   - 50-100ms callback overhead is negligible

2. **Frontend has Socket.IO support** for real-time updates
   - Can fall back to polling if needed

3. **MongoDB supports transactions** for atomic writes
   - Already available in current setup

4. **n8n can retry callbacks** on failure
   - Standard HTTP request retry mechanisms

5. **Context bundle size manageable** (15-30 KB)
   - Limits: 5 previous turns, 10 characters, 3 lore chunks

6. **LLM can reliably detect transitions** via structured output
   - Can add validation layer in backend if needed

---

## Alternatives Considered

### Alternative 1: Keep Everything in n8n

**Approach:** Improve current workflow, add error handling, but keep n8n owning writes

**Rejected because:**
- Doesn't solve dual write path issue
- Still no transaction safety
- Business logic remains in workflows (hard to test)
- Doesn't address maintainability

### Alternative 2: Move Everything to Backend

**Approach:** Backend makes direct Ollama LLM calls, remove n8n entirely

**Rejected because:**
- n8n provides value for LLM orchestration (retry, timeout handling, workflow UI)
- Would lose ability to modify prompts without code changes
- n8n Sub-workflows are reusable across DungeonMaster and Prophet

### Alternative 3: Backend Pulls Context on Demand

**Approach:** n8n calls backend endpoint to fetch context when needed

**Rejected because:**
- Still requires n8n to know WHAT to fetch (business logic in workflow)
- Extra HTTP call adds latency
- Backend might as well send context upfront

### Alternative 4: Keep Synchronous, Optimize Workflow

**Approach:** Improve current workflow but keep 60s timeout pattern

**Rejected because:**
- Cannot support > 60s LLM calls reliably
- Frontend still blocked during processing
- Doesn't solve fundamental state sync issues

---

## Implementation Notes

### Migration Strategy

1. **Incremental Rollout:**
   - Build new system alongside old
   - Feature flag: `USE_ASYNC_TURN_PROCESSING` (default: False)
   - Test with 10% traffic, gradually increase to 100%
   - Keep old workflow for 1 week as fallback

2. **Rollback Plan:**
   - Disable feature flag → reverts to old workflow
   - No data migration needed (same MongoDB schema)
   - Can switch back within seconds

### Success Metrics

Track these metrics to validate decision:

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Turn submission latency | 60s (blocking) | < 100ms | Backend response time |
| LLM processing time | Unknown | 2-5 min (visible) | n8n to callback latency |
| Callback success rate | N/A | > 99% | Backend monitoring |
| State sync errors | ~5/week | 0 | Bug reports |
| Workflow complexity | 34 nodes | 5-6 nodes | n8n workflow editor |

### Monitoring Required

- **Backend:** Callback failure rate, payload sizes, context assembly time
- **n8n:** Workflow execution time, retry attempts, error rates
- **MongoDB:** Transaction rollbacks, orphaned documents
- **Socket.IO:** Disconnect rate, event delivery latency

---

## Related Decisions

- **ADR-002:** (Future) Scene/Chapter Transition Criteria - Define precise rules for transitions
- **ADR-003:** (Future) Skill Check Detection Strategy - LLM vs regex/keyword matching
- **ADR-004:** (Future) Context Caching Strategy - Redis cache for campaign/scene data

---

## References

- [REFACTORING_PLAN.md](../architecture/REFACTORING_PLAN.md) - Full technical design
- [FRICTION_POINTS.md](../architecture/FRICTION_POINTS.md) - Problems this ADR solves
- [DATA_FLOW.md](../architecture/DATA_FLOW.md) - Current vs target data flow
- [DungeonMaster_Main.json](../../n8n_workflows/DungeonMaster_Main.json) - Current workflow

---

## Approval

| Role | Name | Date | Status |
|------|------|------|--------|
| Architect | Claude Code (Phase 2 Design) | 2025-11-29 | Accepted |
| Review Needed | Project Owner | TBD | Pending |

---

## Changelog

- **2025-11-29:** Initial ADR created during Phase 2 Design
