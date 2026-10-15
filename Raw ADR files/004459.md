# ADR-CRM-001 – CRM as Independent AI-First Bounded Context

| Status | Accepted |
|--------|----------|
| Date   | 2025-11-13 |

## Context
- Existing monolithic backend mixes CRM-lite logic with ERP domains; limited events, inconsistent schemas, difficult to evolve.
- CRM requires AI-first features (RAG, LLM, predictive models) and omni-channel interactions that do not fit existing services.
- Other domains (Inventory, Finance, Workflow) are already being extracted as microservices.

## Decision
1. **CRM is its own bounded context** consisting of specialised services (`crm-core`, `crm-sales`, `crm-service`, etc.) with clear ownership of aggregates, databases and event streams.
2. **AI/RAG capabilities are centralised** in `ai-crm` (fronted by `services/ai`) rather than embedding ad-hoc LLM calls inside each service.
3. **Anti-corruption / sync layer (`crm-sync`)** mediates between legacy ERP modules and the new CRM model, emitting canonical events and protecting the core from legacy schemas.
4. **Canonical customer reference** is shared via schema and adapters; all domains referencing customers do so through this structure.

## Consequences
- **Pros**
  - Clean separation of operational CRM logic from ERP; easier to evolve AI-first features.
  - Centralised AI ensures common guardrails, logging, prompt templates, and compliance controls.
  - Event-driven integration encourages reuse of existing modules through adapters rather than direct DB coupling.
  - UI can converge on a consistent Customer 360° experience while gradually embedding legacy forms.
- **Cons**
  - Requires coordinated migration (parallel run) and new infrastructure per CRM service.
  - Need to maintain `crm-sync` adapters until all legacy modules emit canonical events.

## Transitional Plan
- Phase 0: document reuse/refactor/rewrite choices (`docs/crm_reuse_inventory.md`, `docs/crm_ui_mapping.md`).
- Phase 1: implement `crm-core` + `crm-interaction` + `crm-sales` MVP with AI Compose/Summarise endpoints backed by `ai-crm`.
- Phase 2: migrate marketing/service modules, retire monolithic CRM endpoints, tighten SLAs.
