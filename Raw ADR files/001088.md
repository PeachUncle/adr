# ADR-0001: Dual Frontend Architecture

**Date:** 2025-11-27  
**Status:** Active  
**Deciders:** Core Team

---

## Context

The Chef's Mind AI project currently maintains two separate frontend applications:

1. **Vite Client** (`client/`) — React + Vite + TypeScript
2. **Next.js Enhanced** (`frontend-enhanced/`) — Next.js 14+ App Router

### Historical Background

- **Vite Client** was the original rapid prototyping frontend for quick iteration on chat UI, agent selection, and real-time features.
- **Next.js Enhanced** was introduced later to support:
  - Server-side rendering (SSR) for better SEO and performance
  - App Router for advanced routing patterns
  - More complex UI requirements (multi-agent dashboards, sidebar intelligence, advanced visualizations)

### Goals

- **Vite Client:** Fast developer experience (DX), instant HMR, lightweight bundle, suitable for testing and demos
- **Next.js Enhanced:** Production-ready UI with SSR, better UX for complex features, scalability for future enterprise requirements

---

## Decision

**We will maintain both frontends in parallel with clearly defined roles:**

### Vite Client (`client/`)

- **Role:** Development sandbox, rapid prototyping, agent testing
- **Use cases:** Quick feature testing, local agent demos, simple chat interface
- **Stack:** React 18 + Vite 5 + TanStack Query + shadcn/ui

### Next.js Enhanced (`frontend-enhanced/`)

- **Role:** Production frontend for end users
- **Use cases:** Multi-agent orchestration UI, media studio, advanced analytics, Google OAuth integration
- **Stack:** Next.js 14 + App Router + Server Components + shadcn/ui

### Guidelines

- Shared UI components should use shadcn/ui for consistency
- API contracts defined in `shared/` should work with both frontends
- Authentication flows may differ (JWT for Vite, session-based for Next.js)

---

## Consequences

### Advantages

✅ **Developer Flexibility:** Developers can use Vite for rapid prototyping without Next.js overhead  
✅ **Best Tool for the Job:** Vite excels at speed; Next.js excels at production features  
✅ **Risk Mitigation:** If one frontend has issues, the other can serve as fallback/reference  
✅ **Different Audiences:** Vite for internal testing, Next.js for customers  

### Disadvantages

⚠️ **Code Duplication:** UI components, hooks, and utilities may be duplicated  
⚠️ **Maintenance Overhead:** Two codebases to maintain, update dependencies, fix bugs  
⚠️ **Validation Cost:** Features must be tested in both environments  
⚠️ **Onboarding Confusion:** New developers need to understand why two frontends exist  

### Risks

🔴 **Divergence Risk:** Frontends may drift apart in features/UX over time  
🔴 **Resource Split:** Team capacity divided between two frontends  
🟡 **Migration Debt:** Eventually may need to consolidate or deprecate one frontend  

---

## Alternatives Considered

### Alternative 1: Single Vite Frontend

- ❌ No SSR/SEO support
- ❌ Difficult to implement complex routing patterns
- ✅ Simpler maintenance

### Alternative 2: Single Next.js Frontend

- ✅ Best production experience
- ❌ Slower dev experience compared to Vite
- ❌ Higher complexity for simple features

### Alternative 3: Monorepo with Shared Components

- ✅ DRY principle enforced
- ⚠️ Requires tooling setup (Nx, Turborepo)
- 🔄 Considered for future refactoring

---

## Status

**Active** — Both frontends are maintained and in use.

### Next Review

- **When:** After reaching v3.0 milestone
- **Trigger:** If maintenance overhead becomes unsustainable
- **Action:** Evaluate consolidation or shared component library
