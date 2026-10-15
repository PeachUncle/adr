# ADR-001: Serial E2E Test Execution Strategy

## Status
Accepted

## Date
2025-08-28

## Context
Our E2E test suite was experiencing severe reliability issues with parallel execution:
- Database cleanup failures causing test contamination
- SQLite file locks with multiple workers
- Server resource exhaustion (27+ instances spawning)
- Non-deterministic test failures
- Complex worker isolation attempts failing

After extensive analysis, we discovered that our monolithic architecture using SQLite and Entity Framework Core is fundamentally incompatible with parallel E2E test execution without massive architectural changes.

## Decision
We will adopt a **serial E2E test execution strategy** with aggressive performance optimizations.

### Key Decisions:
1. **Single worker execution** - All E2E tests run sequentially
2. **Shared server infrastructure** - Start servers once, use for all tests
3. **File-based database cleanup** - Delete and recreate SQLite file
4. **Test categorization** - Run only necessary tests based on context
5. **Single browser default** - Cross-browser testing only for critical paths

## Consequences

### Positive
- **100% test reliability** - No race conditions or shared state issues
- **Simple architecture** - No complex worker isolation logic
- **Predictable behavior** - Same results locally and in CI
- **Easy debugging** - Can reproduce any failure reliably
- **Lower resource usage** - Only 2 servers instead of 27+
- **Maintainable** - New developers understand immediately

### Negative
- **Longer test execution** - 10 minutes vs theoretical 3 minutes parallel
- **Sequential development** - Can't run multiple test files simultaneously
- **CI pipeline changes** - Need staged execution for fast feedback
- **Developer discipline** - Must write fast tests to keep suite manageable

## Alternatives Considered

### 1. In-Memory SQLite Database
**Rejected because:**
- EF Core connection lifetime management issues
- Cannot debug when tests fail
- Migrations don't work properly
- Background services break

### 2. Schema-Based Isolation (Table Prefixes)
**Rejected because:**
- EF Core DbContext cannot change table names per request
- Foreign key relationships break across schemas
- HTTP headers don't propagate through all layers
- Background services have no request context

### 3. Complete Server Isolation (1 Stack Per Worker)
**Rejected because:**
- Resource exhaustion with multiple workers
- Port management complexity
- Slow startup times
- CI cost explosion

### 4. PostgreSQL Migration
**Rejected because:**
- Major architectural change
- Requires rewriting data layer
- Additional infrastructure complexity
- Not solving the fundamental monolith issue

## Implementation Plan

### Phase 1: Immediate (Day 1-2)
- Fix database cleanup with file deletion
- Switch to single worker configuration
- Single browser for local development

### Phase 2: Optimization (Day 3-4)
- Global server management (start once)
- Lean server configurations
- Remove unnecessary middleware

### Phase 3: Categorization (Day 5-6)
- Tag tests: @smoke, @critical, @extended
- Create multiple test configurations
- Update CI pipeline for staged execution

### Phase 4: Performance (Week 2)
- Optimize individual test speed
- Batch API operations
- Smart waits instead of fixed delays

## Metrics for Success
- Smoke tests: < 2 minutes
- Full suite: < 10 minutes
- Test reliability: 100% (no flaky tests)
- CI failures: < 5% (from current 30%)

## Review Date
2025-09-28 (1 month after implementation)

## References
- [Serial Testing Guide](../Quality-Assurance/SERIAL-TESTING-GUIDE.md)
- [Implementation Plan](../Quality-Assurance/SERIAL-TEST-OPTIMIZATION-PLAN.md)
- [Testing Strategy](../Quality-Assurance/Testing-Strategy.md)