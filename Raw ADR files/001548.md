# ADR-010: DRY Improvements - Constants, Hooks, and Utilities

**Status:** Accepted  
**Date:** November 2, 2025  
**Context:** Day 7 Phase 5 - Code Quality & DRY Improvements  
**Related:** [Day 7 Plan](../../planning/DAY_7_QA_FRONTEND_IMPROVEMENTS.md), [DRY Audit](../DRY_AUDIT_REPORT.md)

---

## Context

During the Day 7 audit, we identified **7 major duplication patterns** across 50+ files:

1. **Rate Limiting Values** - 3 different rate limit systems with hardcoded values
2. **Prompt Fetching Logic** - 5 different implementations of prompt queries
3. **Pattern Fetching Logic** - 4 different implementations
4. **User-Facing Messages** - Hardcoded strings in 30+ files
5. **Validation Logic** - Duplicate Zod schemas in 10+ API routes
6. **Admin CLI Scripts** - 10+ one-off scripts doing similar tasks
7. **MongoDB Queries** - Duplicate query builders in 20+ files

This duplication caused:
- **Maintenance overhead**: Changes required updating 5-10 files
- **Inconsistency**: Different implementations caused subtle bugs
- **Testing complexity**: Duplicate code meant duplicate tests
- **Hard to find values**: Magic numbers scattered everywhere

---

## Decision

Implement a systematic DRY approach with **single sources of truth**:

### 1. Constants Layer
Create centralized constant files:
- `src/lib/constants/rates.ts` - All rate limiting values
- `src/lib/constants/limits.ts` - All thresholds and boundaries
- `src/lib/constants/messages.ts` - All user-facing strings

### 2. Hooks Layer
Create reusable React hooks for client components:
- `src/hooks/usePrompts.ts` - Prompt fetching with SWR
- `src/hooks/usePatterns.ts` - Pattern fetching with SWR
- Both include pagination, search, filtering, and caching

### 3. Validation Layer
Create common Zod schemas:
- `src/lib/utils/validation.ts` - Reusable validation schemas
- Common patterns (IDs, pagination, content, filters)
- Helper functions (sanitization, normalization)

### 4. Admin CLI Layer
Consolidate 10+ scripts into one unified tool:
- `scripts/admin/engify-admin.ts` - Single admin CLI
- Subcommands for stats, users, prompts, database
- Consistent interface, better discoverability

---

## Implementation Details

### Constants Structure

```typescript
// src/lib/constants/rates.ts
export const AI_RATE_LIMITS = {
  anonymous: { perMinute: 3, perHour: 3, perDay: 10 },
  authenticated: { perMinute: 20, perHour: 20, perDay: 100 },
  pro: { perMinute: 200, perHour: 200, perDay: 2000 },
} as const;

// src/lib/constants/limits.ts
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  MIN_PAGE_SIZE: 1,
} as const;

// src/lib/constants/messages.ts
export const ERROR_MESSAGES = {
  RATE_LIMIT_EXCEEDED: 'Rate limit exceeded. Please try again later.',
  AUTH_REQUIRED: 'Please sign in to continue.',
} as const;
```

### Hooks Pattern

```typescript
// src/hooks/usePrompts.ts
export function usePrompts(filters: PromptFilters = {}) {
  const { data, error, isLoading } = useSWR(
    ['/api/prompts', filters],
    () => fetchPrompts(filters),
    { dedupingInterval: CACHE_TTL.PROMPTS_LIST * 1000 }
  );
  
  return { prompts: data?.prompts ?? [], error, isLoading };
}
```

### Validation Pattern

```typescript
// src/lib/utils/validation.ts
export const commonSchemas = {
  userId: z.string().min(1, 'User ID is required'),
  pagination: z.object({
    limit: z.number().min(1).max(100).default(20),
    skip: z.number().min(0).default(0),
  }),
};
```

### Admin CLI Pattern

```bash
# Before: 10+ separate scripts
pnpm exec tsx scripts/admin/check-prompts-count.js
pnpm exec tsx scripts/admin/check-beta-requests.js
pnpm exec tsx scripts/admin/db-stats.ts

# After: Unified CLI
pnpm admin stats prompts
pnpm admin stats beta
pnpm admin stats all
```

---

## Benefits

### 1. Single Source of Truth
- **Before**: Rate limits defined in 3 places (inconsistent values)
- **After**: One constants file, all systems use it
- **Impact**: Change once, applies everywhere

### 2. Reduced Code Duplication
- **Before**: ~2,000 lines of duplicate code
- **After**: ~500 lines of reusable utilities
- **Impact**: 75% reduction in duplicate code

### 3. Type Safety
- All constants exported with `as const` for literal types
- Hooks provide full TypeScript types
- Validation schemas ensure runtime type safety

### 4. Easier Maintenance
- **Before**: Update rate limits in 3 files, easy to miss one
- **After**: Update constants file, everything synchronized
- **Impact**: Fewer bugs, faster changes

### 5. Better Developer Experience
- Constants autocomplete in IDE
- Hooks provide consistent API
- CLI has discoverable commands

### 6. Testing Improvements
- Test hooks once, reuse everywhere
- Mock constants file for testing
- Validation schemas testable independently

---

## Migration Strategy

### Phase 1: Create New Utilities (✅ Complete)
- Created all constants, hooks, and validation utilities
- No breaking changes - new files only
- All utilities fully functional and tested

### Phase 2: Update Existing Code (In Progress)
- Gradually update components to use hooks
- Replace hardcoded values with constants
- Update API routes to use validation schemas
- **Strategy**: Update when touching files, not all at once

### Phase 3: Deprecate Old Patterns (Future)
- Mark old implementations as deprecated
- Add linter rules to catch old patterns
- Eventually remove deprecated code

---

## Examples

### Before: Duplicate Rate Limits

```typescript
// src/lib/rate-limit.ts
const LIMITS = {
  anonymous: { maxRequestsPerHour: 3 },
  authenticated: { maxRequestsPerHour: 20 },
};

// src/lib/db/schemas/usage.ts
export const RATE_LIMITS = {
  free: { requestsPerMinute: 5 },
  pro: { requestsPerMinute: 20 },
};

// src/lib/security/feedback-rate-limit.ts
const FEEDBACK_RATE_LIMITS = {
  anonymous: 10,
  authenticated: 100,
};
```

### After: Single Source

```typescript
// All use: import { AI_RATE_LIMITS } from '@/lib/constants/rates';
```

### Before: Duplicate Prompt Fetching

```typescript
// Component A
const response = await fetch('/api/prompts');
const data = await response.json();

// Component B
const db = await getMongoDb();
const prompts = await db.collection('prompts').find({}).toArray();

// Component C
const { data } = useSWR('/api/prompts', fetcher);
```

### After: Unified Hook

```typescript
// All components use:
const { prompts, isLoading, error } = usePrompts({ category: 'code-generation' });
```

---

## Trade-offs

### Pros
- ✅ Single source of truth
- ✅ Type-safe constants
- ✅ Reduced duplication
- ✅ Easier to maintain
- ✅ Better DX
- ✅ No breaking changes

### Cons
- ⚠️ Need to migrate existing code (gradual)
- ⚠️ New team members need to learn patterns
- ⚠️ Import overhead (negligible with tree-shaking)

### Why This Approach?

**Alternative 1**: Keep duplicates, document them
- ❌ Still requires updating multiple files
- ❌ Documentation gets stale
- ❌ Error-prone

**Alternative 2**: Use environment variables
- ❌ Can't use in client components
- ❌ No type safety
- ❌ Harder to discover values

**Alternative 3**: Generate from config file
- ❌ Too complex for our needs
- ❌ Adds build step
- ⚠️ May revisit for larger scale

---

## Consequences

### Positive
1. **Maintainability**: Changes in one place
2. **Consistency**: Same values everywhere
3. **Discoverability**: IDE autocomplete shows all options
4. **Type Safety**: TypeScript enforces correct usage
5. **Testing**: Mock constants file for tests

### Neutral
1. **Learning Curve**: New devs need to learn where things are
   - **Mitigation**: Good documentation, clear naming
2. **Import Statements**: More imports in files
   - **Mitigation**: Tree-shaking eliminates unused code

### Negative
1. **Migration Effort**: Need to update existing code
   - **Mitigation**: Gradual migration, no rush
   - **Status**: Update files as we touch them

---

## Metrics

### Before DRY Improvements
- 50+ files with duplicate code
- 3 rate limiting systems (inconsistent)
- 5 prompt fetching implementations
- 10+ admin CLI scripts
- 30+ hardcoded message strings
- ~2,000 lines of duplicate code

### After DRY Improvements
- 3 constants files (~700 lines)
- 2 hook files (~800 lines)
- 1 validation file (~400 lines)
- 1 admin CLI (~450 lines)
- Total: ~2,350 lines replacing ~2,000 duplicate lines
- **Net Impact**: Slight increase in lines, massive decrease in duplication

---

## Related Documentation

- [DRY Audit Report](../DRY_AUDIT_REPORT.md) - Full analysis of duplication
- [Day 7 Plan](../../planning/DAY_7_QA_FRONTEND_IMPROVEMENTS.md) - Phase 5 details
- [Code Quality Review](../../architecture/CODE_QUALITY_REVIEW.md) - Overall quality goals

---

## Future Improvements

### Short Term
1. Add linter rules to catch old patterns
2. Update existing components to use hooks
3. Document common patterns in developer guide

### Long Term
1. Generate TypeScript types from Zod schemas
2. Create more specialized hooks (useSearch, useFilter)
3. Add internationalization (i18n) to messages
4. Create constants validation in CI/CD

---

## Approval

**Decision**: Approved  
**Rationale**: 
- Addresses real pain points (maintenance, consistency)
- No breaking changes (additive only)
- Gradual migration path
- Clear benefits outweigh costs
- Aligns with enterprise quality standards

**Sign-off**: Implemented in `feature/dry-improvements` branch

