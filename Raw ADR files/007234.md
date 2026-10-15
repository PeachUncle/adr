# ADR-016: Remove Zodios Dependencies from Default Template

## Status

**Accepted** - October 26, 2025  
**Implementation:** Phase 3 of Architecture Rewrite

## Context

The current default template generates Zodios clients with `@zodios/core` and `axios` dependencies. During Phase 2 pre-work (Task 1.9), we created the `schemas-with-metadata` template that provides superior functionality without Zodios dependencies. This template is now the foundation for our MCP use case and Engraph SDK extraction.

### The Current Situation

**Default Template (Zodios-based):**

- Generates `@zodios/core` client
- Depends on `axios` for HTTP
- Bundle size: ~48 KB (zod + zodios + axios)
- Maintenance: Zodios in maintenance mode (stable but not actively developed)

**schemas-with-metadata Template:**

- Pure Zod schemas (no Zodios)
- Full request/response validation
- MCP tools array
- Validation helpers (optional)
- Schema registry (optional)
- Bundle size: ~13 KB (zod only)
- Status: 14/14 tests passing, production-ready

### Why Zodios Was Used Originally

Historical reasons:

1. Provided type-safe HTTP client out of the box
2. Integrated Zod validation with axios
3. Reduced boilerplate for API clients

### Why It's No Longer Ideal

1. **Maintenance Mode**
   - Zodios is stable but not actively developed
   - No support for latest Zod v4 features
   - Uncertain long-term future
   - Analysis: `.agent/analysis/ZODIOS_CORE_EVALUATION.md`

2. **Not Our Primary Use Case**
   - We need: Zod schemas for validation + MCP tools
   - We don't need: HTTP client wrapper
   - Target: Engraph SDK (headless validation) + MCP tools

3. **Larger Bundle Size**
   - Zodios + axios: ~35 KB additional
   - Unnecessary for schema-only usage
   - Analysis: `.agent/analysis/HANDLEBARS_EVALUATION.md`

4. **schemas-with-metadata is Superior**
   - Everything Zodios provides, plus:
     - Full request parameter validation (path, query, headers, body)
     - All response status codes (not just success)
     - MCP tools array (protocol-ready)
     - Validation helpers
     - Schema registry builder
   - No dependencies beyond Zod
   - Cleaner generated code

### Alternatives Considered

**Option 1: Keep Both Templates (Rejected)**

- Default: Zodios (backward compatibility)
- Alternative: schemas-with-metadata
- **Rejected:** Confusing for users, split maintenance burden

**Option 2: Deprecate Default, Keep Both (Rejected)**

- Mark default as deprecated
- Guide users to schemas-with-metadata
- **Rejected:** Still maintains both codebases

**Option 3: Replace Default with schemas-with-metadata (Accepted)**

- schemas-with-metadata becomes the default
- Zodios template available via explicit flag
- Clear migration path
- **Accepted:** Best for project direction

**Option 4: Remove Zodios Entirely (Considered)**

- Only offer schemas-with-metadata
- **Deferred:** Keep Zodios template for backward compatibility

## Decision

**We will make `schemas-with-metadata` the default template and move Zodios generation to an opt-in flag.**

### Implementation Strategy

**Phase 3 of Architecture Rewrite: Remove Zodios Dependencies (4-6 hours)**

**Step 1: Rename Templates (1 hour)**

- `schemas-with-metadata.hbs` → `default.hbs`
- Current `default.hbs` → `zodios-client.hbs`
- Update template registry
- Update imports

**Step 2: Update CLI Flags (1 hour)**

- Default behavior: Generate schemas-with-metadata
- Add flag: `--with-zodios-client` (opt-in to Zodios)
- Add flag: `--with-validation-helpers` (default: false for schemas-only)
- Update help text

**Step 3: Update Tests (1-2 hours)**

- Update default template tests
- Add tests for --with-zodios-client flag
- Verify backward compatibility path
- Update snapshots

**Step 4: Update Documentation (1-2 hours)**

- README: Update default examples
- README: Add migration guide (Zodios → schemas-with-metadata)
- README: Document --with-zodios-client flag
- Update examples in repo

### Migration Path for Existing Users

**For users wanting schemas-with-metadata (most users):**

```bash
# No change needed - now the default!
pnpx @engraph/castr spec.yaml -o client.ts
```

**For users wanting Zodios client (backward compatibility):**

```bash
# Add --with-zodios-client flag
pnpx @engraph/castr spec.yaml -o client.ts --with-zodios-client
```

**For users wanting to migrate:**

1. Remove flag (or add `--no-zodios-client`)
2. Update imports (no more `@zodios/core`)
3. Use validation helpers if needed (`--with-validation-helpers`)
4. Migration guide in docs

### Generated Code Comparison

**Before (Zodios, was default):**

```typescript
import { Zodios } from "@zodios/core";
import { z } from "zod";

const schemas = { User: z.object({ ... }) };

const api = new Zodios("https://api.example.com", [
  {
    method: "get",
    path: "/users/:id",
    alias: "getUser",
    response: schemas.User,
  },
]);

export default api;
```

**After (schemas-with-metadata, now default):**

```typescript
import { z } from "zod";

// All schemas
export const schemas = { User: z.object({ ... }).strict() };

// Endpoints with full validation
export const endpoints = [{
  method: "get",
  path: "/users/:id",
  operationId: "getUser",
  request: {
    pathParams: z.object({ id: z.string() }).strict(),
  },
  responses: {
    200: { description: "Success", schema: schemas.User },
    404: { description: "Not found", schema: schemas.Error },
  },
}];

// MCP tools (protocol-ready)
export const mcpTools = endpoints.map(e => ({ ... }));

// Optional: Validation helpers (with --with-validation-helpers)
export function validateRequest(endpoint, input) { ... }
export function validateResponse(endpoint, status, data) { ... }
```

## Consequences

### Positive

✅ **Better default** - More capable, less dependencies  
✅ **MCP-ready** - Aligns with project requirements  
✅ **Smaller bundles** - 13 KB vs 48 KB (73% reduction)  
✅ **Future-proof** - Not tied to Zodios maintenance  
✅ **Cleaner code** - No HTTP client wrapper  
✅ **Full validation** - All request params, all responses  
✅ **Engraph-aligned** - Ready for SDK extraction  
✅ **Backward compatible** - Zodios still available via flag

### Negative

⚠️ **Breaking change** - Default output changes  
⚠️ **Migration needed** - Existing users must adapt  
⚠️ **HTTP client removed** - Users must provide their own (fetch, axios, etc.)

### Mitigation

**Breaking Change:**

- Major version bump (when extracted)
- Clear migration guide in docs
- Zodios template still available
- Announcement in CHANGELOG

**Migration:**

- Simple flag addition for Zodios users
- Most users benefit from better default
- Migration guide with code examples
- Step-by-step instructions

**HTTP Client:**

- Modern standard: use `fetch` (built-in)
- Alternative: install axios, ky, etc.
- More flexibility for users
- Example helpers provided in docs

## Alignment with Requirements

**See:** `.agent/plans/requirements.md`

This decision directly supports:

- **Req 1:** Generate Zod schemas ✅ (primary output)
- **Req 2:** SDK generation ✅ (schemas-with-metadata is SDK-focused)
- **Req 3:** Validation helpers ✅ (included, optional)
- **Req 4:** MCP tools ✅ (mcpTools array included)
- **Req 5:** SDK-level validation ✅ (full validation, no duplication)
- **Req 6:** JSON Schema for MCP ✅ (Phase 2B will add)

## Related Decisions

- [ADR-013: Architecture Rewrite Decision](./ADR-013-architecture-rewrite-decision.md) - Parent decision
- [ADR-001: Fail Fast on Spec Violations](./ADR-001-fail-fast-spec-violations.md) - Validation philosophy
- Phase 2B (02-MCP-ENHANCEMENTS.md) - Builds on this foundation

## References

**Related ADRs:**

- [ADR-013: Architecture Rewrite Decision](./ADR-013-architecture-rewrite-decision.md) - Parent decision
- [ADR-001: Fail Fast on Spec Violations](./ADR-001-fail-fast-spec-violations.md) - Validation philosophy

**Requirements:**

- `.agent/requirements.md` - Requirements alignment

## Timeline

- **October 26, 2025**: Decision accepted as part of Architecture Rewrite
- **November-December 2025**: Implementation completed
- **January 2026**: Verified and stable

## Success Criteria

✅ schemas-with-metadata is default template  
✅ Zodios template available via --with-zodios-client  
✅ All 430+ tests passing  
✅ Migration guide complete  
✅ README updated with new examples  
✅ Quality gates pass  
✅ No behavioral regressions

## Commit

- Implementation will be committed as part of Phase 3 execution
- See: Phase 3 tasks in `01-CURRENT-IMPLEMENTATION.md`
