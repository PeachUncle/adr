# ADR-001: LLM-as-Orchestrator for Pusdatin Chatbot

Date: 2025-11-03
Status: Active (wired behind feature flag)

## Context
- Current chatbot supports three modules: Lahan, Benih & Pupuk, Iklim & OPT DPI.
- Structured Retrieval (deterministic SQL) is the authoritative data path.
- OpenAI is used only for a bounded normalization step (optional via API key).
- `getRAGPrompt()` in ChatbotController is legacy and unused.

## Decision
Introduce an orchestration layer that decides the conversation branch while preserving existing APIs.

Pipeline:
- Preprocessing: ChatNormalizationService (bounded, optional OpenAI)
- Orchestration: ChatOrchestrationService (determineIntent+route)
  - smalltalk -> small talk handler
  - definition -> knowledge base handler
  - data -> ReportService.buildStructuredFirstResponse
  - unknown -> light structured extraction + RAGSummarizer summary (with offline fallback)
- Retrieval: StructuredSearchService (unchanged), plus new KnowledgeBase/SmallTalk services
- Generation: RAG summarizer (scaffolded as RAGSummarizer) for fallback/general Qs with token guards
- UI: guided flow only at onboarding or when backend marks intent=unknown

Feature flag: `ORCHESTRATOR_ENABLED=false` by default. When enabled, unknown intents use `RAGSummarizer` with compact context built from structured extraction; if OpenAI key is missing, it falls back to an offline summary.

## Consequences
- No behavior change until controller is wired to orchestrator behind the flag.
- API contract remains: `{ reply, mode, structured? }`, with optional `intent` field in orchestrated responses (future).

## API Contract (current)
POST /api/chatbot
- Request: `{ message: string, mode: 'natural'|'structured'|'guided' }`
- Response:
  - Natural: `{ reply: string, mode: 'natural', structured?: object }`
  - Structured: `{ reply: string, mode: 'structured', structured: object }`
  - Guided: `{ reply: string, mode: 'guided', options?: array }`

## Rollout
1) Scaffold orchestrator (done)
2) Wire behind flag (done)
3) Add KB/SmallTalk (done)
4) Wire RAG fallback for unknown intents (done)
5) Gate guided in FE by onboarding/unknown (done)
6) Logs & tests (done, focused CI job for orchestrator tests + metrics logs)
7) Cleanup legacy (done)
