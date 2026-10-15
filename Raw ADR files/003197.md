# ADR: Use Supabase (Postgres) as Primary Data Platform

- Status: Accepted
- Date: 2025-11-11
- Owners: Platform Team: Backend Owners <backend-team@example.com>, Leticia Cristina Silva (NoSQL - RA: 21352)
- Links: Issue: TBD, PDR: `#PDRs/2025-10-30_MVP_Chat_PDR.md`, Grafana: (link)

## Context

The project currently stores to-do lists and items and needs a more flexible data model to support Projects, TaskLists, Tasks, Chats and ChatMessages. We also want a managed Postgres offering with auth, real-time, and storage features to accelerate development and reduce ops burden.

Evidence:
- The codebase already uses `@supabase/supabase-js` in backend and frontend. The Supabase JS docs confirm it is an isomorphic client with Auth, PostgREST, Realtime, Storage and Functions.

## Decision

We will adopt Supabase as our primary data platform (managed Postgres) and use the `@supabase/supabase-js` client in both backend and frontend. We will store structured data in Postgres tables (Projects, TaskLists, Tasks, Chats, ChatMessages), leverage Supabase Auth for user identity where sensible, and use Supabase Realtime for optional live updates. Vector/embedding storage will use Supabase Vector features if available; otherwise we will integrate a vector store (e.g., pgvector via Supabase).

This decision is testable by deploying migrations, wiring the `createClient()` call, and verifying CRUD + auth flows against a staging Supabase project.

## Alternatives Considered

- Self-managed Postgres on VMs: Pros: full control; Cons: higher operational cost and slower iteration.
- Use a different BaaS (Firebase): Pros: mature realtime; Cons: less SQL flexibility and weaker Postgres compatibility.
- Use a separate vector DB (Pinecone / Milvus): Pros: specialized indexing; Cons: additional infra and integration cost. We'll only adopt if Supabase vector features are insufficient.

## Consequences

- Positive: Fast developer iteration, built-in auth & storage, unified client library in frontend/backend, lower ops burden.
- Negative: Vendor lock-in to Supabase APIs; careful migration plan needed if we change providers.
- Operational: Must secure anon/public keys, configure RLS, and set proper policies to avoid data leaks.

Rollback plan:
- [ ] Revert schema migrations via versioned down-scripts.
- [ ] Reconfigure services to previous DB (if snapshot available) and re-deploy.

## Implementation Plan (Checklist)

- [ ] Create feature branch `feat/adr/supabase-postgres`
- [ ] Add database migrations for: `projects`, `task_lists`, `tasks`, `chats`, `chat_messages` (SQL files in `backend/database/migrations`)
- [ ] Add environment variables for `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY` in staging/production secrets
- [ ] Initialize Supabase client in backend (`backend/src/config/supabase.ts`) using `createClient()` with service role where appropriate
- [ ] Add RLS policies and test with least privilege users
- [ ] Integrate vector index usage (Supabase Vector or pgvector) if RAG flows require semantic search
- [ ] Update frontend to use `@supabase/supabase-js` for authenticated calls where appropriate
- [ ] Create migration rollback scripts and test them in staging

## Testing and Verification

- [ ] Unit tests for DB-layer functions (mock Supabase client)
- [ ] Integration tests applying migrations and running basic CRUD flows
- [ ] Security test: verify RLS prevents cross-user access
- [ ] Load test: smoke test with expected production QPS on staging

## Traceability matrix

| RF ID | RF Description | RNF | Component(s) Impacted |
|-------|----------------|-----|-----------------------|
| RF-DB-001 | Create Project | Data Integrity | backend, supabase DB |
| RF-DB-002 | Chat History | Durability/Retention | backend, supabase storage |

## Effort Estimate

Development:
- Migrations & model design: 4h
- Integration and RLS rules: 4h
- Frontend wiring and small UI updates: 4h

QA/DevOps:
- Staging deploy + rollback test: 2h
- Monitoring dashboards + alerts: 2h

Contingency (20%): add to total
