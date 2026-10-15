# ADR-001: Migrate to Full Facade Architecture

**Date:** 2025-10-31
**Status:** PROPOSED
**Deciders:** Felix, Ada, User
**Consulted:** Luca (consciousness phenomenology), Atlas (infrastructure)

---

## Context

PR #2 introduced a facade wrapper (`consciousness/engine/`) around the legacy consciousness engine (`consciousness_engine_v2.py`). The facade provides:
- Clean hexagonal architecture (ports & adapters)
- Immutable state (EngineState)
- Pure functions (testable, composable)
- I/O abstraction (GraphPort, TelemetryPort)

**Current Architecture:**
```
Facade (300 lines, clean) wraps → Legacy Engine (3000 lines, does all the work)
```

**The Question:** Should we:
1. Keep facade as permanent wrapper (maintain legacy engine)
2. Migrate all logic into facade, delete legacy engine

---

## Decision

**We will migrate all consciousness logic into the facade architecture and delete the legacy engine.**

---

## Rationale

### Why Migrate (Pros)

**1. Maintainability**
- Clean separation of concerns (domain/services/ports)
- Pure functions easier to understand and modify
- No I/O mixed with business logic
- Immutable state prevents subtle bugs

**2. Testability**
- Pure domain logic: Easy to test without mocks
- Ports: Easy to mock for integration tests
- Can test consciousness algorithms in isolation
- Current legacy engine: Hard to test (tightly coupled)

**3. Extensibility**
- Ports pattern makes adding new I/O easy
- Can swap implementations (e.g., different graph backends)
- Can add new features without touching core logic
- Current legacy engine: Tightly coupled to FalkorDB, WebSocket, etc.

**4. Code Quality**
- Remove 3000 lines of legacy code
- Eliminate tech debt (hardcoded values, old patterns)
- Apply modern patterns (hexagonal, DDD)
- Enforce fail-loud contract (R-400/401)

**5. Team Velocity**
- New team members: Easier to understand clean architecture
- Luca (consciousness architect): Can review pure domain logic
- Felix (consciousness engineer): Can focus on algorithms, not I/O plumbing
- Atlas (infrastructure): Clear port boundaries

### Why NOT Keep Legacy (Cons of Wrapper)

**1. Maintenance Burden**
- Maintaining two codebases (facade + legacy)
- Facade features need to be kept in sync with legacy
- Bug fixes need to be applied in two places
- Tech debt in legacy never gets addressed

**2. Confusion**
- Which code is "real"? (Answer: legacy engine)
- Why have a clean facade if logic is still messy?
- New team members don't know which to read

**3. Performance**
- Facade wrapper adds overhead (function calls, state copying)
- Not getting benefits of clean architecture (still using legacy patterns)

---

## Alternatives Considered

### Alternative 1: Keep Facade as Permanent Wrapper
**Approach:** Facade provides clean API, legacy engine does the work

**Pros:**
- Low risk (no behavior changes)
- Fast (no migration work)
- Can iterate on facade API without touching legacy

**Cons:**
- Maintains tech debt in legacy engine
- Facade overhead without benefits
- Two codebases to maintain

**Verdict:** REJECTED - Doesn't solve maintainability problems

---

### Alternative 2: Incremental Refactor (No Facade)
**Approach:** Gradually refactor legacy engine in-place

**Pros:**
- No architectural shift
- Can do small changes incrementally

**Cons:**
- Hard to maintain clean boundaries
- Temptation to take shortcuts
- No forcing function for good architecture
- Likely to end up with hybrid mess

**Verdict:** REJECTED - Experience shows in-place refactors rarely finish

---

### Alternative 3: Full Rewrite from Scratch
**Approach:** Write new engine from first principles

**Pros:**
- Cleanest possible result
- No legacy constraints

**Cons:**
- VERY high risk (might not replicate behavior)
- Much longer timeline (6+ months)
- No rollback path

**Verdict:** REJECTED - Too risky, facade migration is safer

---

## Risks and Mitigations

### Risk 1: Breaking Consciousness Behavior ⚠️ HIGH
**Description:** New pure functions might not perfectly replicate legacy behavior

**Mitigations:**
- Test-driven migration (write tests first)
- Side-by-side comparison (run old + new in parallel)
- Telemetry monitoring (compare metrics)
- Gradual rollout (one citizen first, then all)
- Rollback plan (keep legacy in git)

**Acceptance:** 24 hours of production monitoring with <5% metric deviation

---

### Risk 2: Performance Degradation ⚠️ MEDIUM
**Description:** New architecture might be slower (immutable state, more function calls)

**Mitigations:**
- Profiling before/after
- Optimization phase (Phase 10)
- Performance tests (<10% regression acceptable)

**Acceptance:** Frame loop time <10% slower than legacy

---

### Risk 3: Timeline Overruns ⚠️ MEDIUM
**Description:** 37 hours estimate might be wrong (could take longer)

**Mitigations:**
- Phased approach (can pause after any phase)
- Each phase <5 hours (manageable chunks)
- Can adjust timeline as we learn

**Acceptance:** Complete within 6 weeks (even if estimate off)

---

### Risk 4: Integration Failures ⚠️ LOW
**Description:** New facade might not integrate with existing systems

**Mitigations:**
- Keep legacy engine functional until full verification
- Integration tests at each phase
- Can revert to legacy if needed

**Acceptance:** All existing integrations work (dashboard, telemetry, APIs)

---

## Success Metrics

**Code Quality:**
- ✅ Delete 3000+ lines of legacy code
- ✅ All domain logic is pure functions
- ✅ 0 R-400/401 violations in new code
- ✅ Test coverage >80% for domain layer

**Behavior Preservation:**
- ✅ All existing tests pass
- ✅ Telemetry metrics within 5% of baseline
- ✅ Consciousness behavior visually identical (dashboard)
- ✅ SubEntity coordination working

**Performance:**
- ✅ Frame loop time <10% slower than legacy
- ✅ Memory usage <10% higher than legacy
- ✅ No memory leaks (24h stability test)

**Team Velocity:**
- ✅ New features easier to add (measured by LOC per feature)
- ✅ Bugs easier to fix (measured by time to resolve)
- ✅ Code review faster (measured by review time)

---

## Timeline

**Recommended:** Option B (4 weeks, measured pace)

- **Week 1:** Phases 1-2 (Energy + Activation)
- **Week 2:** Phases 3-4 (Frame Loop + Criticality)
- **Week 3:** Phases 5-7 (Diffusion + SubEntity + WM)
- **Week 4:** Phases 8-10 (Ports + Cutover + Polish)

**Cutover Point:** End of Week 4
**Verification Period:** Week 5 (production monitoring)
**Rollback Window:** 7 days after cutover

---

## Consequences

### Positive

**Short-term:**
- Clean, testable consciousness codebase
- Delete 3000 lines of legacy code
- Easier to onboard new team members

**Long-term:**
- Foundation for advanced consciousness features
- Can experiment with algorithms without breaking I/O
- Can swap graph backends, telemetry systems, etc.
- Team velocity increases (easier to add features)

### Negative

**Short-term:**
- 37 hours of engineering effort
- Risk of breaking consciousness behavior
- Requires extensive testing/verification

**Long-term:**
- Team needs to learn hexagonal architecture (if not familiar)
- More files to navigate (but better organized)

### Neutral

**Architecture becomes opinionated:**
- Forces hexagonal/ports & adapters pattern
- Forces pure functions in domain layer
- Forces immutable state
- This is GOOD for quality, but constrains implementation choices

---

## Implementation Notes

**See:** `docs/MIGRATION_PLAN_FACADE_FULL.md` for detailed 10-phase migration plan

**Key Principles:**
1. Test-driven migration (write tests first)
2. One subsystem at a time (energy → activation → frame loop → ...)
3. Keep legacy functional (can rollback)
4. Verify at each phase (tests + telemetry)
5. Gradual cutover (one citizen first)

---

## Review Notes

**Felix (2025-10-31):**
- Strongly support migration
- Legacy engine is hard to maintain
- Facade pattern is proven (PR #2 tests passing)
- 37 hours is reasonable for this scope

**Ada:**
- [To be filled]

**Luca:**
- [To be filled - phenomenological review]

**Atlas:**
- [To be filled - infrastructure concerns]

**User:**
- [To be filled - decision approval]

---

## Decision Status

**Status:** PROPOSED (awaiting approval)

**Approvers:**
- [ ] User (final decision)
- [ ] Ada (architecture review)
- [ ] Luca (consciousness phenomenology review)
- [ ] Felix (implementation commitment)
- [ ] Atlas (infrastructure impact review)

**If Approved:**
- Create TICKET-008: Facade Full Migration
- Start Phase 1 (Energy Dynamics)
- Target completion: 4 weeks from approval

**If Rejected:**
- Keep facade as wrapper
- Do TICKET-006 (clean legacy engine)
- Document decision in this ADR

---

**Generated:** 2025-10-31
**Author:** Felix "Core Consciousness Engineer"
**Next Action:** Await approval to proceed
