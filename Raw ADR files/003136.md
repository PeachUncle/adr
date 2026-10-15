# ADR 004: Feature-Based Architecture Adoption

**Status:** Accepted
**Date:** 2025-11-02
**Deciders:** Matt (HIL), Claude Code
**Related PR:** #66
**Constitutional Alignment:** v3.1 (8-12 MVP features)

---

## Context

### Problem Statement

PayPlan's codebase had grown into a flat, disorganized structure with significant technical debt:

**Symptoms:**
- 50+ loose files scattered in root directory (research, tests, temp files)
- Flat frontend structure (`components/`, `lib/`, `hooks/`, `types/`)
- Orphaned type files (not imported anywhere)
- Mixed concerns (categories + budgets + dashboard all in same folders)
- Hard to find code (budgets code spread across 4 directories)
- No clear feature boundaries
- Difficult to scale (where to add new features?)

**Measurement:**
- Root directory: 50+ items (mess)
- Frontend structure: 4 top-level dirs with mixed concerns
- Orphaned files: 7 type files with 0 imports
- Coupling: 2.8/100 (actually good, but structure didn't reflect it)
- Developer complaint: "It's a fucking mess"

**Constitutional Requirements (v3.1):**
- 8-12 MVP features required
- Each feature should be self-contained
- Clear boundaries for TDD implementation (80% coverage for `lib/**/*.ts`)
- Easy to find and modify code

---

## Decision

**Adopt feature-based architecture** with the following structure:

```text
frontend/src/
├── features/              # Self-contained feature modules
│   ├── categories/        # Spending categories (MVP #1)
│   │   ├── components/    # UI components
│   │   ├── hooks/         # React hooks
│   │   ├── lib/           # Business logic (⚠️ TEST THIS)
│   │   ├── types/         # TypeScript types
│   │   └── index.ts       # Barrel export (public API)
│   ├── budgets/           # Budget creation (MVP #2)
│   ├── dashboard/         # Dashboard (MVP #3)
│   ├── transactions/      # Transactions (MVP #8)
│   └── archive/           # Archives
└── shared/                # Shared across features
    ├── components/        # UI kit
    ├── lib/               # Utilities
    ├── hooks/             # Shared hooks
    └── types/             # Shared types
```text

**Key Principles:**
1. **Feature Colocation:** All code for a feature lives together
2. **Barrel Exports:** Each feature has `index.ts` for clean imports
3. **Shared Separation:** Code used by 2+ features goes in `shared/`
4. **Constitutional Alignment:** Structure matches 8 MVP features

---

## Alternatives Considered

### Alternative 1: Layer-Based (MVC-style)
```text
src/
├── components/    # All components
├── services/      # All services
├── hooks/         # All hooks
└── types/         # All types
```text

**Pros:**
- Familiar to developers from traditional MVC
- Clear technical layers

**Cons:**
- Feature code scattered across 4 directories
- Hard to find all code for one feature
- Doesn't match constitutional feature requirements
- Scaling issues (100+ components in one folder)

**Decision:** ❌ Rejected - Doesn't align with 8-12 feature MVP structure

---

### Alternative 2: Domain-Driven Design (Clean Architecture)
```text
src/
├── domain/           # Business entities
├── application/      # Use cases
├── infrastructure/   # External services
└── presentation/     # UI layer
```text

**Pros:**
- Strong separation of concerns
- Testable architecture
- Enterprise-grade

**Cons:**
- Over-engineered for Phase 1 (0-100 users)
- Higher cognitive load for developers
- Violates Simplicity principle (YAGNI)
- Not needed for localStorage-only app

**Decision:** ❌ Rejected - Too complex for current phase

---

### Alternative 3: Hybrid (Pages + Components)
```text
src/
├── pages/         # Route pages
├── components/    # Shared components
├── features/      # Feature-specific code
└── lib/           # Business logic
```text

**Pros:**
- Gradual migration path
- Keeps some existing structure

**Cons:**
- Still has scattered feature code
- Doesn't fully solve the problem
- Confusing (which components go where?)

**Decision:** ❌ Rejected - Half-measure, doesn't solve core issue

---

### Alternative 4: Feature-Based (CHOSEN)
```text
src/
├── features/      # Self-contained features
│   ├── categories/
│   ├── budgets/
│   └── ...
└── shared/        # Shared utilities
```text

**Pros:**
- ✅ All feature code in one place
- ✅ Matches constitutional 8-12 feature structure
- ✅ Easy to find code (all budgets in `features/budgets/`)
- ✅ Clear boundaries for testing (test each feature independently)
- ✅ Scalable (add new features easily)
- ✅ Self-documenting (features/ matches MVP list)
- ✅ Industry standard for React apps

**Cons:**
- Breaking change (all import paths change)
- Large migration (99 files moved)
- Risk of mistakes during reorganization

**Mitigations:**
- Full backup before changes (.codebase-safety/ 130MB)
- Git tracking all moves (can revert)
- Automated import path updates (sed scripts)
- Build verification after changes
- Circular dependency check (madge)

**Decision:** ✅ **ACCEPTED** - Best fit for PayPlan's needs

---

## Implementation

### Execution (2025-11-02)

**Tools Used:**
- codebase-architect (analysis + safety)
- git mv (tracked renames)
- sed (automated import updates)
- madge (circular dependency check)

**Process:**
1. Created full backup (130MB .tar.gz)
2. Created new directory structure (features/ + shared/)
3. Moved 99 files using `git mv` (tracked by git)
4. Updated 20+ import paths automatically
5. Created 5 barrel exports (index.ts)
6. Verified build (12.06s, 0 errors)
7. Checked circular dependencies (0 found)

**Timeline:** ~4 hours (analysis + reorganization + documentation)

**Safety Measures:**
- Full backup before changes ✅
- Git tracking all moves ✅
- Trash system for deleted files ✅
- Build verification ✅
- Rollback capability ✅

---

## Consequences

### Positive

1. **Developer Experience:**
   - ✅ Easy to find code (all categories in `features/categories/`)
   - ✅ Easy to add features (clear pattern to follow)
   - ✅ Clean imports (`from '@/features/categories'`)
   - ✅ Self-documenting structure

2. **Constitutional Alignment:**
   - ✅ Structure matches 8 MVP features
   - ✅ Clear boundaries for TDD (test each feature's `lib/`)
   - ✅ Supports phased development (add features to `features/`)

3. **Code Quality:**
   - ✅ Better encapsulation (features are self-contained)
   - ✅ Clear boundaries (no cross-feature imports without barrel exports)
   - ✅ Reduced coupling (features only import from `shared/` or other features)

4. **Documentation:**
   - ✅ Root directory 54% cleaner (50+ → 18 items)
   - ✅ All research in docs/research/
   - ✅ All tests in docs/testing/
   - ✅ Contributing guide (CONTRIBUTING.md)

5. **Metrics:**
   - ✅ 0 circular dependencies
   - ✅ 2.8/100 coupling score (very low)
   - ✅ Build time: 12.06s
   - ✅ TypeScript errors: 0

### Negative

1. **Breaking Changes:**
   - ❌ All import paths changed
   - ❌ Any external code referencing old paths will break
   - **Mitigation:** Migration guide in CONTRIBUTING.md, deprecation warnings

2. **Learning Curve:**
   - ❌ Developers need to learn new structure
   - ❌ "Where do I put this file?" requires understanding
   - **Mitigation:** CONTRIBUTING.md with clear examples

3. **Migration Risk:**
   - ❌ Large change (99 files moved)
   - ❌ Potential for missed import updates
   - **Mitigation:** Automated testing, build verification, full backup

4. **Test Debt:**
   - ❌ Revealed that categories/budgets/dashboard have 0 tests
   - ❌ Constitution v3.1 requires 80% coverage for lib/**/*.ts
   - **Mitigation:** Deferred to follow-up PR (high priority)

### Neutral

1. **Documentation Burden:**
   - New structure requires documentation
   - CONTRIBUTING.md created to address this
   - CLAUDE.md updated with new structure

2. **Tooling:**
   - IDEs may need import path updates
   - Auto-import may need configuration
   - TypeScript paths aliases already support new structure

---

## Compliance

### Constitutional (v3.1)

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. Privacy-First | ✅ N/A | No changes to localStorage strategy |
| II. Accessibility-First | ✅ N/A | No UI changes |
| III. Free Core | ✅ N/A | No pricing changes |
| IV. Visual-First | ✅ N/A | No design changes |
| V. Mobile-First | ✅ N/A | No responsive changes |
| VI. Quality-First | ⚠️ **PARTIAL** | Good structure, but tests missing |
| VII. Simplicity | ✅ **MET** | Clear, simple structure |
| IX. Specification-Driven | ✅ N/A | Reorganization only |

**Overall:** ✅ Compliant (test debt deferred to follow-up)

### Phase 1 Definition of Done

| Criterion | Status | Notes |
|-----------|--------|-------|
| Functional | ✅ **MET** | Build working, 0 errors |
| TDD for Business Logic | ⚠️ **DEFERRED** | To be added in follow-up PR |
| Manual UI Testing | ✅ **N/A** | No UI changes |
| Accessibility | ✅ **N/A** | No UI changes |
| Privacy | ✅ **MET** | No privacy changes |
| Error Handling | ✅ **MET** | Existing error handling preserved |
| Responsive | ✅ **N/A** | No UI changes |
| Documented | ✅ **MET** | CONTRIBUTING.md, updated CLAUDE.md |

**Overall:** ✅ Acceptable for structural PR (test debt acknowledged)

---

## Follow-Up Actions

### Immediate (Before Next Feature):
1. ✅ Create Linear issue: "Add TDD for categories/budgets business logic" (HIGH priority)
2. ✅ Create Linear issue: "Migrate remaining @/lib imports to @/shared/lib" (MEDIUM priority)
3. ✅ Create Linear issue: "Add TOC to CLAUDE.md/CONTRIBUTING.md" (LOW priority)

### Medium-Term (This Month):
1. Implement TDD for existing business logic (60% coverage target)
2. Update any external tooling/scripts to use new paths
3. Monitor for any missed import path updates

### Long-Term (Next Quarter):
1. Evaluate feature boundaries (are they correct?)
2. Consider if any features should be split or merged
3. Review if shared/ is appropriate size (not a dumping ground)

---

## Metrics & Success Criteria

### Success Metrics (Measured 2025-11-02):

| Metric | Before | After | Target | Status |
|--------|--------|-------|--------|--------|
| Root items | 50+ | 18 | <25 | ✅ EXCEEDED |
| Feature directories | 0 | 5 | 5-8 | ✅ MET |
| Orphaned types | 7 | 0 | 0 | ✅ MET |
| Circular deps | 0 | 0 | 0 | ✅ MET |
| Build time | 15.41s | 12.06s | <20s | ✅ IMPROVED |
| TypeScript errors | 0 | 0 | 0 | ✅ MET |
| Test coverage | ~4% | ~4% | 60% | ⚠️ DEFERRED |

### Validation:

**Build Verification:**
```bash
cd frontend && npm run build
# ✓ built in 12.06s
# 0 TypeScript errors
```text

**Circular Dependency Check:**
```bash
npx madge --circular frontend/src
# ✔ No circular dependency found!
```text

**Import Verification:**
- ✅ All barrel exports working
- ✅ Clean imports (`from '@/features/categories'`)
- ⚠️ Some verbose imports remain (acceptable)

---

## References

### Related Documents:
- [Constitutional Alignment Strategy](../test_results/CONSTITUTIONAL_ALIGNMENT_STRATEGY.md)
- [Complete Cleanup Report](../archive/COMPLETE_CLEANUP_REPORT.md)
- [Organization Summary](../ORGANIZATION_SUMMARY.md)
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Structure guide

### Related PRs:
- PR #66: Complete codebase reorganization (this ADR)
- PR #64: BNPL removal (created need for cleanup)

### Related Issues:
- MMT-61: Spending Categories & Budgets (first feature-based implementation)
- MMT-62: Dashboard (second feature-based implementation)

### Research:
- [Feature-Based Architecture Patterns](../../tools/codebase-architect/references/javascript-patterns.md)
- [React Best Practices 2025](../research/COMPETITOR-DESIGN-SYSTEM-ANALYSIS.md)

---

## Decision Drivers

### Technical Drivers:
1. **Scalability:** Flat structure doesn't scale beyond 5-10 features
2. **Maintainability:** Scattered code hard to modify safely
3. **Testability:** Clear boundaries needed for TDD (v3.1 requirement)
4. **Developer Experience:** "Where do I put this?" needs obvious answer

### Business Drivers:
1. **Constitutional Mandate:** 8-12 MVP features need clear structure
2. **Team Growth:** Structure must support future developers
3. **Code Quality:** Professional structure attracts contributors
4. **Velocity:** Finding code faster = shipping features faster

### Risk Drivers:
1. **Technical Debt:** Messy structure accumulates debt quickly
2. **Onboarding:** New developers lost in flat structure
3. **Refactoring Safety:** No clear boundaries = risky changes

---

## Implementation Details

### Migration Strategy

### Phase 1: Analysis (1 hour)
- Used codebase-architect to analyze structure
- Identified 99 files to reorganize
- Mapped features to constitutional requirements

### Phase 2: Execution (2 hours)
- Created backup (130MB)
- Moved files with `git mv` (tracked renames)
- Updated 20+ import paths (automated with sed)
- Created 5 barrel exports

### Phase 3: Verification (1 hour)
- Build verification (12.06s, 0 errors)
- Circular dependency check (0 found)
- Documentation (CONTRIBUTING.md, updated CLAUDE.md)

**Total Time:** ~4 hours

### File Moves

**Categories Feature (20 files):**
```text
components/categories/* → features/categories/components/
lib/categories/*        → features/categories/lib/
hooks/useCategories.ts  → features/categories/hooks/
types/category.ts       → features/categories/types/
```text

**Budgets Feature (18 files):**
```text
components/budgets/* → features/budgets/components/
lib/budgets/*        → features/budgets/lib/
hooks/useBudgets.ts  → features/budgets/hooks/
types/budget.ts      → features/budgets/types/
```text

**Dashboard Feature (24 files):**
```text
components/dashboard/* → features/dashboard/components/
lib/dashboard/*        → features/dashboard/lib/
hooks/useDashboard*    → features/dashboard/hooks/
types/chart-data.ts    → features/dashboard/types/
types/gamification.ts  → features/dashboard/types/
types/dashboard.ts     → features/dashboard/types/
```text

**Transactions Feature (8 files):**
```text
components/transactions/* → features/transactions/components/
lib/transactions/*        → features/transactions/lib/
types/transaction.ts      → features/transactions/types/
```text

**Archive Feature (29 files):**
```text
components/archive/* → features/archive/components/
lib/archive/*        → features/archive/lib/
hooks/usePayment*    → features/archive/hooks/
```text

**Shared Utilities (moved to shared/):**
```text
components/ui/*           → shared/components/ui/
components/ErrorAlert.tsx → shared/components/
lib/utils.ts              → shared/lib/
lib/csv.ts                → shared/lib/
lib/api.ts                → shared/lib/
lib/validation/*          → shared/lib/validation/
types/bill.ts             → shared/types/
types/goal.ts             → shared/types/
```text

**Total:** 99 files reorganized

### Barrel Exports Created

Each feature now has `index.ts`:

```typescript
// features/categories/index.ts
export * from './lib';                    // Business logic
export { CategoryCard } from './components/CategoryCard';
export { useCategories } from './hooks/useCategories';
```text

**Benefits:**
- Clean imports: `import { CategoryCard } from '@/features/categories'`
- Single source of truth for public API
- Easy to see what each feature exports

---

## Risks & Mitigations

### Risk 1: Breaking Changes
**Risk:** All old import paths break immediately
**Likelihood:** HIGH
**Impact:** HIGH
**Mitigation:**
- ✅ Migration guide in CONTRIBUTING.md
- ✅ Build verification (catches broken imports)
- ✅ Full backup available for rollback

### Risk 2: Missed Import Updates
**Risk:** Some imports not updated, cause runtime errors
**Likelihood:** MEDIUM
**Impact:** HIGH
**Mitigation:**
- ✅ Automated updates (sed scripts)
- ✅ TypeScript compilation catches errors
- ✅ Build verification (0 errors)

### Risk 3: Test Coverage Gaps Exposed
**Risk:** Reorganization reveals 0 tests for categories/budgets
**Likelihood:** HIGH (already discovered)
**Impact:** MEDIUM (deferred to follow-up)
**Mitigation:**
- ⚠️ Create Linear issue (HIGH priority)
- ⚠️ Add tests before next feature
- ✅ Constitution v3.1 mandates TDD going forward

### Risk 4: Lost Productivity During Transition
**Risk:** Developers confused by new structure
**Likelihood:** MEDIUM
**Impact:** LOW
**Mitigation:**
- ✅ CONTRIBUTING.md created
- ✅ CLAUDE.md updated
- ✅ Clear examples in documentation

---

## Lessons Learned

### What Went Well:
1. ✅ **Safety features worked perfectly** - Backup system prevented data loss
2. ✅ **Git mv preserved history** - Can trace file origins
3. ✅ **Automated import updates** - Saved hours of manual work
4. ✅ **Codebase-architect tool** - Professional analysis
5. ✅ **Constitutional alignment** - Structure matches MVP features

### What Could Improve:
1. ⚠️ **Should have added tests BEFORE reorganization** - Missed safety net
2. ⚠️ **Entry point detection** - Dead code detector had false positives
3. ⚠️ **Gradual migration** - Could have been phased (one feature at a time)

### For Next Time:
1. Add tests BEFORE major refactoring (safety net)
2. Consider phased migration (reduce risk)
3. Use feature flags for gradual rollout

---

## Future Considerations

### When to Revisit This Decision:

**Triggers for re-evaluation:**
1. Feature count >15 (may need subdomains)
2. Shared/ grows >50% of codebase (too much shared code)
3. Features start importing heavily from each other (wrong boundaries)
4. Monorepo split (would change structure entirely)

**Review Schedule:** Quarterly during architectural health checks

### Potential Evolution:

**If PayPlan grows to 50+ features:**
```text
features/
├── budgeting/       # Subdomain
│   ├── categories/
│   ├── budgets/
│   └── goals/
├── analytics/       # Subdomain
│   ├── reports/
│   └── insights/
└── ...
```text

**If PayPlan goes multi-platform:**
```text
packages/
├── web/              # Web app (current frontend/)
├── mobile/           # React Native
├── shared-domain/    # Shared business logic
└── shared-ui/        # Shared components
```text

---

## Approval

**Approved by:** Matt (HIL) - @mmtuentertainment (Architecture owner)
**Date:** 2025-11-02
**Reviewed by:** Claude Code Bot (PR #66 review), CodeRabbit AI (PR #66 review)
**Constitutional Compliance:** ✅ Aligned with v3.1

**Supersedes:** N/A (first major architectural decision)
**Superseded by:** N/A (current)

---

## Changelog

- **2025-11-02:** Initial decision and implementation
- **PR #66:** Complete codebase reorganization to feature-based architecture

---

**This ADR documents the most significant architectural change in PayPlan's history, transforming it from a messy flat structure to a professional, scalable, feature-based architecture aligned with constitutional requirements.**
