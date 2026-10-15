# ADR-0011: UI Framework Selection for Portal

Status: Accepted
Date: 2025-10-09
Deciders: Architecture Team (architect.morgan-lee)

## Context
The MaxAI Platform requires a modern, performant, and accessible UI framework for the client portal (apps/portal-web). The portal handles multi-tenant onboarding, connections management, usage dashboards, and billing views with RBAC enforcement. We need a stack that supports SSR, accessibility, theming, state management, and API integration while maintaining developer productivity and compliance with our security baseline (ADR-0008).

## Decision
Adopt the following frontend technology stack for the portal:

1. **Framework**: Next.js 14 with App Router
   - Server-side rendering for performance and SEO
   - API routes for backend integration
   - App Router for nested layouts and improved routing

2. **React Version**: React 18 with Server Components
   - Enhanced performance with Server Components
   - Concurrent features for better UX

3. **UI Components**: shadcn/ui with Tailwind CSS
   - Accessibility-first components (WCAG compliant)
   - Consistent design system with easy theming
   - Utility-first CSS for maintainability

4. **Client State Management**: Zustand
   - Lightweight and simple for UI state (forms, toggles)
   - Avoids complexity of Redux for our use cases

5. **Server State Management**: TanStack Query (React Query)
   - Efficient API data fetching and caching
   - Optimistic updates and background refetching
   - Integration with error boundaries and loading states

## Consequences
- **Positive**: Improved performance, accessibility, and developer experience. Aligns with modern React/Next.js best practices. Supports our multi-tenant, feature-flagged portal.
- **Negative**: Learning curve for shadcn/ui if unfamiliar. Bundle size increase from additional libraries (mitigated by tree-shaking).
- **Risks**: Ensure Tailwind customization doesn't conflict with multi-tenant theming. Monitor TanStack Query for audit logging integration.
- **Dependencies**: Requires Next.js upgrade if not on 14. Adds dev dependencies for shadcn/ui CLI.

## Alternatives Considered
- **Material-UI + Emotion**: Heavier bundle, less flexible theming.
- **Chakra UI**: Similar to shadcn/ui but less customizable.
- **Redux Toolkit**: Overkill for client state; Zustand is simpler.
- **SWR**: Similar to TanStack Query but less feature-rich for our API-heavy app.

## References
- ops/docs/design/ui-framework-spec.md
- ops/docs/design/architecture-overview.md
- ADR-0008: Security/Compliance Baseline