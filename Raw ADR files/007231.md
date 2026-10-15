# ADR-013: Comprehensive Architecture Rewrite Over Incremental Fixes

## Status

**Accepted** - October 26, 2025

## Context

During Phase 2 pre-work (dependency updates and cleanup), we attempted to eliminate 74 type assertions as required for extraction to the target monorepo (`assertionStyle: "never"`). After completing 11/15 files (~30 assertions eliminated), we discovered that the remaining assertions were not symptoms of library limitations but were masking fundamental architectural problems.

### The Discovery

While analyzing `openApiToTypescript.ts` and `openApiToTypescript.helpers.ts`, we found:

1. **`makeSchemaResolver` lies about return types**
   - Claims to return `SchemaObject`
   - Actually returns any component type (schemas, responses, parameters, etc.)
   - Type assertions throughout codebase mask this dishonesty
   - ~20-25 assertions exist solely to "fix" the resolver's lies

2. **Not leveraging `SwaggerParser.bundle()` correctly**
   - SwaggerParser already resolves all operation-level `$ref`s
   - We're not trusting this guarantee
   - Custom resolver logic is redundant and error-prone
   - Analysis: `.agent/analysis/SWAGGER_PARSER_INTEGRATION.md`

3. **`CodeMeta` is a poorly conceived abstraction**
   - Wraps tanu's `t` types with name strings
   - No clear value proposition
   - Adds complexity without benefits
   - Makes code harder to understand and maintain
   - Analysis: `.agent/analysis/CODEMETA_ANALYSIS.md`

4. **Tanu API usage at wrong abstraction level**
   - Both `t` and `ts` from same library but don't compose well
   - Suggests incorrect API usage pattern
   - ~15-20 assertions at tanu boundary
   - Analysis: `.agent/docs/type-assertion-elimination-analysis.md`

### The Problem

**Type assertions were symptoms, not the disease.**

Attempting incremental fixes would:

- Leave architectural dishonesty in place
- Perpetuate the resolver anti-pattern
- Continue masking bugs with assertions
- Create technical debt
- Make future maintenance harder

### Alternatives Considered

**Option 1: Continue Incremental Fixes (Rejected)**

- Complete type assertion elimination file-by-file
- Work around resolver and CodeMeta issues
- Migrate to ts-morph separately later
- **Rejected:** Leaves technical debt, requires rework when fixing architecture

**Option 2: Partial Rewrite (Rejected)**

- Fix resolver only, keep CodeMeta
- Or fix CodeMeta only, keep resolver
- **Rejected:** These issues are interconnected, half-measures insufficient

**Option 3: Comprehensive 4-Phase Rewrite (Accepted)**

- Phase 0: Comprehensive test suite (safety net)
- Phase 1: Eliminate resolver + CodeMeta
- Phase 2: Migrate tanu → ts-morph
- Phase 3: Remove Zodios dependencies
- **Accepted:** Clean foundation, eliminates technical debt

## Decision

**We will perform a comprehensive 4-phase architecture rewrite instead of incremental fixes.**

### Phase Breakdown

**Phase 0: Comprehensive Public API Test Suite (8-12 hours)**

- 50-60 end-to-end tests covering entire public API
- Safety net before making architectural changes
- Prevents behavioral regressions
- Tests document expected behavior

**Phase 1: Eliminate makeSchemaResolver + CodeMeta (8-10 hours)**

- Direct schema access via `components` parameter
- Honest function signatures (return what they claim)
- Remove CodeMeta abstraction entirely
- Use native tanu `t` types directly
- Eliminates ~20-25 type assertions automatically

**Phase 2: Migrate from tanu to ts-morph (6-8 hours)**

- Replace tanu with ts-morph for AST manipulation
- Better ecosystem, more maintainable
- Type-safe code generation
- Eliminates ~15-20 tanu-boundary assertions

**Phase 3: Remove Zodios Dependencies (4-6 hours)**

- schemas-with-metadata becomes default template
- Remove Zodios from generated code
- Cleaner, more maintainable output
- Aligns with MCP use case

**Total:** 26-36 hours over 2-3 weeks

### Superseded Work

This decision supersedes:

- **Task 3.2:** Type Assertion Elimination (11/15 files complete, paused)
- **Task 2.3:** Defer Logic Analysis (completed but revealed deeper issues)

Work from Task 3.2 is preserved:

- 11 files with ~30 assertions eliminated
- Established patterns (type guards, honest types, fail-fast)
- Custom type guards created (isRequestBodyObject, isParameterObject, etc.)

### Implementation Principles

1. **TDD throughout** - All phases follow strict Test-Driven Development
2. **Quality gates always pass** - After every task: format, build, type-check, test
3. **No behavioral regressions** - Phase 0 tests protect public API
4. **Incremental progress** - Small, testable steps within each phase
5. **Documentation** - Comprehensive comments and examples

## Consequences

### Positive

✅ **Eliminates architectural dishonesty** - Functions return what they claim  
✅ **Removes ~40-50 type assertions** - Naturally, not forcefully  
✅ **Better maintainability** - Honest types, clear abstractions  
✅ **Cleaner codebase** - Removes unnecessary complexity  
✅ **Extraction ready** - No type assertions blocking monorepo extraction  
✅ **Future-proof** - ts-morph has better ecosystem than tanu  
✅ **MCP-aligned** - Zodios removal aligns with MCP use case  
✅ **Test coverage** - 50-60 new tests documenting behavior

### Negative

⚠️ **Time investment** - 26-36 hours vs continuing Task 3.2  
⚠️ **Risk** - Major refactoring could introduce bugs  
⚠️ **Context switches** - 4 distinct phases to manage  
⚠️ **Delayed completion** - Takes longer than incremental approach

### Mitigation

**Time Investment:**

- Comprehensive planning (done) reduces unknowns
- TDD approach prevents rework
- Clean foundation saves future maintenance time

**Risk:**

- Phase 0 test suite catches regressions
- Small, testable steps within phases
- Quality gates must pass after every change
- Rollback plan documented

**Context Switches:**

- Clear phase boundaries with completion criteria
- Each phase is independently valuable
- Can pause between phases if needed

**Delayed Completion:**

- Better than rushed incremental fixes
- Avoids technical debt requiring later rework
- Investment pays off in maintainability

## Related Decisions

- [ADR-001: Fail Fast on Spec Violations](./ADR-001-fail-fast-spec-violations.md) - Philosophy applied
- [ADR-002: Defer Types to openapi3-ts](./ADR-002-defer-types-to-openapi3-ts.md) - Honest types principle
- [ADR-003: Type Predicates Over Boolean Filters](./ADR-003-type-predicates-over-boolean-filters.md) - Used in Phase 1
- [ADR-004: Pure Functions and Single Responsibility](./ADR-004-pure-functions-single-responsibility.md) - Applied throughout
- [ADR-014: Migrate from tanu to ts-morph](./ADR-014-migrate-tanu-to-ts-morph.md) - Phase 2 details
- [ADR-015: Eliminate makeSchemaResolver](./ADR-015-eliminate-make-schema-resolver.md) - Phase 1 details
- [ADR-016: Remove Zodios Dependencies](./ADR-016-remove-zodios-dependencies.md) - Phase 3 details

## References

**Related ADRs:**

- [ADR-014: Migrate from tanu to ts-morph](./ADR-014-migrate-tanu-to-ts-morph.md)
- [ADR-015: Eliminate makeSchemaResolver](./ADR-015-eliminate-make-schema-resolver.md)
- [ADR-016: Remove Zodios Dependencies](./ADR-016-remove-zodios-dependencies.md)

**Requirements:**

- `.agent/requirements.md` - Core requirements this rewrite supports

## Timeline

- **October 24-25, 2025**: Phase 2 pre-work (Task 3.2 partial completion)
- **October 26, 2025**: Architecture Rewrite Decision accepted
- **November 2025**: Phase 0-3 execution (estimated 2-3 weeks)
- **December 2025**: Phase 2B (MCP Enhancements) and Phase 3 (DX Improvements)

## Commit

- This ADR documents the decision captured in planning reconciliation
- Implementation begins with Phase 0 test suite creation
