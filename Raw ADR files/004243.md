# ADR-0005: Backend Technology Stack for RAG Chatbot

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-06
- **Feature:** 003-rag-chatbot
- **Context:** Building a production-ready RAG chatbot backend requires async-first architecture for streaming responses, vector database integration for semantic search, and serverless deployment for cost-effective hackathon hosting. The system must handle 50+ concurrent users with < 2s response times, support streaming LLM responses (< 500ms first chunk), and operate within free tier constraints (Neon 512MB, Qdrant 1GB, Railway 500 hrs/month). Backend must be stateless, horizontally scalable, and integrate with external services (Gemini API, Better Auth).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use the following integrated backend stack:

- **Framework**: FastAPI 0.109+ with async/await patterns throughout
- **Language**: Python 3.11+ with type hints (Pydantic for validation)
- **Database Drivers**: asyncpg 0.29+ (Postgres), qdrant-client 1.7+ AsyncQdrantClient (vector DB)
- **Logging**: structlog 24.1+ with JSON formatter for machine-readable logs
- **Configuration**: pydantic-settings for type-safe environment variables
- **ASGI Server**: uvicorn with gunicorn for production (multiple async workers)
- **Deployment**: Docker container on Railway/Render (Linux server, horizontal scaling)
- **API Pattern**: RESTful JSON endpoints + Server-Sent Events (SSE) for streaming

## Consequences

### Positive

- FastAPI automatic OpenAPI docs generation (Swagger UI at `/docs`)
- Native async/await support eliminates blocking I/O for 50+ concurrent users
- asyncpg 3-5x faster than psycopg3 for async workloads (per benchmarks)
- Pydantic provides runtime validation + automatic JSON serialization
- structlog JSON logs integrate seamlessly with Railway/Render dashboards
- Docker deployment enables consistent dev/prod environments
- Stateless architecture allows horizontal scaling without session affinity
- SSE streaming provides real-time UX without WebSocket complexity
- Strong Python AI/ML ecosystem (easy integration with future ML features)

### Negative

- Python GIL limits true parallelism (mitigated by async I/O and multi-worker deployment)
- FastAPI framework coupling (migration to another framework requires significant refactoring)
- SSE doesn't support bidirectional communication (acceptable for one-way streaming)
- Docker image size ~500MB (Python + dependencies, slower cold starts vs compiled languages)
- Type hints are not enforced at runtime (rely on Pydantic for validation)
- Railway/Render free tier has 500 hr/month limit (requires monitoring)

## Alternatives Considered

**Alternative A: Node.js + Express + TypeScript**
- Pros: Full-stack TypeScript consistency, large ecosystem, faster cold starts
- Cons: No native async patterns like Python (callbacks/promises more verbose), weaker AI/ML ecosystem, less mature async Postgres drivers
- Rejected: FastAPI's async-first design better suited for streaming + concurrent I/O

**Alternative B: Go + Gin Framework**
- Pros: True parallelism (no GIL), smaller binary size (~20MB), faster execution
- Cons: Verbose error handling, smaller ecosystem for AI/ML, less hackathon-friendly (longer development time)
- Rejected: Python development speed critical for 5-7 day hackathon timeline

**Alternative C: Next.js API Routes (unified frontend/backend)**
- Pros: Single codebase, shared types, simplified deployment (Vercel)
- Cons: Node.js async limitations, poor fit for long-lived streaming connections, Vercel serverless functions have 10s timeout (incompatible with streaming)
- Rejected: Separate backend enables independent scaling and better async support

**Why FastAPI Won**: Best balance of async performance, development speed, AI/ML ecosystem, and hackathon timeline constraints.

## References

- Feature Spec: {{SPEC_LINK}}
- Implementation Plan: {{PLAN_LINK}}
- Related ADRs: {{RELATED_ADRS}}
- Evaluator Evidence: {{EVAL_NOTES_LINK}} <!-- link to eval notes/PHR showing graders and outcomes -->
