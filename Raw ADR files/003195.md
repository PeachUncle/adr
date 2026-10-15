# ADR: Frontend Stack — Next.js (App Router) + React

- Status: Accepted
- Date: 2025-11-11
- Owners: Frontend Team <frontend@example.com>
- Links: PR: TBD, Docs: Next.js, React.dev

## Context

The frontend in this repo uses Next.js (App Router) and React (see `frontend/planeja-ai/package.json`). The app already calls Supabase and contains components for tasks and UI primitives.

## Decision

We will continue using Next.js (App Router) + React 19 for the frontend. Server components will be used for data-heavy pages where appropriate and Client components for interactive pieces (chat UI, forms). The `@supabase/supabase-js` client will be used with environment-scoped keys.

Rationale: Next.js provides routing, image optimization, server actions and App Router features used in the repo. React 19 aligns with Next.js 15+ and the codebase.

## Alternatives Considered

- Single Page React app with CRA/Vite: simpler but loses SSR/SSG benefits.
- Remix: good for full-stack routing, but migration cost and team familiarity favor Next.js.

## Consequences

- Positive: Good DX, SSR/SSR hybrid options, built-in optimizations.
- Negative: App Router complexity for newcomers; enforce a few patterns in docs.

## Implementation Plan

- [ ] Standardize pages/components separation (`app/` for server components)
- [ ] Create `lib/supabase.ts` pattern for client initialization and session handling
- [ ] Build Chat UI as a client component consuming `POST /chats/messages` and streaming responses
- [ ] Add tests for critical components (unit + Playwright for flow)

## Tests

- [ ] Unit tests for components
- [ ] Playwright E2E: send chat message → AI response appears → project generated appears in "My Projects"

## Traceability

| RF ID | RF Description | RNF | Component(s) Impacted |
|-------|----------------|-----|-----------------------|
| RF-FE-001 | Chat UI | Latency/P95 | frontend, API |

## Effort Estimate

Dev:
- UI scaffolding & chat components: 8h
- Integration with API + tests: 6h

QA/Playwright: 6h
