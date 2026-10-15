# ADR: Temporary Relaxation of Unused Variable Checks in CI

**Date**: 2025-01-07
**Status**: Accepted (Temporary)
**Rollback Date**: 2025-02-01

## Context

The monorepo has accumulated 300+ unused variable/parameter violations across the codebase. While ESLint enforces these rules on changed files (via `.lintstagedrc.js`), the CI type-check step was failing due to legacy technical debt.

## Decision

1. **Module Resolution**: Switch `config/typescript/tsconfig.base.json` to `moduleResolution: "bundler"` to align with Next.js/Turborepo and fix extensionless import resolution errors.

2. **CI-Only Relaxation**: Create `config/typescript/tsconfig.ci.json` that extends base config but disables `noUnusedLocals` and `noUnusedParameters` for CI type-checking only.

3. **Guardrails Preservation**: Keep strict unused checks enabled in base tsconfig. ESLint continues to enforce these rules on all changed files via lint-staged.

## Consequences

### Positive
- CI unblocked immediately without weakening day-to-day developer guardrails
- Module resolution errors fixed globally
- New code still prevented from introducing unused variables/parameters
- Technical debt contained and visible

### Negative
- Legacy unused variables temporarily hidden in CI
- Risk of drift if not addressed by rollback date

## Mitigation Strategy

1. **ESLint Enforcement**: Strict boundaries on changed files prevent new violations
2. **Rollback Date**: 2025-02-01 - Re-enable unused checks in CI after backlog reduction
3. **Tracking**: Create follow-up issues to systematically address unused variables per package
4. **Per-Package Override**: If any Node-only service shows regressions from bundler resolution, override that package's tsconfig to `"moduleResolution": "nodenext"` without reverting the base

## Implementation

```json
// config/typescript/tsconfig.ci.json (reserved for future use)
{
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "noUnusedLocals": false,
    "noUnusedParameters": false
  }
}
```

```yaml
# .github/workflows/eslint-guardrails.yml
# Type-checking is performed via turbo build step
# Each workspace uses its own tsconfig with appropriate path mappings
- name: Build workspace packages
  run: npx turbo run build --filter='@athlete-ally/*' --no-daemon
```

**Note**: Monorepo-wide `tsc --noEmit` check is not feasible due to conflicting path mappings across workspaces (e.g., `@/` resolves differently in frontend vs services). Instead, type-checking is enforced via each package's build step, which uses the package's own tsconfig.

## Rollback Plan

On or before 2025-02-01:
1. Run full type-check with base tsconfig
2. If violations < 50: Fix remaining and revert to base tsconfig in CI
3. If violations > 50: Extend rollback date by 2 weeks and create tracking issues

## References

- Original issue: CI type-check failing with 300+ unused variable errors
- Related: Module resolution errors with `@athlete-ally/*` paths
- Approved by: Engineering team decision 2025-01-07
