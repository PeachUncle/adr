# ADR 009: Mock Data Removal Strategy

**Date:** 2025-11-02  
**Status:** ✅ Accepted  
**Deciders:** Engineering Team  
**Related:** Day 7 QA Process, PATTERN_AUDIT_DAY7.md, Phase 3 Mock Data Audit

---

## Context

During Day 7 QA audit, user feedback repeatedly emphasized: **"No mock data"** - this was mentioned 10+ times. The codebase contained various forms of mock/fake data that undermined trust and professionalism.

### Problems with Mock Data

1. **User Trust**: Fake metrics (views, ratings, counts) mislead users
2. **Professionalism**: Hardcoded values make product appear unfinished
3. **Analytics**: Can't distinguish real vs. fake engagement
4. **Technical Debt**: Mock data masks missing features
5. **DRY Violations**: Hardcoded values duplicated across files
6. **Enterprise Readiness**: Enterprise customers expect honest, real data

### Examples Found

**Hardcoded Stats:**
```typescript
// ❌ Homepage had multiple hardcoded counts
const totalPrompts = 76;  // Should be from DB
const totalPatterns = 15; // Should be from DB
```

**Fake Engagement Metrics:**
```typescript
// ❌ Prompt cards showed fake views/ratings
<PromptCard views={576} rating={4.9} ratingsCount={5} />
// No real tracking implemented
```

**Mock User Data:**
```typescript
// ❌ LocalStorage fake favorites
localStorage.setItem('favorites', JSON.stringify([...]));
// No persistence, no sync, no analytics
```

---

## Decision

**Adopt systematic mock data removal strategy with zero-tolerance policy**

### Core Principles

1. **Zero Mock Data in Production**
   - All displayed metrics must come from real data sources
   - Hardcoded values are only acceptable in tests or development fixtures
   - Empty states preferred over fake data

2. **Single Source of Truth**
   - All stats come from `/api/stats` endpoint
   - MongoDB queries, not hardcoded numbers
   - Redis caching for performance (not mock data)

3. **Honest Empty States**
   - Show "0" or "No data yet" instead of fake numbers
   - Provide clear CTAs for first-time users
   - Professional messaging when data doesn't exist

4. **Progressive Enhancement**
   - Start with real data at 0, not fake data
   - Build tracking/metrics as features mature
   - Incremental improvement over fake perfection

---

## Implementation Strategy

### Phase 1: Identification & Audit

**Search Patterns:**
```bash
# Find hardcoded numbers in components
grep -r "views:\s*\d\{3,\}" src/components/
grep -r "rating:\s*\d" src/components/
grep -r "total.*=.*\d\{2,\}" src/app/

# Find mock/fake patterns
grep -r "TODO.*fake\|TODO.*mock\|MOCK\|FAKE" src/
grep -r "localStorage.*favorite" src/
grep -r "hardcoded\|hard-coded" src/
```

**Categories:**
- **Stats & Counts**: Hardcoded totals, breakdowns
- **Engagement Metrics**: Fake views, ratings, likes
- **User Data**: Mock favorites, localStorage fallbacks
- **Demo Data**: Placeholder content, dummy arrays

### Phase 2: Systematic Removal

**For Each Instance:**

1. **Identify Data Source**
   - Does real data exist? → Use it
   - Does tracking exist? → Implement it
   - Neither? → Show empty state

2. **Replace Strategy**

   ```typescript
   // ❌ BEFORE: Hardcoded
   const totalPrompts = 76;
   
   // ✅ AFTER: Real data
   const stats = await fetch('/api/stats');
   const totalPrompts = stats.prompts?.total || 0;
   ```

3. **Empty State Pattern**

   ```typescript
   // ✅ Proper empty state
   {totalPrompts === 0 ? (
     <EmptyState
       title="No prompts yet"
       description="Be the first to create a prompt"
       action={<Button>Create Prompt</Button>}
     />
   ) : (
     <StatsDisplay count={totalPrompts} />
   )}
   ```

### Phase 3: Prevention

**Pre-commit Hook Checks:**
```javascript
// scripts/hooks/check-mock-data.js
const mockPatterns = [
  /views:\s*\d{3,}/,
  /rating:\s*[4-5]\.\d/,
  /TODO.*(fake|mock|stub)/i,
  /MOCK_|FAKE_|STUB_/,
];

// Block commits with mock data patterns
```

**Documentation:**
- Update `.cursorrules` with "No mock data" principle
- Add to CONTRIBUTING.md
- Include in code review checklist

---

## Consequences

### ✅ Positive

1. **User Trust**
   - Honest metrics build credibility
   - Users see real value, not inflated numbers
   - Professional appearance

2. **Data Integrity**
   - Analytics reflect actual usage
   - Can track real engagement trends
   - Product decisions based on truth

3. **Technical Quality**
   - Forces proper data architecture
   - Encourages real feature implementation
   - Reduces technical debt

4. **Enterprise Readiness**
   - Enterprise customers expect real data
   - Compliance with data honesty standards
   - Professional polish

### ⚠️ Negative

1. **Initial Appearance**
   - Empty states may look "unfinished"
   - Lower counts than competitors
   - Need strong empty state design

2. **Development Time**
   - Requires real data infrastructure
   - More complex than hardcoding
   - Tracking/metrics take time to build

3. **User Expectations**
   - Users may prefer seeing "activity"
   - Empty states need compelling CTAs
   - Requires UX finesse

### 🔄 Trade-offs

| Aspect | Mock Data | Real Data |
|--------|-----------|-----------|
| Setup Time | ⚡ Instant | 🌐 Requires infrastructure |
| User Trust | ❌ Low | ✅ High |
| Analytics | ❌ Fake | ✅ Real |
| Professionalism | ❌ Appears unfinished | ✅ Enterprise-ready |
| Technical Debt | ⚠️ High | ✅ Low |
| Maintenance | ⚠️ Constant updates | ✅ Self-maintaining |

**Winner:** Real Data (trust and professionalism outweigh initial complexity)

---

## Alternatives Considered

### Alternative 1: Keep Mock Data (Status Quo)

**Pros:**
- Fast to implement
- Looks "finished" initially
- No infrastructure needed

**Cons:**
- Misleads users
- Violates trust
- Masks missing features
- Not enterprise-ready

**Verdict:** ❌ Rejected - User explicitly requested removal

### Alternative 2: Gradual Migration

**Pros:**
- Lower risk
- Incremental improvement
- Can prioritize high-visibility areas

**Cons:**
- Inconsistent experience
- Technical debt remains
- Partial solution

**Verdict:** ⚠️ Acceptable - Use for Phase 3 implementation

### Alternative 3: Mock Data with Disclaimer

**Pros:**
- Transparent about fake data
- Still looks "finished"
- Easy to implement

**Cons:**
- Still misleading
- Doesn't solve trust issue
- Unprofessional appearance

**Verdict:** ❌ Rejected - Doesn't meet user requirements

---

## Implementation Plan

### Phase 3: Mock Data Audit (Day 7)

**Tasks:**
1. ✅ Create comprehensive audit report
2. ✅ Document all mock data instances
3. ✅ Categorize by type (stats, engagement, user data)
4. ✅ Prioritize fixes (Critical → High → Medium → Low)
5. ⏳ Remove critical instances
6. ⏳ Add proper empty states
7. ⏳ Implement real data sources

**Timeline:** 2-3 hours for audit, incremental fixes

### Prevention Strategy

**Pre-commit Hook:**
```javascript
// Block commits with mock data patterns
const violations = checkMockDataPatterns(changedFiles);
if (violations.length > 0) {
  console.error('❌ Mock data detected in production code');
  console.error(violations);
  process.exit(1);
}
```

**Code Review Checklist:**
- [ ] No hardcoded stats or counts
- [ ] No fake engagement metrics
- [ ] Empty states instead of mock data
- [ ] All data comes from real sources

---

## Examples

### Example 1: Stats Panel

**Before:**
```typescript
// ❌ Hardcoded counts
const stats = {
  totalPrompts: 76,
  totalPatterns: 15,
  categories: 8,
};
```

**After:**
```typescript
// ✅ Real data from API
const stats = await fetch('/api/stats').then(r => r.json());
// Returns: { prompts: { total: 132, byRole: {...}, byCategory: {...} } }
```

### Example 2: Engagement Metrics

**Before:**
```typescript
// ❌ Fake views/ratings
<PromptCard views={576} rating={4.9} />
```

**After:**
```typescript
// ✅ Real tracking (or empty state)
{views > 0 ? (
  <div>Views: {views}</div>
) : (
  <div className="text-muted-foreground">No views yet</div>
)}
```

### Example 3: Favorites System

**Before:**
```typescript
// ❌ localStorage fake data
const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
```

**After:**
```typescript
// ✅ MongoDB persistence
const { data: favorites } = await fetch('/api/favorites');
// Returns real user favorites from database
```

---

## Success Criteria

**Phase 3 Completion:**
- ✅ Audit report created
- ✅ All critical mock data removed
- ✅ Empty states implemented
- ✅ Pre-commit hooks active
- ✅ Documentation updated

**Long-term:**
- Zero mock data in production code
- All metrics show real data or proper empty states
- User trust increased
- Analytics reflect actual usage

---

## Metrics

### Before Removal

- **Mock Data Instances:** ~15-20 across codebase
- **Hardcoded Stats:** Homepage, dashboard, multiple pages
- **Fake Metrics:** Views, ratings, favorites
- **User Trust:** Low (user repeatedly complained)

### After Removal

- **Mock Data Instances:** 0 (target)
- **Real Data Sources:** `/api/stats`, MongoDB queries
- **Empty States:** Professional, actionable
- **User Trust:** High (meets user requirements)

---

## References

- [Day 7 Plan](../planning/DAY_7_QA_FRONTEND_IMPROVEMENTS.md)
- [Pattern Audit Report](../../testing/PATTERN_AUDIT_DAY7.md)
- [Mock Data Audit Report](../../testing/MOCK_DATA_AUDIT_DAY7.md) (to be created)
- [Stats API](../../../src/app/api/stats/route.ts)
- [Enterprise Compliance](../../architecture/CODE_QUALITY_REVIEW.md)

---

## Related ADRs

- ADR 009: Pattern-Based Bug Fixing (similar audit approach)
- ADR 008: Favorites System (MongoDB persistence replaces localStorage)
- ADR 010: DRY Improvements (single source of truth for stats)

---

## Notes

**Future Enhancements:**
1. Real view tracking implementation
2. Real rating system (if needed)
3. Engagement analytics dashboard
4. Popularity metrics for content curation

**Key Principle:**
> "Start with real data at 0, not fake data at 1000"

---

**Last Updated:** 2025-11-02  
**Review Date:** 2025-12-02 (1 month)  
**Status:** ✅ Accepted - Implementation in progress  
**Tags:** #quality #user-trust #technical-debt #day7 #mock-data

