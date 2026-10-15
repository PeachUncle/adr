# ADR-0001: Frontend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** 001-phase-2-web-app
- **Context:** Phase 2 requires transforming the Phase 1 console application into a production-ready, multi-user web application. The frontend must support modern UI/UX, be mobile-responsive (320px+), achieve <1.5s First Contentful Paint, and deploy to free-tier services. The frontend must integrate with Better Auth for authentication and communicate with a FastAPI backend.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines the entire frontend platform
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Remix, CRA, Vite+React evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all frontend development
-->

## Decision

We will adopt the following integrated frontend technology stack:

- **Framework:** Next.js 16+ (App Router with Server Components)
- **Language:** TypeScript 5.0+
- **Styling:** Tailwind CSS 4.0
- **Component Library:** Shadcn/ui (Radix UI primitives) + Aceternity UI (visual effects)
- **State Management:** Zustand 5.0+ with persist middleware (MANDATORY - NO React Context)
- **HTTP Client:** Axios 1.7+ with interceptors (MANDATORY - NO fetch API)
- **Animation:** Framer Motion 11+
- **Deployment:** Vercel Edge Network
- **Form Handling:** React Hook Form + Zod validation
- **Testing:** Jest + React Testing Library + Playwright (E2E)

### Rationale

This stack provides an integrated solution where all components work seamlessly together. Next.js + Vercel offer tight integration for deployment, Tailwind + Shadcn/ui provide consistent styling with minimal configuration, and Zustand + Axios offer predictable, testable patterns for state and API communication. The stack is optimized for developer experience while meeting performance requirements.

## Consequences

### Positive

- **Integrated Tooling:** Next.js, Tailwind, and Vercel are designed to work together, reducing configuration complexity
- **Excellent Developer Experience:** TypeScript support, hot reload, automatic routing, and clear error messages
- **Performance Optimizations:** Server Components reduce bundle size, automatic code splitting, edge caching on Vercel
- **Strong TypeScript Support:** All libraries have first-class TypeScript support with excellent type inference
- **Modern Patterns:** App Router enforces server/client component boundaries, encouraging best practices
- **Zero-Config Deployment:** Vercel detects Next.js automatically, handles builds, and provides instant previews
- **State Predictability:** Zustand's single-store pattern with persist ensures consistent state across sessions
- **HTTP Reliability:** Axios interceptors provide global error handling, auth token injection, and retry logic
- **Component Reusability:** Shadcn/ui copy-paste components give full control without NPM dependency bloat
- **Visual Polish:** Aceternity UI provides production-ready animations for landing page differentiation

### Negative

- **Vercel Vendor Lock-in:** While the app can run elsewhere, Vercel's edge features may create migration friction
- **Framework Coupling:** Next.js-specific patterns (Server Components, `useRouter`) make framework switching harder
- **Learning Curve:** Server Components, async components, and middleware patterns require mental model shift
- **Build Complexity:** Server/client boundaries can cause subtle bugs if not understood properly
- **Bundle Size:** Framer Motion adds ~30KB gzipped; acceptable for Phase 2 but should be monitored
- **Zustand vs Context Trade-off:** Zustand adds a dependency where Context is built-in, but Context causes re-render issues with frequent updates
- **Axios vs Fetch Trade-off:** Axios adds ~5KB but provides interceptor patterns that fetch lacks natively

## Alternatives Considered

### Alternative Stack A: Remix + styled-components + Cloudflare Pages
- **Pros:** Better nested routing, built-in form handling, edge-first architecture
- **Cons:** Smaller ecosystem, steeper learning curve, less mature than Next.js, styled-components adds runtime overhead
- **Why Rejected:** Remix's focus on server-side rendering doesn't align with our optimistic UI requirements; styled-components conflicts with Tailwind CSS approach

### Alternative Stack B: Vite + React + vanilla CSS + AWS Amplify
- **Pros:** Faster dev builds, more flexible, no framework lock-in
- **Cons:** Manual setup for routing, SSR, authentication; requires configuring build pipeline and deployment
- **Why Rejected:** Too much manual configuration; does not meet "spec-driven development" principle requiring integrated solutions

### Alternative Stack C: Create React App (CRA)
- **Pros:** Simple setup, well-known
- **Cons:** Deprecated by React team, no SSR, poor performance, no longer maintained
- **Why Rejected:** Officially deprecated; does not meet modern performance standards

### State Management Alternative: React Context API
- **Pros:** Built-in, no dependencies, simpler API
- **Cons:** Re-renders entire component tree on updates, no middleware (persist, devtools), verbose setup with reducers
- **Why Rejected:** Context causes performance issues with frequent task updates; Zustand provides persist middleware and optimistic update patterns needed for our use case

### HTTP Client Alternative: Native Fetch API
- **Pros:** Built-in, no dependencies, modern standard
- **Cons:** No interceptors (must manually add auth headers everywhere), verbose error handling, no automatic retries
- **Why Rejected:** Lack of interceptors leads to repetitive auth token injection code; global error handling (401 → logout) requires manual setup per request

## References

- Feature Spec: [specs/001-phase-2-web-app/spec.md](../../specs/001-phase-2-web-app/spec.md)
- Implementation Plan: [specs/001-phase-2-web-app/plan.md](../../specs/001-phase-2-web-app/plan.md)
- Research Notes: [specs/001-phase-2-web-app/research.md](../../specs/001-phase-2-web-app/research.md)
- Related ADRs: ADR-0003 (Authentication Architecture), ADR-0004 (UI Component Strategy)
- Context7 Research: Next.js (/vercel/next.js), Zustand (/pmndrs/zustand), Axios (community best practices)
