# ADR-010: Choice of Server State Management Library

**Date:** 2025-09-12

**Status:** Decided & Implemented

## Context

The PlumbingPOC application was using a custom `useRequests` hook for server state management, which manually handled data fetching, loading states, error handling, and real-time updates via Supabase subscriptions. As the application grew in complexity, this custom implementation became increasingly difficult to maintain and lacked robust features like automatic request deduplication, background refetching, and optimistic updates.

The application required:
- Efficient caching and request deduplication
- Automatic background refetching and stale-while-revalidate patterns
- Real-time data synchronization
- Optimistic updates for better UX
- Proper error handling and loading states
- Mutation management for data updates

## Decision

We will adopt **TanStack Query (React Query)** as our server state management library. This replaces the custom `useRequests` hook with a battle-tested, production-ready solution that provides all the required functionality out-of-the-box.

## Consequences

*   **Pros:**
    *   **Robust Caching & Performance:** Automatic request deduplication, background refetching, and stale-while-revalidate patterns significantly improve performance and reduce unnecessary API calls.
    *   **Real-time Integration:** Seamless integration with Supabase real-time subscriptions, with automatic query invalidation on data changes.
    *   **Developer Experience:** Declarative API with built-in loading, error, and success states. Mutations with optimistic updates and rollback capabilities.
    *   **Production Ready:** Battle-tested library used by thousands of applications, with excellent TypeScript support and comprehensive documentation.
    *   **Future-Proof:** Active maintenance, regular updates, and a large ecosystem of plugins and integrations.

*   **Cons:**
    *   **Additional Dependency:** Adds ~10KB to the bundle size, though this is minimal compared to the benefits.
    *   **Learning Curve:** Team needs to understand TanStack Query patterns and best practices.
    *   **Migration Effort:** Required refactoring existing data fetching logic and component interfaces.

*   **Implementation Details:**
    *   Replaced `useRequests` hook with `useRequestsQuery` using `useQuery`
    *   Created mutation hooks (`useUpdateRequestStatus`, `useAcceptQuote`, `useTriageRequest`) using `useMutation`
    *   Set up `QueryClient` with `QueryClientProvider` in the app root
    *   Configured 5-minute stale time and window focus refetching
    *   Maintained existing real-time subscription patterns with automatic query invalidation

*   **Alternatives Considered:**
    *   **SWR:** A strong alternative with similar caching capabilities. Chose TanStack Query for its more comprehensive mutation API and better TypeScript support.
    *   **Redux Toolkit Query (RTK Query):** Excellent for complex state management but overkill for our server-state needs. TanStack Query provides the same benefits with less boilerplate.
    *   **Custom Implementation:** Continue with the existing `useRequests` hook. Rejected due to maintenance burden and lack of advanced features like optimistic updates and request deduplication.
    *   **Apollo Client:** Powerful GraphQL client but unnecessary since we're using REST APIs with Supabase.
