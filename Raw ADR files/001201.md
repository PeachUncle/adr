# ADR-025: ActionList Code Review & Gap Analysis

## Status
**Accepted** | 2025-12-28

## Context

TaskMan-v2 backend-api Phase 3 Task T2 requires comprehensive code review and gap analysis before proceeding with ActionList implementation. Evidence suggests partial implementation exists across multiple layers, but completeness, quality, and architectural consistency remain unvalidated.

### Current Implementation State

**Known Existing Components**:
- **Schemas**: `action_list.py` (Pydantic models confirmed)
- **Service**: `action_list_service.py` (business logic layer confirmed)
- **Models**: SQLAlchemy implementation status unknown
- **Repository**: CRUD layer existence unconfirmed
- **Router**: API endpoint implementation unconfirmed
- **Tests**: Coverage metrics unavailable

**Risk Factors**:
- Proceeding without gap analysis risks duplicating existing code
- Partial implementations may contain technical debt or anti-patterns
- Test coverage gaps could propagate to new features
- Architectural inconsistencies may violate established patterns (Task/Sprint/Project)

**Comparison Baseline**:
- **Task Router**: 184 lines, 10 query parameters, comprehensive CRUD
- **Sprint Router**: 187 lines, metrics endpoints, date filtering
- **Project Router**: 171 lines, health assessment, aggregation queries

### Architecture Drivers

**Quality Requirements**:
1. **Code Completeness**: All six architectural layers present (Model → Schema → Repository → Service → Router → Tests)
2. **Pattern Compliance**: Consistency with established Task/Sprint/Project implementations
3. **Test Coverage**: ≥70% baseline per quality gates ([09-Development-Guidelines.md](../09-Development-Guidelines.md))
4. **Technical Debt**: Identification of TODOs, workarounds, incomplete features
5. **Risk Assessment**: Classification of gaps by severity and implementation priority

## Decision

**Adopt systematic code review process before ActionList implementation**:

### Phase 1: Automated Discovery (Tool-Assisted)

**Component Inventory**:
```bash
# Locate all ActionList-related files
grep -r "ActionList" TaskMan-v2/backend-api --include="*.py"
grep -r "action_list" TaskMan-v2/backend-api --include="*.py"

# Identify test coverage
pytest --cov=action_list --cov-report=term-missing
```

**Metrics Collection**:
- Lines of code per component
- Cyclomatic complexity
- Dependency graph analysis
- Import relationship mapping

### Phase 2: Manual Code Inspection

**Review Matrix by Layer**:

| Layer | Checklist | Pass Criteria |
|-------|-----------|---------------|
| **Model** | SQLAlchemy schema, relationships, indexes | Matches DB schema, follows naming conventions |
| **Schema** | Request/response DTOs, validation rules | Pydantic v2 patterns, comprehensive field validation |
| **Repository** | CRUD methods, query composition, transactions | Result monad pattern, proper error handling |
| **Service** | Business logic, orchestration, validation | Dependency injection, logging, stateless design |
| **Router** | Endpoint definitions, OpenAPI docs, error mapping | RESTful conventions, HTTP status codes, examples |
| **Tests** | Unit tests, integration tests, fixtures | ≥70% coverage, edge cases, mocking patterns |

**Pattern Compliance Check**:
- Compare ActionList router structure against `tasks.py` baseline
- Validate dependency injection matches established service patterns
- Confirm error handling uses Result monad consistently
- Verify logging follows unified logger conventions

### Phase 3: Gap Documentation

**Gap Categories**:

1. **Missing Components** (Severity: Critical)
   - Components that were planned but never implemented
   - Example: Repository layer if completely absent

2. **Incomplete Implementations** (Severity: High)
   - Stubbed methods with `pass` or `raise NotImplementedError`
   - Missing error handling branches
   - Insufficient validation logic

3. **Technical Debt** (Severity: Medium)
   - TODO comments indicating deferred work
   - Workarounds or temporary solutions
   - Code duplication opportunities for refactoring

4. **Test Coverage Gaps** (Severity: High)
   - Untested code paths below 70% threshold
   - Missing edge case coverage
   - Inadequate integration test scenarios

5. **Documentation Deficiencies** (Severity: Low)
   - Missing docstrings
   - Incomplete OpenAPI examples
   - Outdated inline comments

**Gap Report Format**:
```yaml
component: action_list_service.py
gaps:
  - category: incomplete_implementation
    severity: high
    location: update_action_list() method
    description: "Task relationship updates not implemented"
    impact: "Cannot add/remove tasks from lists via API"
    estimated_effort: "4 hours"

  - category: technical_debt
    severity: medium
    location: line 87
    description: "TODO: Implement caching strategy"
    impact: "Performance degradation on repeated queries"
    estimated_effort: "2 hours"
```

### Phase 4: Implementation Plan Adjustment

**Outcomes**:

1. **Comprehensive Gap Report**
   - All identified gaps with severity classification
   - Estimated effort for remediation
   - Dependency relationships between gaps

2. **Priority Classification**
   - **Must-Fix**: Blocks core functionality (e.g., missing repository)
   - **Should-Fix**: Impacts quality/performance (e.g., test coverage gaps)
   - **Nice-to-Have**: Improves maintainability (e.g., documentation)

3. **Risk Assessment Update**
   - Quantified risk from proceeding with known gaps
   - Mitigation strategies for acceptable technical debt
   - Regression risk from modifying existing code

4. **Adjusted WBS**
   - Task effort estimates recalibrated based on findings
   - New subtasks added for gap remediation
   - Dependencies reordered to address critical gaps first

## Consequences

### Positive

- **Prevents Code Duplication**: Reuses existing implementations where quality is acceptable
- **Identifies Hidden Technical Debt**: Surfaces TODOs and workarounds before they multiply
- **Establishes Quality Baseline**: Quantifies current state before introducing changes
- **Reduces Regression Risk**: Validates existing code patterns before modification
- **Improves Estimation Accuracy**: Adjusts effort based on actual vs assumed completion

### Negative

- **Upfront Time Investment**: Requires 4-6 hours before implementation begins
- **Potential Discouragement**: May reveal significant gaps requiring rework
- **Analysis Paralysis Risk**: Could delay implementation if perfectionism emerges

### Neutral

- **Documentation Artifact**: Creates audit trail for future maintainers
- **Learning Opportunity**: Team gains deeper understanding of existing codebase
- **Baseline for Metrics**: Establishes pre/post comparison for improvement tracking

## Alternatives Considered

### Alternative 1: Skip Review, Implement Fresh
**Rationale**: Assume existing code is incomplete, rebuild from scratch
**Rejected Because**:
- High risk of duplicating working code
- Wastes existing investment in partial implementations
- May introduce regressions in functional components

### Alternative 2: Spot-Check Critical Paths Only
**Rationale**: Review only high-risk areas (e.g., repository, service)
**Rejected Because**:
- Surface-level analysis misses interconnected gaps
- Test coverage gaps remain hidden
- Pattern inconsistencies propagate undetected

### Alternative 3: Progressive Discovery During Implementation
**Rationale**: Address gaps as encountered during development
**Rejected Because**:
- Reactive approach causes rework and context switching
- Effort estimation becomes unreliable
- Architectural decisions made without full context

## Implementation Notes

### Critical Review Questions

1. **Existence Validation**
   - Which of the six layers (Model, Schema, Repository, Service, Router, Tests) are present?
   - Are file structures consistent with naming conventions?

2. **Quality Assessment**
   - What percentage of methods have complete implementations vs stubs?
   - Does error handling follow Result monad pattern consistently?
   - Are dependencies injected properly via FastAPI dependency system?

3. **Pattern Consistency**
   - How does ActionList router compare to Task/Sprint/Project patterns?
   - Are repository queries using SQLAlchemy best practices?
   - Does service layer avoid database coupling?

4. **Reusability Analysis**
   - Which components meet quality standards and can be reused as-is?
   - Which require refactoring before integration?
   - Which must be rebuilt completely?

### Success Criteria

- [ ] All six architectural layers inventoried with status (complete/incomplete/missing)
- [ ] Test coverage metrics obtained (line coverage, branch coverage)
- [ ] Gap report generated with ≥80% of actual gaps identified
- [ ] Priority classification assigned to all gaps
- [ ] WBS effort estimates adjusted within ±20% accuracy
- [ ] Risk register updated with quantified gap-related risks

### Tooling

- **Static Analysis**: `pylint`, `mypy` for type checking
- **Coverage**: `pytest --cov` with branch coverage enabled
- **Code Metrics**: `radon` for cyclomatic complexity
- **Search**: `grep`/`ripgrep` for pattern detection
- **Diff Analysis**: Compare against `tasks.py`, `sprints.py`, `projects.py` baselines

## References

- [ADR-017: ActionList Repository Implementation Strategy](./ADR-017-ActionList-Repository-Implementation-Strategy.md)
- [ADR-018: ActionList Service Layer Architecture](./ADR-018-ActionList-Service-Layer-Architecture.md)
- [ADR-019: ActionList API Router Architecture](./ADR-019-ActionList-API-Router-Architecture.md)
- [09-Development-Guidelines.md](../09-Development-Guidelines.md) — Quality gates and standards
- [13-Testing-Validation.md](../13-Testing-Validation.md) — Coverage requirements

---

**Decision Authority**: ContextForge Work Architect
**Stakeholders**: Backend development team, QA lead
**Review Date**: 2026-01-28 (30-day reassessment)
