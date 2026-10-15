# ADR: MVP Chat — AI-assisted Project Generation (Hybrid Chat + CRUD)

- Status: Accepted
- Date: 2025-10-30
- Owners: Tech Team (placeholder — please replace with real owners)
- Related PDR: `#PDRs/2025-10-30_MVP_Chat_PDR.md`
- Related ADRs: `#ADRs/2025-11-11_ADR_AI_LANGCHAIN_AZURE.md`, `#ADRs/2025-11-11_ADR_SUPABASE_POSTGRES.md`, `#ADRs/2025-11-11_ADR_BACKEND_EXPRESS_TS.md`, `#ADRs/2025-11-11_ADR_FRONTEND_NEXTJS_REACT.md`, `#ADRs/2025-11-11_ADR_AUTH_SUPABASE_JWT.md`, `#ADRs/2025-11-11_ADR_SECURITY_VALIDATION.md`

## Context

The product is experiencing significant churn traced to a rigid data model: users cannot group TaskLists under Projects. User feedback and Grafana metrics indicate users abandon the product when they face the "blank page" problem and limited organizational flexibility. The MVP Chat PDR (linked above) prescribes a hybrid solution: an AI-powered chat that can generate an initial Project + TaskLists + Tasks structure, plus a full manual CRUD surface so users retain control.

Go Live date for the MVP: 2025-11-06 (fixed, high-risk). This ADR formalizes the architecture decision for implementing the MVP Chat feature.

## Decision

Implement the MVP Chat as a hybrid system combining:

- A conversational Chat Service that uses LangChain.js as the orchestration/prompt layer and Azure/OpenAI models for generation. The Chat will support creating Projects, TaskLists and Tasks when the AI determines it's appropriate.
- Persistent domain objects in PostgreSQL (via Supabase): `projects`, `task_lists`, `tasks`, plus conversation artifacts: `chats`, `chat_messages`.
- A full CRUD surface (APIs + UI) for Projects, TaskLists and Tasks to allow manual control and post-generation editing.
- The Chat Service must persist conversation history, record AI outputs in `chat_messages`, and trigger `ProjectService` calls when the AI decides to create a Project.

This decision is implemented behind a feature flag to allow staged rollout and rollback.

## Rationale (Why)

- Directly addresses product churn by fixing data model rigidity and offering an assistive AI experience to reduce activation friction (the "blank page").
- LangChain.js offers battle-tested orchestration primitives (chains, tools, memory, RAG patterns) that reduce complexity in prompt management and context handling compared to hand-rolled orchestration.
- Azure/OpenAI managed models provide production-ready inference with streaming and cost controls suited to MVP demands.
- Supabase/Postgres is already in use and supports the required SQL, RLS and vector/embedding workflows needed for future RAG features.
- Keeping manual CRUD ensures users retain control and reduces liability from incorrect AI creations.

## Alternatives Considered

1. Build AI orchestration manually without LangChain
   - Pros: fewer dependencies, direct control.
   - Cons: large engineering effort to replicate prompt management, memory, tool integration and streaming in reduced time.

2. Use a different orchestration library or hosted agent service
   - Pros: Potentially faster integration if hosting exists.
   - Cons: Additional vendor lock-in and potential mismatch with our existing stack (LangChain has strong JS support and community examples for Azure/OpenAI).

3. Do not implement AI at MVP and only fix the DB model (Projects/TaskLists/Tasks)
   - Pros: Lower immediate complexity and risk; fixes core churn cause.
   - Cons: Loses strategic differentiation and the immediate activation improvements from the AI "wow" feature.

The hybrid LangChain + Azure approach balances speed, maintainability and functionality for the tight schedule.

## Consequences

Positive:

- Expected increase in activation and reduced churn by removing the blank-page barrier.
- Competitive differentiation via AI-assisted creation.

Negative / Risks:

- Integration complexity and time pressure: LangChain + Azure + migrations + CRUD before 2025-11-06 is HIGH RISK.
- Cost and privacy concerns for AI calls (monitoring, PII handling and consent required).
- Potential for incorrect or harmful AI-generated tasks — mitigation: human-in-the-loop and editability.

Mitigations:

- Deploy behind a feature flag with a staged rollout and A/B validation.
- Add usage and cost telemetry for AI calls; set quotas and rate limits for the service.
- Add content-safety checks and avoid sending PII to the model (policy + engineering guardrails).

Rollback Plan:

- Use versioned migrations: DBA can revert `projects`, `task_lists`, `tasks`, `chats`, `chat_messages` with rollback scripts.
- Re-deploy previously stable container images for backend/frontend if needed.

## Implementation Checklist (high-level)

DB / Migrations

- [ ] Add migrations for `projects`, `task_lists`, `tasks`.
- [ ] Add migrations for `chats`, `chat_messages`.
- [ ] Add rollback scripts for each migration and validate them in staging.

Backend (per existing repo conventions; current backend uses Express + TypeScript)

- [ ] Create `ProjectService`, `TaskListService`, `TaskService`, `ChatService` (service segregation and tests).
- [ ] Implement endpoints:
  - `POST /chats/messages` — if no `chat_id` present, create `chat` and persist user message; call ChatService orchestration.
  - `GET /chats` — list chats for current user.
  - `GET /chats/:id/messages` — list messages in chat by chronological order.
  - CRUD endpoints for `projects`, `task_lists` and `tasks` (`POST`, `GET`, `PUT`, `DELETE`), including `GET /projects/:id/lists`.
- [ ] Implement LangChain integration:
  - Setup a LangChain client wrapper using a safe prompt persona/agent, streaming where feasible.
  - Maintain short-term conversation memory (chat history) and persist to `chat_messages`.
  - Provide a tool or service boundary allowing the ChatService to call `ProjectService` when AI decides to create a project.
- [ ] Implement feature flag around AI generation logic and server-side toggles.

Frontend (Next.js App Router)

- [ ] Chat History view integrated with `GET /chats`.
- [ ] Chat Conversation UI integrated with `GET /chats/:id/messages` and `POST /chats/messages`.
- [ ] Real-time update of AI responses: prefer streaming; fall back to polling when streaming unsupported.
- [ ] My Projects page and Project Details page displaying `TaskLists` and `Tasks`.
- [ ] Manual CRUD UI for Projects, TaskLists, Tasks.

Security, Validation and Operational

- [ ] Use RLS and least-privilege with Supabase/Postgres for multi-tenant user isolation.
- [ ] Validate all requests with `express-validator` (or equivalent) and centralize error responses.
- [ ] Protect endpoints with `helmet`, `cors` and `express-rate-limit` per `#ADRs/2025-11-11_ADR_SECURITY_VALIDATION.md`.
- [ ] Add logging, metrics and tracing for AI invocation latency, errors, and cost metrics (Sentry/Prometheus/Grafana).

Testing and Verification

- [ ] Unit tests for services and controllers (happy-path + error flows).
- [ ] Integration tests for endpoints (create chat, add messages, generate project flow).
- [ ] E2E tests for the UI flows (chat -> project creation -> projects listing).
- [ ] DBA verification that migrations and rollback scripts succeed in staging.

Rollout

- Feature flag the Chat generation and do staged rollout to a subset of users.
- Monitor key metrics: activation (% users creating projects), churn, AI call volume/cost, and error rates.

Traceability

- This ADR satisfies PDR user stories US-101 through US-107 (see linked PDR). Traceability matrix entries and acceptance tests are in `#PDRs/2025-10-30_MVP_Chat_PDR.md`.

Effort Estimate (rough, per PDR constraints)

- DBA: 0.5–1d to design migrations + validate rollbacks.
- BE: 3–6 engineer-days (services, endpoints, LangChain integration, feature flags) — HIGH RISK.
- FE: 3–5 engineer-days (chat UI, projects pages, CRUD integration).
- QA/Release: 1–2 engineer-days for staging, integration and hotfixes.

Owners and Contacts

- Primary Owner: Tech Team (please replace with specific names/emails)
- Backend Lead: (placeholder)
- Frontend Lead: (placeholder)
- DBA: (placeholder)
- Security/Ops: (placeholder)

Implementation Notes and References

- Follow `#PDRs/2025-10-30_MVP_Chat_PDR.md` for test cases, traceability matrix and Gantt.
- See `#ADRs/2025-11-11_ADR_AI_LANGCHAIN_AZURE.md` for LangChain + Azure design decisions and vendor notes.
- See `#ADRs/2025-11-11_ADR_SUPABASE_POSTGRES.md` for DB practices, RLS and vector store guidance.

Status and Next Steps

- This ADR is accepted (2025-10-30). Next: implement the checklist above in staging behind a feature flag and validate migrations/rollback.

---

If you want, I can now:

- Extract the implementation checklist into GitHub issues/PR templates.
- Generate example SQL migration skeletons for `projects`, `task_lists`, `tasks`, `chats`, `chat_messages`.
- Create a PR with this ADR and the PDR link included.

Please tell me which (if any) of these follow-ups you'd like me to do next.
