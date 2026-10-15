# ADR-0011: ArkType for Schema Validation

**Status:** Accepted
**Date:** 2025-11-07
**Deciders:** Jace Babin

## Context

Plugin manifests (`plugin.json`, `marketplace.json`) and skill frontmatter (`SKILL.md` YAML) are currently not validated before commit or deployment. This leads to runtime errors when Claude Code attempts to load plugins with invalid schemas.

**Current incident:**

The workflow plugin is broken due to an invalid hooks schema structure. We used an array format `"hooks": [...]` instead of the required nested object structure `"hooks": { "hooks": { ... } }`. This error was only discovered after pushing to the marketplace, breaking the plugin for all users.

**Error message:**

```txt
Plugin workflow has an invalid manifest file.
Validation errors: hooks: Invalid input
```

**Problem scope:**

- No validation at commit/push time
- Schema errors only caught at Claude Code runtime
- Unclear error messages from Claude Code's internal validator
- No guidance on correct schema structure
- Affects all plugins: meta, design-system, workflow, etc.

**Constraints:**

- Must validate before code reaches marketplace
- Must be fast (<500ms for typical commits)
- Must provide clear, actionable error messages
- Must catch all schema issues (structure, types, required fields)

## Decision

We will implement a **multi-layer schema validation system using ArkType** to validate all plugin manifests and skill frontmatter before they reach the marketplace.

**Components:**

1. **ArkType schema definitions** for all manifest types
2. **CLI validation tool** (`scripts/validate-schemas.ts`)
3. **Git hooks** (pre-commit for changed files, pre-push for all)
4. **NPM scripts** for manual validation
5. **Clear error messages** with file paths and expected formats

## Alternatives Considered

### Option 1: ArkType

**Description:**

TypeScript-native schema validation library using string literal syntax. Provides runtime validation with TypeScript inference.

**Pros:**

- 10x+ faster runtime validation than Zod
- Concise syntax: `type("string")` vs `z.string()`
- Smaller bundle size (~10KB vs ~50KB for Zod)
- TypeScript-native inference (no code generation)
- Better error messages with path information
- Pure TypeScript (no dependencies)

**Cons:**

- Smaller ecosystem than Zod
- Less documentation/examples
- Newer library (less battle-tested)
- Fewer community resources

**Decision:** ✅ Selected

**Rationale:** For CLI validation tools, runtime performance and bundle size don't matter much, but the concise syntax and excellent TypeScript integration make ArkType ideal. The error messages are superior for developer experience. Since we're not shipping this in a client bundle and validation frequency is low, maturity concerns are minimal.

### Option 2: Zod

**Description:**

Popular TypeScript-first schema validation library with declarative API.

**Pros:**

- Mature ecosystem (widely adopted)
- Extensive documentation and examples
- Strong community support
- Can generate JSON Schema for IDE autocomplete
- Many integrations (tRPC, React Hook Form, etc.)
- Battle-tested in production

**Cons:**

- Slower runtime validation (10x vs ArkType)
- Larger bundle size
- More verbose syntax: `z.object({ ... })`
- Extra step to generate TypeScript types

**Decision:** ❌ Rejected

**Rationale:** While Zod is more mature, the performance and syntax advantages of ArkType outweigh ecosystem size for our CLI use case. We don't need the integrations that make Zod popular for frontend validation.

### Option 3: JSON Schema + AJV

**Description:**

Standard JSON Schema with AJV validator. Industry standard approach.

**Pros:**

- Industry standard (JSON Schema spec)
- Language-agnostic (could validate from other tools)
- IDE support (many editors understand JSON Schema)
- Can generate TypeScript types via json-schema-to-typescript
- Extremely mature and well-documented

**Cons:**

- TypeScript types are generated, not inferred
- More boilerplate (separate schema files)
- Less type-safe (disconnect between schema and types)
- Verbose schema definitions
- Extra dependencies (ajv, json-schema-to-typescript)

**Decision:** ❌ Rejected

**Rationale:** JSON Schema is excellent for language-agnostic validation, but we're in a TypeScript monorepo. The type generation step and schema verbosity make it less ergonomic than ArkType for our use case.

### Option 4: Custom Validation Scripts

**Description:**

Hand-written validation functions with manual type checking.

**Pros:**

- No dependencies
- Full control over error messages
- Simple implementation
- No learning curve

**Cons:**

- More code to maintain
- Error-prone (manual validation logic)
- No TypeScript inference
- Must manually update for schema changes
- Harder to ensure completeness

**Decision:** ❌ Rejected

**Rationale:** Custom validation is tempting for simplicity, but schema libraries provide better error messages, type safety, and maintainability. The small dependency cost is worth the robustness.

## Consequences

### Positive

- **Catch errors early**: Schema issues found at commit time, not runtime
- **Better error messages**: Clear feedback with file paths and expected formats
- **Faster debugging**: Developers know immediately what's wrong
- **Prevent broken deployments**: Invalid schemas blocked before reaching marketplace
- **Multi-layer safety**: Pre-commit (fast) + pre-push (thorough) + manual validation
- **Type safety**: ArkType infers TypeScript types from schemas
- **Fast validation**: <500ms for typical commits (changed files only)

### Negative

- **New dependency**: Add ArkType to devDependencies
- **Maintenance burden**: Must keep schemas in sync with Claude Code updates
- **Git hook overhead**: Adds ~100-500ms to commit process
- **Learning curve**: Team must understand ArkType syntax
- **Schema duplication**: Our schemas mirror Claude Code's internal schemas

### Neutral

- **Validation is mandatory**: Commits blocked on validation failures
- **Manual override**: Developers can skip hooks if necessary (`--no-verify`)
- **CLI validation available**: `bun run validate` for manual checks

## Implementation Notes

**How will this be enforced?**

1. **Git hooks via Lefthook:**
   - Pre-commit: Validate changed files only (<500ms target)
   - Pre-push: Validate all schemas (<2s target)

2. **NPM scripts:**
   - `bun run validate` - All schemas
   - `bun run validate:plugins` - Just plugins
   - `bun run validate:marketplace` - Just marketplace

3. **File structure:**

```sh
schemas/
├── plugin.schema.ts          # plugin.json validation
├── marketplace.schema.ts     # marketplace.json validation
└── skill-frontmatter.schema.ts  # SKILL.md YAML validation

scripts/
└── validate-schemas.ts       # CLI validator
```

**When does this take effect?**

- Immediately upon merge
- Existing plugins must be validated and fixed
- New plugins must pass validation before commit

**What needs to change to comply?**

1. Fix workflow plugin hooks schema (immediate blocker)
2. Validate all existing plugins
3. Update any invalid schemas
4. Add validation to commit workflow

**Error message format:**

```txt
❌ Validation failed: plugins/workflow/.claude-plugin/plugin.json

  Line 22: "hooks" field

  Expected one of:
    - String path: "./hooks.json"
    - Object: { "hooks": { "SessionStart": [...] } }

  Found: Array (old schema format)

  Fix: Restructure hooks as nested object or extract to hooks.json

  See: https://code.claude.com/docs/en/hooks.md
```

## References

**Related ADRs:**

- [ADR-0008: No Auto-Formatting Hooks](ADR-0008-no-auto-formatting-hooks.md) - Hook design constraints
- [ADR-0010: Hook Type Selection](ADR-0010-hook-type-selection.md) - Command vs prompt hooks

**OpenSpec Proposals:**

- [openspec/changes/add-schema-validation/](../../../openspec/changes/add-schema-validation/) - Implementation plan

**External Resources:**

- [ArkType Documentation](https://arktype.io/docs)
- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference.md)
- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks.md)
- [JSON Schema Specification](https://json-schema.org/)

## Notes

**Why not wait for Claude Code to provide better error messages?**

We can't control Claude Code's validator or timeline. We need immediate protection against schema errors. Even if Claude Code improves errors, our validation provides earlier feedback (at commit vs load time).

**What if Claude Code's schema changes?**

We'll need to update our schemas accordingly. This is acceptable maintenance overhead given the benefits. We can monitor Claude Code releases and update schemas as needed.

**Should we validate hook script syntax (TypeScript)?**

No - TypeScript validation is handled by `tsc` and the type-checker hook. This ADR focuses solely on manifest/frontmatter JSON/YAML schema validation.

**Future considerations:**

- Auto-fix capabilities for common issues
- Generate JSON Schema files for IDE autocomplete
- CI/CD integration (GitHub Actions)
- Schema versioning if Claude Code adds breaking changes
