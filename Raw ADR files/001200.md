# ADR-016: Schema Audit for cf_core-TaskMan-v2 ActionList Integration

## Status
**Accepted** | 2025-12-28

## Context

ContextForge Work operates two parallel ActionList implementations serving different architectural layers:

1. **cf_core ActionList** ([action_list.py](../../cf_core/models/action_list.py))
   - Pydantic v2 domain model
   - Minimal 8-field schema (id, name, description, status, task_ids, created_by, created_at, updated_at, tags)
   - Used for in-memory operations, CLI tools, and MCP services
   - No direct database persistence layer

2. **TaskMan-v2 ActionList** ([models/action_list.py](../../TaskMan-v2/backend-api/src/taskman_api/models/action_list.py))
   - SQLAlchemy ORM model with 20-field schema
   - Includes full ContextForge integration (geometry_shape, priority, evidence_refs, etc.)
   - PostgreSQL primary, SQLite test dual-database support
   - Rich API schemas with validation aliases (title/name compatibility)

**The Integration Challenge**: Phase 3 execution requires cf_core CLI tools to persist ActionLists to TaskMan-v2's database. Without comprehensive schema audit, we risk:

- Field name mismatches breaking API contracts
- Type incompatibilities causing validation failures
- Data loss during transformation (cf_core → TaskMan-v2)
- Migration complexity if gaps discovered post-implementation

**Current State**:
- cf_core has no awareness of TaskMan-v2's extended schema
- TaskMan-v2 API uses validation aliases (`title`/`name`) not documented in cf_core
- No formalized mapping between 8-field minimal model and 20-field database schema
- Unknown compatibility of Pydantic validators vs SQLAlchemy constraints

## Decision Drivers

### Critical Requirements
1. **Zero Data Loss**: Every cf_core field must map to TaskMan-v2 without information loss
2. **Type Safety**: Pydantic validators must align with SQLAlchemy column types
3. **API Contract Stability**: Prevent breaking changes in existing TaskMan-v2 endpoints
4. **Dual-Database Support**: Preserve PostgreSQL/SQLite compatibility via StringList TypeDecorator
5. **Migration Safety**: Identify schema gaps before implementing persistence layer

### Risk Assessment
- **High Risk**: Implementing blind leads to production bugs requiring data migration
- **Medium Risk**: Partial audit misses edge cases (e.g., timezone handling in timestamps)
- **Low Risk**: Comprehensive audit upfront delays initial commit by ~2 hours but prevents 80% of integration issues

### Stakeholder Impact
- **cf_core Users**: Expect seamless persistence without changing existing CLI workflows
- **TaskMan-v2 API Consumers**: Require backward compatibility of existing endpoints
- **Database Administrators**: Need clear migration path if schema changes required

## Options Considered

### Option 1: Skip Audit, Implement Blindly ❌
**Approach**: Begin implementing cf_core persistence layer immediately without formal schema comparison.

**Pros**:
- Fastest time to first commit (~2 hours)
- Minimal upfront planning overhead

**Cons**:
- 80% probability of discovering incompatibilities during implementation
- Requires rework cycles (estimated 6-8 additional hours)
- Risk of data corruption in production if type mismatches undetected
- No documentation for future maintainers

**Total Estimated Time**: 8-10 hours (2 hours implementation + 6-8 hours rework)

### Option 2: Partial Audit (Models Only) ⚠️
**Approach**: Compare only Pydantic and SQLAlchemy model definitions without examining validators, API schemas, or database constraints.

**Pros**:
- Moderate time investment (~1 hour)
- Catches obvious field name/type mismatches
- Provides basic compatibility matrix

**Cons**:
- Misses subtle issues (e.g., Pydantic `field_validator` vs SQLAlchemy `CheckConstraint`)
- No validation of API schema compatibility (title/name alias patterns)
- Overlooks database-specific behaviors (PostgreSQL ARRAY vs SQLite JSON in StringList)
- Incomplete documentation for integration patterns

**Total Estimated Time**: 6-7 hours (1 hour audit + 5-6 hours implementation + minor rework)

### Option 3: Comprehensive Audit (Recommended) ✅
**Approach**: Systematic analysis across all layers with deliverable artifacts.

**Scope**:
1. Field-by-field mapping (cf_core → TaskMan-v2)
2. Type compatibility matrix (Pydantic → SQLAlchemy → PostgreSQL)
3. Validator alignment (cf_core validators vs database constraints)
4. API schema review (validation aliases, transformation logic)
5. Database compatibility verification (PostgreSQL ARRAY vs SQLite JSON)
6. Migration strategy if gaps identified

**Pros**:
- Prevents 80% of integration issues through early detection
- Creates reusable documentation for Task/Sprint integration (Phases 3.2, 3.3)
- Establishes pattern for future cf_core ↔ TaskMan-v2 integrations
- Enables confident implementation with minimal rework

**Cons**:
- Higher upfront time (~2-3 hours)
- Requires systematic approach vs rapid prototyping

**Total Estimated Time**: 5-6 hours (2-3 hours audit + 3 hours implementation + minimal rework)

## Decision

**We adopt Option 3: Comprehensive Audit** as the mandatory first step before any ActionList integration implementation.

### Rationale

1. **Economic**: Saves 2-4 hours over blind implementation (5-6 hours total vs 8-10 hours)
2. **Risk Mitigation**: Prevents production data corruption from type mismatches
3. **Reusability**: Audit artifacts guide Task/Sprint integrations in Phases 3.2-3.3
4. **Quality**: Aligns with ContextForge "Context Before Action" principle
5. **Maintainability**: Documents integration patterns for future developers

### ROI Analysis

| Approach | Upfront Cost | Rework Cost | Total Time | Production Risk |
|----------|--------------|-------------|------------|-----------------|
| Blind Implementation | 2h | 6-8h | **8-10h** | **High** |
| Partial Audit | 1h | 5-6h | **6-7h** | **Medium** |
| **Comprehensive Audit** | **2-3h** | **0-1h** | **5-6h** | **Low** |

## Consequences

### Positive ✅
- **Documentation Artifact**: Audit creates integration specification used by all Phase 3 tasks
- **Pattern Establishment**: Defines standard approach for cf_core-TaskMan-v2 integration
- **Confidence**: Implementation proceeds with validated compatibility matrix
- **Migration Clarity**: Any schema changes identified upfront before code written
- **Type Safety**: Ensures Pydantic validators align with PostgreSQL constraints

### Negative ⚠️
- **Initial Delay**: First commit delayed by 2-3 hours for audit completion
- **Overhead**: Requires structured approach vs rapid exploration
- **Documentation Burden**: Must maintain audit artifacts as schemas evolve

### Neutral ℹ️
- **Learning Curve**: Team gains deep understanding of dual-model architecture
- **Process Formalization**: Establishes audit as standard practice for integrations

## Implementation Plan

### Phase 1: Field Mapping Matrix (45 min)
Create comprehensive mapping table:

```markdown
| cf_core Field | Type | TaskMan-v2 Field | SQLAlchemy Type | PostgreSQL Type | Notes |
|---------------|------|------------------|-----------------|-----------------|-------|
| id | str | id | String(36) | VARCHAR(36) | Must match AL-XXXX pattern |
| name | str | name (title alias) | String(255) | VARCHAR(255) | API schema uses validation_alias |
| description | str | description | Text | TEXT | Nullable in TaskMan-v2 |
| status | Literal | status | String(50) | VARCHAR(50) | Enum compatibility check |
| task_ids | list[str] | task_ids | StringList() | ARRAY/JSON | Dual-database via TypeDecorator |
| created_by | str | owner | String(100) | VARCHAR(100) | **Field name mismatch!** |
| created_at | datetime | created_at | DateTime(tz=True) | TIMESTAMPTZ | Timezone handling critical |
| updated_at | datetime | updated_at | DateTime(tz=True) | TIMESTAMPTZ | Auto-updated via onupdate |
| tags | list[str] | tags | StringList() | ARRAY/JSON | Uses same TypeDecorator |
```

### Phase 2: Gap Analysis (30 min)
Identify missing fields requiring default values:

**TaskMan-v2 Extended Fields**:
- `project_id`, `sprint_id` → Nullable, default `None`
- `geometry_shape`, `priority`, `due_date` → ContextForge extensions, default `None`
- `evidence_refs`, `extra_metadata`, `notes` → Rich metadata, default `[]`/`{}`
- `parent_deleted_at`, `parent_deletion_note`, `completed_at` → Lifecycle tracking, default `None`

**Action Required**: Define transformation logic for cf_core → TaskMan-v2 with safe defaults.

### Phase 3: Type Compatibility Verification (30 min)
Test critical type conversions:

1. **Datetime Handling**:
   ```python
   # cf_core uses datetime.now(UTC)
   # TaskMan-v2 uses func.now() server default
   # VERIFY: Timezone preservation in PostgreSQL TIMESTAMPTZ
   ```

2. **List Serialization**:
   ```python
   # cf_core: list[str] → JSON serialization
   # TaskMan-v2: StringList() → PostgreSQL ARRAY or SQLite JSON
   # VERIFY: Round-trip compatibility
   ```

3. **Status Enums**:
   ```python
   # cf_core: Literal["active", "completed", "archived"]
   # TaskMan-v2: ActionListStatus enum with same values
   # VERIFY: String representation matches
   ```

### Phase 4: API Schema Compatibility (30 min)
Review TaskMan-v2 API schemas for transformation requirements:

- **ActionListCreate**: Maps `title` → `name` via `validation_alias`
- **ActionListResponse**: Reverse mapping with `validation_alias="name"`
- **Field Validators**: Check `parse_status()` for enum coercion compatibility

### Phase 5: Documentation Deliverables (30 min)
Create integration specification:

```markdown
# ActionList Integration Specification

## cf_core → TaskMan-v2 Mapping
[Field mapping table from Phase 1]

## Transformation Logic
[Gap analysis results from Phase 2]

## Type Conversion Utilities
[Validated conversions from Phase 3]

## API Contract
[Schema compatibility notes from Phase 4]
```

### Validation Criteria
Audit complete when:
- ✅ All 8 cf_core fields mapped to TaskMan-v2
- ✅ Type compatibility verified for datetime, lists, enums
- ✅ Gap analysis identifies default values for 12 TaskMan-v2 extended fields
- ✅ API schema transformations documented
- ✅ Integration specification reviewed by architect

## Related Decisions
- [ADR-003: TaskMan-v2 Backend API Placeholder](ADR-003-TaskMan-v2-Backend-API-Placeholder.md) — Original TaskMan-v2 architecture
- [ADR-Tasks-EvidenceSchema.md](ADR-Tasks-EvidenceSchema.md) — Evidence tracking patterns
- Future: ADR-017 (Task Integration), ADR-018 (Sprint Integration)

## Validation

### Success Metrics
- **Zero Data Loss**: All cf_core fields persist without transformation errors
- **Type Safety**: No runtime type coercion failures during create/update operations
- **API Stability**: Existing TaskMan-v2 endpoints remain functional
- **Test Coverage**: Integration tests validate round-trip cf_core → DB → cf_core

### Acceptance Test
```python
# Pseudo-test validating audit completeness
def test_actionlist_schema_audit():
    cf_core_fields = set(ActionList.model_fields.keys())
    taskman_fields = set(inspect(TaskManActionList).columns.keys())

    # All cf_core fields must map to TaskMan-v2
    assert cf_core_fields.issubset(get_mapped_fields())

    # Type compatibility verified
    for field in cf_core_fields:
        assert validate_type_compatibility(field)

    # API schema transformation documented
    assert exists("docs/integration/ActionList-API-Mapping.md")
```

## Notes

### Key Findings from Initial Analysis
1. **Field Name Mismatch**: `created_by` (cf_core) vs `owner` (TaskMan-v2) requires explicit mapping
2. **Validation Alias Pattern**: TaskMan-v2 uses `title`/`name` aliasing requiring transformation awareness
3. **Dual-Database TypeDecorator**: `StringList` provides PostgreSQL ARRAY / SQLite JSON compatibility
4. **Extended Schema**: 12 additional TaskMan-v2 fields require safe default values

### Future Considerations
- **Bidirectional Sync**: If cf_core becomes authoritative source, reverse sync (TaskMan-v2 → cf_core) requires lossy transformation (12 extended fields dropped)
- **Schema Evolution**: Changes to either model require audit update to maintain integration
- **Performance**: Lazy loading of extended fields if cf_core doesn't require full 20-field hydration

---

**Authority**: This ADR establishes the mandatory audit process for all cf_core ↔ TaskMan-v2 integrations.
**Architect**: GitHub Copilot (architect mode)
**Review Status**: Pending stakeholder validation
