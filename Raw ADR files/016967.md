---
title: "ADR-0001: Dual API Architecture (tRPC + FastAPI)"
description: "Architectural decision for implementing both tRPC and FastAPI to handle different types of operations"
type: "adr"
canonical_url: "/decisions/adr-0001-dual-api-architecture"
status: "accepted"
decision_date: "2024-08-15"
review_date: "2025-02-15"
version: "1.0"
last_updated: "2025-01-09"
authors: ["Lead Architect"]
reviewers: ["Tech Lead", "Backend Team"]
stakeholders: ["Frontend Team", "Backend Team", "DevOps"]
supersedes: []
related_adrs: ["ADR-0002", "ADR-0003"]
tags: ["architecture", "api-design", "trpc", "fastapi", "performance"]
impact: "high"
---

## ADR-0001: Dual API Architecture (tRPC + FastAPI)

## Status

Accepted

## Context

Sightline.ai requires both real-time user interactions (database operations, authentication,
library management) and CPU-intensive AI processing (video transcription, content analysis,
summarization). A single API architecture would either limit TypeScript type safety for frontend
interactions or constrain AI processing performance with Python libraries.

## Decision

Implement a dual API architecture:

1. **tRPC API Layer** (TypeScript): Handle user-facing operations with end-to-end type safety
2. **FastAPI Layer** (Python): Process AI operations with optimal performance and library ecosystem

### Architecture Flow

```text
Frontend → tRPC Router → Database Operations (immediate)
Frontend → tRPC Router → FastAPI → AI Processing → Database Storage
```

## Consequences

### Positive Consequences

- **Type Safety**: End-to-end TypeScript validation from frontend to tRPC procedures
- **Performance**: Python FastAPI optimized for AI/ML workloads with async processing
- **Library Access**: Full Python ecosystem for AI (LangChain, OpenAI, transcript services)
- **Scalability**: Independent scaling of user operations vs. AI processing
- **Developer Experience**: Familiar patterns for both frontend and AI developers

### Negative Consequences

- **Complexity**: Two API surfaces to maintain and coordinate
- **Deployment**: Requires coordination between TypeScript and Python environments
- **Testing**: Need test suites for both API layers
- **Documentation**: Must maintain API docs for both layers

### Risks

- **Service Communication**: FastAPI failures could impact user experience
- **Type Synchronization**: Manual coordination between TypeScript and Python models
- **Deployment Complexity**: Multiple services increase operational overhead

## Alternatives Considered

- **Single TypeScript API**: Rejected due to limited AI/ML library ecosystem and performance
  constraints for CPU-intensive operations
- **Single Python API**: Rejected due to loss of type safety and increased development complexity for frontend interactions
- **Microservices Architecture**: Rejected as over-engineering for current scale, adds unnecessary complexity

## Implementation Notes

### tRPC Layer Responsibilities

- User authentication and session management
- Database CRUD operations for summaries, library, sharing
- Subscription and billing management
- Real-time progress polling

### FastAPI Layer Responsibilities  

- Video transcript acquisition from multiple sources
- OpenAI API integration for content analysis
- Smart Collections classification and tagging
- Task progress tracking for long-running operations

### Integration Pattern

```typescript
// tRPC procedure calls FastAPI
const summary = await api.summary.create.mutate({ url })
// → tRPC creates database record
// → tRPC calls FastAPI for processing
// → FastAPI updates database with AI results
// → Frontend polls progress via tRPC
```

## References

- [tRPC Documentation](https://trpc.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Architecture Design Document](../ARCHITECTURE.md)

---

*Decision Date: 2024-08-15*
*Review Date: 2025-02-15*
