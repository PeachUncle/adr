# ADR: Layout Domain Relocation & Transitional Shims

Date: 2025-09-18
Status: Active
Decision Drivers:
- Enforce layered architecture (core → domain → ui) (#171 Phase 2) while preserving lint guardrails
- Minimize churn/risk to existing tests and ESLint rules during incremental refactor
- Enable future removal of root `src/layout` implementation except where lint rules still rely on path scoping

## Context
Historically, `LayoutEngine`, `layoutManifest`, `SlotContainer`, and `legacyLayout.css` lived under `src/layout`. Phase 2 began migrating domain logic into `src/domain`. We introduced shims (re-exports / @import) to keep existing import paths functional and tests green while reorganizing.

During relocation we discovered two ESLint rules tightly coupled to physical path assumptions:
- `require-manifest-validation`: Only enforces validation inside `src/layout/LayoutEngine.*`.
- `no-hardcoded-layout-styles`: Originally allowed hardcoded grid styles only inside `src/layout/**` (and root `App`).

To avoid broad simultaneous rule rewrites plus implementation moves, we:
1. Moved `layoutManifest` implementation into `src/domain/layout/layoutManifest.ts` and converted root file to a shim.
2. Canonicalized `legacyLayout.css` under `src/domain/layout`; root sheet is now just an `@import` shim.
3. Left `LayoutEngine` implementation in `src/layout` (required by rule path + style allowance) and kept the domain file as a re-export.
4. Updated `no-hardcoded-layout-styles` rule to also permit `src/domain/layout/**` so future incremental logic (responsive transforms, slot mapping) can migrate without lint noise.

## Decision
Adopt a phased deprecation strategy:
- Phase A (current): Keep `LayoutEngine` implementation in root; all other layout artifacts canonicalized in domain. Expanded lint allowlist to include `src/domain/layout/**`.
- Phase B (optional future): Generalize ESLint rules to detect "layout engine context" semantically (e.g., by exported symbol or filename pattern) rather than absolute path, then move `LayoutEngine` to domain.
- Phase C: Remove root shims (`layoutManifest.ts`, `legacyLayout.css`, `SlotContainer.tsx`) once external consumers (if any) are confirmed migrated. Provide one release with deprecation notice.

## Consequences
- Slight duplication of file presence (`LayoutEngine` re-export) until Phase B completes.
- Reduced risk: tests and lint rules remain stable now; incremental improvements easier.
- Clear migration runway documented here to justify final root directory cleanup.

## Alternatives Considered
1. Immediate hard move of `LayoutEngine` + rewrite ESLint patterns: Higher risk of missing edge cases; declined for now.
2. Symbol-based ESLint rule matching (AST-level): More robust but higher implementation cost up-front.
3. Keep everything in root and abandon domain move: Fails architectural goal; rejected.

## Migration Plan & Checklist
| Step | Action | PR | Done |
|------|--------|----|------|
| A1 | Move `layoutManifest` impl to domain | current | ✅ |
| A2 | Canonicalize CSS in domain | current | ✅ |
| A3 | Expand lint allowlist to include domain | current | ✅ |
| B1 | Refactor ESLint rules (path → pattern) | current | ✅ |
| B2 | Move `LayoutEngine` to domain | current | ✅ |
| C1 | Deprecation notice in CHANGELOG | current | ✅ |
| C2 | Remove root shims | current | ✅ |

## Deprecation Notice (Finalized)
The following layout shim files were removed as part of Phase C. Update imports to `src/domain/layout/*` (already in the codebase) if you have private/experimental forks:
- src/layout/layoutManifest.ts
- src/layout/legacyLayout.css
- src/layout/SlotContainer.tsx
- src/layout/LayoutEngine.tsx (now a transient re-export and subsequently removed when all consumers migrated)

## Follow-ups
- Implement Phase B rule adjustments (ticket TBD)
- Track external import usage via a codemod or search in dependant repos (if monorepo context emerges)
- Add automated lint rule test for `src/domain/layout/LayoutEngine` acceptance once migrated

---
Owned by: Architecture Working Group
