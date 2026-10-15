# Frontend UI Framework Selection

* Status: proposed
* Deciders: Platform Team, Frontend Team
* Date: 2025-12-05

## Context and Problem Statement

With the Nx polyglot monorepo strategy accepted (ADR-006), we must now select the UI framework and associated tooling for frontend applications. The first applications are a customer-facing e-commerce system and an employee POS system, with future plans for admin dashboards, merchandising tools, and order management interfaces.

This decision will establish the foundation for all frontend development, affecting developer experience, performance, hiring, and long-term maintainability.

## Constraints

- **Client-only runtime in production**: Frontends must ship as static assets (SPA/MPA) with no dedicated Node.js server/BFF in production. Backend responsibilities stay in Spring services.
- **Strict separation**: Clear boundary between frontend (static bundle + browser APIs) and backend (Spring services); avoid full-stack coupling that requires server runtimes for pages/routes.

## Guiding Principles

These principles inform the evaluation criteria and final decision, listed in priority order:

1. **LLM/AI Tooling Support** - Frameworks with strong representation in LLM training data enable better AI-assisted development (code generation, debugging, refactoring). Prioritize widely-used frameworks with extensive documentation and examples.
2. **Type Safety** - Full TypeScript support with strict typing across components, state, and API boundaries
3. **Developer Productivity** - Minimize boilerplate, maximize iteration speed, enable hot module replacement
4. **Performance** - Fast initial load, efficient updates, optimized bundle sizes for e-commerce conversion
5. **Ecosystem Maturity** - Stable libraries, active maintenance, comprehensive documentation
6. **Team Scalability** - Easy onboarding, clear patterns, ability to hire experienced developers
7. **Nx Integration** - First-class support in Nx with generators, executors, and affected analysis
8. **Backend Alignment** - Complement reactive Spring Boot services with efficient data fetching patterns
9. **Progressive Enhancement** - Support for SSR/SSG where SEO matters (e-commerce), SPA where it doesn't (POS)
10. **Code Sharing** - Maximize reuse across e-commerce, POS, admin, and future mobile (React Native)
11. **Long-term Viability** - Framework with strong backing, community, and evolutionary path

**Note:** Current team experience (Angular) is valued but ranked below LLM support and ecosystem factors. The team can learn a new framework; AI tooling effectiveness is harder to change.

## Decision Drivers

1. **LLM training data prevalence** - Framework representation in AI models for code assistance
2. **E-commerce requirements** - SEO, performance, accessibility, conversion optimization
3. **POS requirements** - Offline capability, fast interactions, hardware integration (barcode, receipt)
4. **Nx ecosystem** - Quality of Nx plugins and generators for the framework
5. **State management** - Server state (API data) vs client state patterns
6. **Testing story** - Unit, integration, and E2E testing support
7. **Team experience** - Current team has Angular experience (valued but not decisive)

## Considered Options

### Framework Level

1. **React** - Component library with ecosystem flexibility
2. **Angular** - Full-featured opinionated framework

### React Ecosystem Options (if React chosen)

3. **React + Vite (Vanilla SPA)** - Minimal setup, client-side only
4. **React + Vite + React Router** - SPA with the most mature React router
5. **React + Vite + TanStack Router (+ Query)** - Modern SPA with type-safe routing + server-state
6. **Next.js** - Full-stack React framework with SSR/SSG
7. **Remix** - Full-stack with nested routing and progressive enhancement

## Decision Outcome

Chosen option: **React + Vite + TanStack Router + TanStack Query (SPA, client-only)**

Rationale:
- Strong type safety and routing ergonomics without requiring a server runtime.
- TanStack Query covers server-state concerns; avoids heavy client stores.
- Vite delivers fast DX and small bundles; deploys as static assets with no Node server.
- Aligns with strict frontend/backend separation while remaining flexible for multiple apps (e-commerce, POS, admin).

## Pros and Cons of the Options

### 1. React

Component library approach - "just the view layer" with ecosystem choice.

**Good**
- **Best LLM/AI support** - Largest training corpus, highest quality AI code generation and assistance
- Largest ecosystem and community
- Maximum flexibility in architecture choices
- Extensive Nx support (@nx/react, @nx/next)
- React Native path for mobile apps
- Hooks-based API is intuitive and composable
- Strong TypeScript support
- TanStack ecosystem (Query, Router, Table) is excellent
- Massive hiring pool

**Bad**
- Decision fatigue - must choose routing, state, styling, etc.
- No official "blessed" patterns - team must establish conventions
- Breaking changes between major versions (though improving)
- JSX is polarizing for some developers
- Team must learn React (current experience is Angular)

**Nx Support**
- `@nx/react` - Vite-based React apps and libs
- `@nx/next` - Next.js apps with full SSR support
- Generators for components, hooks, libs
- Module federation support for micro-frontends

### 2. Angular

Full-featured framework with batteries included.

**Good**
- **Team has existing Angular experience** - reduces initial learning curve
- Opinionated - routing, HTTP, forms, DI built-in
- Strong TypeScript integration (written in TS)
- Enterprise adoption and long-term Google backing
- Consistent patterns across projects
- RxJS aligns with reactive Spring Boot backend
- Excellent Nx support (Nx was originally Angular-focused)
- Signals API modernizing reactivity

**Bad**
- **Smaller LLM training corpus** - Less prevalent in AI training data than React, resulting in lower quality AI code assistance
- Steeper learning curve for new hires (modules, decorators, DI, RxJS)
- Larger bundle sizes historically (improving with Ivy/standalone)
- Smaller component ecosystem than React
- No direct path to mobile (Ionic or NativeScript, not as seamless as React Native)
- Hiring pool smaller than React
- More verbose than React for simple components

**Nx Support**
- `@nx/angular` - First-class support, generators, schematics
- Module federation for micro-frontends
- Strong affected analysis

### 3. React + Vite (Vanilla SPA)

Minimal React setup with Vite bundler, client-side only.

**Good**
- Fastest dev server startup and HMR
- Simplest mental model - just React
- Full control over architecture
- Smallest initial learning curve
- Easy to add libraries incrementally

**Bad**
- No SSR/SSG - poor for e-commerce SEO
- Must manually configure everything (routing, data fetching)
- No conventions - team must establish all patterns
- Risk of inconsistent patterns across apps

**Best For**: Internal tools, admin dashboards, POS

### 4. React + Vite + React Router (+ TanStack Query)

SPA using React Router for navigation and TanStack Query for server state.

**Good**
- Most battle-tested React router; large ecosystem and docs
- Declarative nested routing and data APIs (loaders/actions) available but optional
- Works entirely client-side; no Node runtime required
- TanStack Query handles caching/deduping for server data
- Minimal lock-in; easy to host as static assets

**Bad**
- No SSR/SSG out of the box
- Must assemble styling/build/testing conventions
- Loader/action patterns are less type-safe than TanStack Router
- Query + Router are separate concerns to wire together

**Best For**: SPAs where SEO is less critical (POS, dashboards) but stability and community size matter

### 5. React + Vite + TanStack Router (+ TanStack Query)

Modern React SPA stack focused on server state management.

**Good**
- TanStack Query handles caching, deduplication, background refresh
- Eliminates most client-side state management needs
- Type-safe routing with TanStack Router
- Excellent DevTools for debugging
- Works with any backend (REST, GraphQL)
- Smaller bundle than Next.js
- Vite provides fast DX

**Bad**
- No SSR without additional setup
- Newer ecosystem - less battle-tested than Next.js
- Must wire together multiple libraries
- TanStack Router is newer than React Router

**Best For**: Data-heavy SPAs, dashboards, POS

### 6. Next.js (App Router)

Full-stack React framework with SSR, SSG, and API routes.

**Good**
- SSR/SSG for SEO-critical e-commerce pages
- Incremental Static Regeneration (ISR) for dynamic content
- File-based routing with layouts
- Server Components reduce client bundle
- API routes for BFF pattern
- Image optimization built-in
- Strong Vercel backing and community
- Excellent Nx support (@nx/next)

**Bad**
- Vendor influence (Vercel-optimized patterns)
- App Router complexity (Server vs Client Components)
- Larger runtime than pure SPA
- Learning curve for RSC mental model
- Over-engineered for simple SPAs (POS)

**Best For**: E-commerce, marketing pages, SEO-required content

### 7. Remix

Full-stack React framework with nested routing and progressive enhancement.

**Good**
- Nested routing with parallel data loading
- Progressive enhancement - works without JS
- Form-based mutations (web standards)
- No client-side state for most cases
- Excellent error boundaries
- Works well with edge deployment

**Bad**
- Smaller community than Next.js
- Shopify acquisition creates uncertainty
- Less Nx ecosystem support than Next.js
- Mental model shift from SPA patterns
- Fewer examples and tutorials

**Best For**: Form-heavy apps, progressive enhancement needs

## React Router vs TanStack Router (SPA)

- **Maturity/community**: React Router is older with more docs/examples; TanStack Router is newer but rapidly iterating.
- **Type safety**: TanStack Router provides stronger end-to-end typing (params/search/loaders) and first-class search params; React Router relies more on manual typing.
- **Data APIs**: Both offer loaders/actions; TanStack Router emphasizes co-located route loaders with type inference. Neither requires a server runtime.
- **Hosting model**: Both work as client-only SPAs with static asset hosting (no Node server needed). SSR is optional and not required for deployment.
- **Ecosystem**: React Router has broader third-party integration; TanStack Router pairs tightly with TanStack Query for server-state patterns.

## Evaluation Matrix

| Criterion | Angular | React+Vite (vanilla) | React+Vite+React Router | React+Vite+TanStack Router | Next.js | Remix |
|-----------|---------|-----------------------|--------------------------|----------------------------|---------|-------|
| **LLM/AI Support** | Fair | Excellent | Excellent | Excellent | Excellent | Good |
| **SEO/SSR** *(not a deciding factor)* | SSR possible | No | No | No | Excellent | Excellent |
| **Dev Speed** | Medium | Fast | Fast | Fast | Medium | Medium |
| **Bundle Size** | Large | Small | Small | Small | Medium | Medium |
| **Learning Curve** | Low (team exp) | Medium | Medium | Medium | Medium | Medium |
| **Nx Support** | Excellent | Good | Good | Good | Excellent | Fair |
| **Mobile Path** | Ionic | React Native | React Native | React Native | React Native | React Native |
| **Type Safety** | Excellent | Good | Good | Excellent | Good | Good |
| **Hiring Pool** | Medium | Large | Large | Large | Large | Small |
| **E-commerce Fit** | Good | Poor | Fair | Fair | Excellent | Good |
| **POS Fit** | Good | Good | Excellent | Excellent | Overkill | Good |

## Recommended Approach

*(To be filled after team discussion)*

Consider a **hybrid strategy** based on application needs:

| Application | Recommended Stack | Rationale |
|-------------|-------------------|-----------|
| E-commerce Web | Next.js (App Router) | SSR/SSG for SEO, image optimization |
| POS Web | React + TanStack Query + Vite | SPA, offline-first, fast interactions |
| Admin Dashboard | React + TanStack Query + Vite | Internal, no SEO needs |
| Merchandising | React + TanStack Query + Vite | Data-heavy, forms |
| Mobile Apps | React Native + TanStack Query | Code sharing with web |

**Shared across all:**
- TanStack Query for server state
- Shared UI component library (`libs/shared-ui`)
- Generated API types from OpenAPI
- Common validation schemas (Zod)

## Open Questions

- **Offline requirements** - How critical is offline-first for POS? (PWA vs native wrapper)
- **Server Components adoption** - If Next.js chosen, how aggressively to adopt React Server Components?

## Deferred to Separate ADR

The following decisions will be documented in ADR-008 after this framework decision is accepted:

- **Component library** - Build custom vs adopt (Radix, shadcn/ui, MUI, Chakra)
- **Styling approach** - Tailwind CSS, CSS Modules, styled-components, or CSS-in-JS
- **Design system** - Design tokens, theming architecture, accessibility standards

## References

- ADR-006: Frontend Monorepo Strategy (Nx accepted)
- [Next.js Documentation](https://nextjs.org/docs)
- [TanStack Query](https://tanstack.com/query)
- [TanStack Router](https://tanstack.com/router)
- [Nx React Plugin](https://nx.dev/nx-api/react)
- [Nx Next.js Plugin](https://nx.dev/nx-api/next)
- [Nx Angular Plugin](https://nx.dev/nx-api/angular)
