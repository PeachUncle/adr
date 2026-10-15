---
docid: ADR-083
title: ADR 040 Tenant Customizable Language Resources
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿---
docid: ADR-039
title: Tenant-Customizable Language Resources
status: Proposed
owner: @Architect
created: 2026-01-05
---

# ADR-039: Tenant-Customizable Language Resources

## Context

B2X is a multi-tenant application supporting 8 languages (en, de, fr, es, it, pt, nl, pl). Currently, all tenants share the same global translations stored as static JSON files in the frontend. This limits tenant-specific customization needs for:

- Brand-specific terminology
- Industry-specific language
- Regional variations
- Legal/compliance text requirements

**Critical Update (2026-01-05):** SEO for the store frontend has been identified as critical business priority. This necessitates server-side rendering (SSR) to ensure proper search engine indexing of multi-tenant, multi-language content.

## Decision

Implement tenant-customizable language resources using a hybrid database-driven approach with static file fallbacks, incorporating SSR for SEO-critical store frontend.

### Architecture Overview

1. **Storage Strategy**: Store tenant-specific translation overrides in PostgreSQL
2. **Fallback Logic**: Use global static files as defaults for unchanged keys
3. **API Design**: Dynamic loading with tenant context (client-side) + server-side preloading (SSR)
4. **Frontend Integration**: Vue i18n with dual loading strategy (SSR + client hydration)
5. **SSR Implementation**: Nuxt.js migration for store frontend with tenant-aware rendering

### Updated Database Schema

```sql
CREATE TABLE tenant_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    language_code VARCHAR(5) NOT NULL,
    key_path VARCHAR(500) NOT NULL,
    translation TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, language_code, key_path, is_active)
);

-- Index for performance
CREATE INDEX idx_tenant_translations_lookup 
ON tenant_translations(tenant_id, language_code, key_path) 
WHERE is_active = true;

-- Additional index for SSR performance
CREATE INDEX idx_tenant_translations_ssr 
ON tenant_translations(tenant_id, language_code) 
WHERE is_active = true;
```

### API Endpoints

```
GET /api/v1/localization/{tenantId}/{languageCode}
- Returns merged translations (global + tenant overrides)
- Cached with Redis (TTL: 1 hour for client, 24 hours for SSR)
- Supports ETags for conditional requests
- SSR mode: Optimized for server-side bulk loading

POST /api/v1/localization/{tenantId}/{languageCode}
- Bulk upsert tenant translations
- Requires tenant admin permissions

DELETE /api/v1/localization/{tenantId}/{languageCode}/{keyPath}
- Reset specific key to global default

GET /api/v1/localization/ssr/{tenantId}/{languageCode}
- SSR-optimized endpoint with minimal payload
- Preloads all tenant translations for server rendering
- Higher cache priority for performance
```

### Frontend Implementation

**Dual Loading Strategy:**

```typescript
// SSR-compatible i18n configuration
const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages: process.server ? 
    await loadServerTranslations() : {}, // SSR preload
  loadLanguages: async (lang: string) => {
    if (process.server) {
      // Server-side: direct database access
      return await loadServerTranslations(lang);
    } else {
      // Client-side: API call
      const tenantId = getCurrentTenantId();
      const response = await fetch(`/api/v1/localization/${tenantId}/${lang}`);
      return response.json();
    }
  }
});

// Nuxt.js SSR context
export default defineNuxtConfig({
  i18n: {
    locales: ['en', 'de', 'fr', 'es', 'it', 'pt', 'nl', 'pl'],
    strategy: 'prefix',
    detectBrowserLanguage: false, // Tenant-specific
    customRoutes: 'config' // Tenant-aware routing
  }
});
```

## Consequences

### Positive
- Full tenant customization capability
- Minimal storage overhead (only overrides stored)
- **SEO optimization** through SSR for store frontend
- Better Core Web Vitals (LCP, CLS) for customer-facing pages
- Instant translation availability (no loading delay)
- Maintains performance with intelligent caching
- Easy to reset to defaults
- Audit trail for changes

### Negative
- **Increased complexity** with SSR migration
- Higher server load and infrastructure requirements
- **Development workflow changes** (build, deployment, debugging)
- More complex caching strategy (server + CDN + client)
- Tenant context management during SSR
- Potential for hydration mismatches

### Risks
- Performance impact on high-traffic tenants
- Data consistency between global and tenant translations
- **SSR migration complexity** and potential regressions
- Cache invalidation challenges with multi-tenant content

## Alternatives Considered

### 1. Tenant-Specific Locale Files
- **Rejected**: File management complexity, harder auditing, potential for malformed uploads

### 2. Full Database Storage
- **Rejected**: Higher storage costs, slower loading, unnecessary for unchanged content

### 3. Client-Side Merging Only
- **Rejected**: Increases bundle size, exposes global translations to client

### 4. Server-Side Rendering (SSR) Integration
**Adopted**: Nuxt.js SSR with server-side translation injection for SEO-critical store frontend

**Benefits for SEO:**
- Search engines can crawl multi-language, tenant-specific content immediately
- Improved Core Web Vitals affect search rankings
- Better social media sharing and link previews
- Enhanced accessibility and performance

**Implementation Approach:**
- Hybrid SSR: Store frontend gets SSR, Admin remains SPA
- Tenant-aware server rendering with translation preloading
- Intelligent caching with CDN integration
- Graceful fallback to client-side loading if SSR fails

## Implementation Plan

### Phase 1: Database & API Infrastructure (Week 1-2)
- Database schema migration with SSR-optimized indexes
- Backend API endpoints (client + SSR variants)
- Redis caching strategy implementation
- Basic tenant isolation validation

### Phase 2: SSR Migration Preparation (Week 3-4)
- Nuxt.js setup for store frontend
- Tenant context resolution in SSR
- Server-side translation loading
- Hybrid client/server loading strategy

### Phase 3: Frontend Integration (Week 5-6)
- Vue i18n SSR-compatible configuration
- Client-side hydration handling
- Error boundaries for translation failures
- Testing across all supported languages

### Phase 4: Admin Interface & Advanced Features (Week 7-8)
- Translation management UI for tenants
- Bulk import/export functionality
- Translation completeness validation
- Audit logging and version control

### Phase 5: Performance Optimization (Week 9-10)
- CDN integration for global translations
- Cache optimization and monitoring
- Load testing with multi-tenant scenarios
- SEO validation and Core Web Vitals optimization

## Success Metrics
- <100ms average response time for translation loading
- <5% increase in localization API error rate
- 95% translation completeness across tenants
- Zero cross-tenant data leakage incidents
- **SEO Improvement**: 20% increase in organic search traffic
- **Core Web Vitals**: LCP <2.5s, CLS <0.1, FID <100ms
- **SSR Performance**: <500ms server response time
- **Cache Hit Rate**: >90% for translation requests

## Related Documents
- [GL-009] AI Behavior Guidelines
- [KB-005] .NET Localization
- [KB-007] Vue.js 3
- ADR-030: Vue-i18n v10 to v11 Migration

## Open Questions
- How to handle translation versioning for rollbacks?
- Should we implement machine translation for new keys?
- What's the strategy for handling RTL languages if added later?