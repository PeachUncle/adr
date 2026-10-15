# 3. Iframe vs Module Federation for Micro-Frontends

**Date:** 2025-10-01  
**Status:** Accepted  
**Deciders:** Frontend Team, UX Team

---

## Context

We need to integrate multiple micro-frontends (pet-licensing, pet-insurance, etc.) into our main dashboard. Each micro-frontend should be independently deployable and maintainable.

### Requirements

- Independent deployment of micro-frontends
- Consistent user experience
- Type safety where possible
- Minimal coupling between apps
- Support for different update cycles

### Use Case

Main dashboard (`apps/web`) needs to display pet-licensing app (`apps/pet-licensing`) as a tab. The licensing app should also be accessible standalone at `pet-licensing.harnesshero.com`.

---

## Decision

We will use **iframe integration** for micro-frontends, with Module Federation as a future option.

**Current Implementation:**
```typescript
// apps/web/src/app/(dashboard)/licensing/page.tsx
<iframe
  src="http://localhost:3001/dashboard"
  className="w-full h-[800px]"
  title="Pet Licensing Dashboard"
  sandbox="allow-same-origin allow-scripts allow-forms"
/>
```

**Communication:**
- Use `postMessage` API for parent ↔ child communication
- Pass auth tokens via secure messages
- Handle loading/error states in parent

---

## Consequences

### Positive

- ✅ **Complete isolation** - No CSS/JS conflicts
- ✅ **Independent deployment** - Update micro-frontend without touching dashboard
- ✅ **Technology flexibility** - Could use different framework if needed
- ✅ **Simple implementation** - Just an iframe tag
- ✅ **Security** - Sandboxed execution
- ✅ **Rollback easy** - Just change src URL
- ✅ **Standalone capability** - Same app works independently

### Negative

- ⚠️ **Less seamless UX** - Iframe boundaries visible
- ⚠️ **Communication overhead** - postMessage is more complex
- ⚠️ **Duplicate bundles** - React loaded multiple times
- ⚠️ **SEO challenges** - Content in iframe not indexed
- ⚠️ **Styling coordination** - Need consistent design system
- ⚠️ **Authentication complexity** - Separate contexts

### Neutral

- Loading time similar to Module Federation
- Performance adequate for our use case
- Can migrate to Module Federation later if needed

---

## Implementation Details

### Communication Pattern

```typescript
// Parent (dashboard) sends message
window.postMessage({
  type: 'UPDATE_USER',
  payload: { userId: 'user_123' },
}, 'http://localhost:3001');

// Child (micro-frontend) receives
window.addEventListener('message', (event) => {
  if (event.origin !== 'http://localhost:3000') return;
  
  if (event.data.type === 'UPDATE_USER') {
    setUser(event.data.payload);
  }
});
```

### Authentication

```typescript
// Backend session validation (simplest approach)
// Both dashboard and micro-frontend validate with backend
const session = await fetch('/api/session', {
  credentials: 'include', // Send cookies
});
```

---

## Alternatives Considered

### Alternative 1: Webpack Module Federation

**How it works:**
```typescript
// apps/web/next.config.ts
experimental: {
  moduleFederation: {
    remotes: {
      licensing: 'licensing@http://localhost:3001/remoteEntry.js',
    },
  },
}

// Use in dashboard
import { LicensingDashboard } from 'licensing/Dashboard';
```

**Pros:**
- Seamless UX (no iframe boundaries)
- Shared dependencies (smaller bundle)
- Direct component import
- Better performance (shared React)

**Cons:**
- More complex setup
- Build-time coupling
- Version coordination needed
- Harder to debug
- Less isolation

**Why not chosen now:** Added complexity not justified yet. May reconsider when we have >5 micro-frontends.

---

### Alternative 2: Monorepo Shared Routes

**How it works:**
```
apps/web/src/app/
├── (dashboard)/
│   ├── licensing/    # Import from licensing package
│   ├── insurance/    # Import from insurance package
```

**Pros:**
- Very simple
- Type-safe
- Same bundle

**Cons:**
- Not truly independent
- Can't deploy separately
- Defeats purpose of micro-frontends

**Why not chosen:** Not really micro-frontends, just code organization.

---

### Alternative 3: Web Components

**How it works:**
```html
<pet-licensing-dashboard></pet-licensing-dashboard>
```

**Pros:**
- Framework agnostic
- Standard web API
- Good encapsulation

**Cons:**
- React doesn't integrate well
- Immature tooling
- Props/events awkward

**Why not chosen:** Poor React integration, immature ecosystem.

---

## Migration Path to Module Federation

**When to migrate:**
- Have >5 micro-frontends
- Performance becomes issue
- UX feedback demands seamlessness
- Team has bandwidth for complexity

**How to migrate:**
1. Add Module Federation config
2. Keep iframe as fallback
3. A/B test both approaches
4. Gradually migrate based on results

**Estimated effort:** 1-2 weeks for initial setup + 2-3 days per app

---

## Related Decisions

- [ADR-002: Hybrid Microservices](./002-hybrid-microservices-approach.md)
- Future: Design system sharing strategy
- Future: Authentication across micro-frontends

---

## Success Criteria

**This decision succeeds if:**

1. ✅ Micro-frontends deploy independently
2. ✅ User experience is acceptable
3. ✅ Development velocity is high
4. ✅ Authentication works reliably
5. ⏳ No major UX complaints about iframe

**Review:** After launching 3rd micro-frontend

---

## References

- [Micro-Frontends](https://micro-frontends.org/)
- [Module Federation Docs](https://webpack.js.org/concepts/module-federation/)
- [postMessage API](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- Team Discussion: October 1, 2025
- POC: pet-licensing iframe integration

---

## Appendix: Comparison Matrix

| Feature | Iframe | Module Federation | Monorepo Routes |
|---------|--------|-------------------|-----------------|
| **Independence** | ✅ High | 🟡 Medium | ❌ Low |
| **UX Seamlessness** | 🟡 Medium | ✅ High | ✅ High |
| **Complexity** | ✅ Low | ⚠️ High | ✅ Low |
| **Type Safety** | ❌ None | ✅ Full | ✅ Full |
| **Bundle Size** | ⚠️ Duplicated | ✅ Shared | ✅ Single |
| **Deployment** | ✅ Independent | 🟡 Semi-independent | ❌ Coupled |
| **Tech Flexibility** | ✅ Any framework | 🟡 Same build tool | ❌ Same everything |
| **SEO** | ❌ Poor | ✅ Good | ✅ Good |
| **Authentication** | 🟡 Complex | ✅ Shared context | ✅ Shared context |
| **CSS Isolation** | ✅ Complete | 🟡 Manual | 🟡 Manual |
| **Our Choice** | ✅ **Current** | 🔮 Future | ❌ Not micro-frontend |

---

**Last Updated:** 2025-10-01  
**Next Review:** After 3rd micro-frontend launch (Q1 2026)

