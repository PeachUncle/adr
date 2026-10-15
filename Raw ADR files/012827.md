# ADR-005: Frontend Framework

## Status

Accepted

## Context

We need a frontend framework for the Ohana Booking admin application. This is an internal tool for:

- Admins (full access)
- Coordinators (booking management, no financial access)
- Performers (Phase 1.5: view schedule, mark availability)

Key requirements:

- Fast development iteration
- Good developer experience
- Modern tooling
- Type safety with TypeScript
- No SEO requirements (internal admin tool)

## Decision Drivers

- **SEO not needed**: Admin dashboard doesn't need server-side rendering
- **Development speed**: Solo developer needs fast iteration
- **Developer familiarity**: Strong Vue experience
- **Tooling quality**: Modern build tools and DX
- **Type safety**: Full TypeScript support
- **Ecosystem**: Rich component libraries and state management

## Options Considered

### Option A: Vite + Vue 3 SPA

**Pros:**

- ✅ **Fastest DX** - Vite HMR is instant
- ✅ **Simple architecture** - no SSR complexity
- ✅ **Vue Composition API** - clean, modern patterns
- ✅ **Full TypeScript support** - excellent type inference
- ✅ **Smaller bundle** - Vue is lightweight
- ✅ **No over-engineering** - SPA is perfect for admin tools
- ✅ **Great ecosystem** - PrimeVue, Pinia Colada, VueUse

**Cons:**

- ⚠️ **No SSR** - but not needed for admin dashboard
- ⚠️ **Manual routing setup** - need to configure vue-router

### Option B: Nuxt 3

**Pros:**

- ✅ **File-based routing** - auto-imports, zero-config
- ✅ **SSR/SSG ready** - if ever needed later
- ✅ **More batteries-included** - less setup

**Cons:**

- ❌ **Overkill for admin tool** - SSR not needed
- ❌ **More complexity** - server/client split
- ❌ **Slightly slower DX** - full-stack framework overhead
- ❌ **Larger bundle** - includes server code

### Option C: Next.js (React)

**Pros:**

- ✅ **Large ecosystem** - many admin templates
- ✅ **Resume value** - React dominance

**Cons:**

- ❌ **Less familiar** - developer stronger in Vue
- ❌ **Heavier** - React + Next is larger than Vue
- ❌ **More complex** - React hooks, useEffect, memo
- ❌ **App Router churn** - still stabilizing

## Decision

**We will use Vite + Vue 3 SPA.**

### Stack Details

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "@pinia/colada": "^0.x", // State management
    "primevue": "^3.x", // UI components
    "axios": "^1.6.0" // HTTP client
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0"
  }
}
```

### Project Structure

```
apps/frontend/
├── src/
│   ├── components/        # Vue components
│   ├── views/             # Page components
│   ├── router/            # Vue Router config
│   ├── stores/            # Pinia Colada queries/state
│   ├── api/               # API client
│   ├── types/             # Local types (imports from @ohana/types)
│   └── App.vue
├── index.html
├── vite.config.ts
└── tsconfig.json
```

### Rationale

1. **Perfect fit**: SPA architecture is ideal for admin dashboards
2. **Developer velocity**: Vite's DX is unmatched for iteration speed
3. **No complexity debt**: Avoid SSR when it's not needed
4. **Strong Vue knowledge**: Leverage existing expertise
5. **Modern patterns**: Composition API + TypeScript is clean
6. **Lightweight**: Faster load times, smaller bundle

## Consequences

### Positive

- Lightning-fast development with Vite HMR
- Simple mental model (no server/client split)
- Full TypeScript safety across frontend
- Easy to integrate with NestJS backend
- Smaller production bundle than SSR alternatives
- PrimeVue provides all needed UI components
- Can migrate to Nuxt later if SSR ever needed (same Vue 3 code)

### Negative

- Manual router setup (but straightforward)
- No file-based routing (acceptable tradeoff)
- If public site is added to this repo later, would need different approach

### Risks

- **Future SSR needs**: What if we need SSR for public pages?
  - _Mitigation_: Public marketing site is separate repo; can use Nuxt/Astro there
- **Routing complexity**: Manual routing could get messy
  - _Mitigation_: Keep routing simple; use route guards for auth

## Follow-up Actions

- [ ] Initialize Vite + Vue 3 project with TypeScript
- [ ] Configure Vue Router with auth guards
- [ ] Set up Pinia Colada for state management (see ADR-007)
- [ ] Install and configure PrimeVue (see ADR-009)
- [ ] Create API client with axios + types from monorepo
- [ ] Set up Tailwind CSS
- [ ] Configure ESLint + Prettier
- [ ] Create base layout components
