---
docid: ADR-073
title: ADR 030 Vue I18n V11 Migration
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

---
docid: ADR-030
title: Vue-i18n v10 to v11 Migration
status: Accepted
date: 2026-01-05
decision-makers: ["@Frontend", "@TechLead"]
consulted: ["@SARAH"]
---

# ADR-030: Vue-i18n v10 to v11 Migration

## Status

**Accepted** - Migration completed successfully

## Context

Vue-i18n v10 is deprecated and no longer maintained. The deprecation warning states:

> v9 and v10 no longer supported. please migrate to v11.

**Current state:**
- Store: `vue-i18n@^10.0.2`
- Admin: `vue-i18n@^10.0.2`
- Management: No vue-i18n (uses basic localization)

**Latest version:** 11.2.8

## Decision Drivers

1. **Security**: Unmaintained packages won't receive security patches
2. **Compatibility**: Future Vue updates may break v10
3. **Features**: v11 has performance improvements and better TypeScript support
4. **Maintenance**: Reduces technical debt

## Considered Options

### Option 1: Migrate to v11 (Recommended)

**Pros:**
- Long-term support
- Better TypeScript integration
- Performance improvements
- Smaller bundle size

**Cons:**
- Breaking API changes require code updates
- Testing effort required

### Option 2: Stay on v10

**Pros:**
- No immediate work required

**Cons:**
- Security risk
- Future compatibility issues
- Technical debt accumulation

## Decision

**Migrate to vue-i18n v11** in a dedicated sprint with proper testing.

## Migration Plan

### Phase 1: Analysis (1 day)
- [ ] Audit current i18n usage in Store and Admin
- [ ] Identify breaking changes from v10 to v11
- [ ] Document affected components

### Phase 2: Migration (2-3 days)
- [ ] Update package.json to v11
- [ ] Update initialization code (main.ts)
- [ ] Update composition API usage patterns
- [ ] Fix any breaking changes in components

### Phase 3: Testing (1-2 days)
- [ ] Unit tests for i18n composables
- [ ] E2E tests for language switching
- [ ] Manual QA for all supported languages

### Breaking Changes to Address

Based on vue-i18n v11 changelog:

1. **Legacy API removal**: Ensure using Composition API
2. **Message format changes**: Review complex interpolations
3. **TypeScript strict mode**: Update type definitions
4. **Plugin registration**: New setup pattern

### Code Changes Expected

```typescript
// Before (v10)
import { createI18n } from 'vue-i18n'
const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages
})

// After (v11) - similar but check options
import { createI18n } from 'vue-i18n'
const i18n = createI18n({
  locale: 'en',
  messages,
  // New options available
  missingWarn: false,
  fallbackWarn: false
})
```

## Consequences

### Positive
- Maintained, secure dependency
- Better TypeScript support
- Performance improvements
- Future Vue compatibility

### Negative
- Development time investment (3-5 days)
- Potential regression risk (mitigated by testing)

### Neutral
- Need to update documentation
- Team needs to learn v11 changes

## Timeline

| Phase | Duration | Sprint |
|-------|----------|--------|
| Analysis | 1 day | Current |
| Migration | 2-3 days | Next |
| Testing | 1-2 days | Next |

**Total effort**: ~5 story points

## Related Documents

- [GL-013] Dependency Management Policy
- [INS-002] Frontend Instructions
- [KB-LESSONS] Lessons Learned

---

**Owner**: @Frontend  
**Review**: @TechLead
