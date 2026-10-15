---
title: "ADR 008: Centralized AI Rate Limiting & Gateway"
type: "architecture"
audience: "developer"
status: "accepted"
priority: "high"
version: "1.0.0"
created: "2025-12-12"
updated: "2025-12-22"
reviewers: ["@opencode"]
related: ["../02-implementation/ai-integration.md", "../03-operations/monitoring.md"]
tags: ["adr", "architecture", "ai", "rate-limiting", "gateway"]
---

# ADR 008: Centralized AI Rate Limiting & Gateway

## Status
**Current Status:** Accepted

## Date
**Created:** 2025-12-12  
**Updated:** 2025-12-22

## Context

Our application relies heavily on external AI services (Perplexity, OpenAI) for features like portfolio enrichment, task generation, and architectural analysis. As the number of automated scripts (e.g., `enrich-portfolio.ts`) and API routes grew, we began experiencing frequent `429 Too Many Requests` errors.

### Root Causes

These errors occurred because:

1. **Isolated Instantiation**: Scripts and API routes instantiated their own isolated `OpenAI` clients
2. **Parallel Execution**: Requests were fired in parallel (`Promise.all`) without centralized concurrency control
3. **Missing Retry Logic**: There was no unified retry logic or exponential backoff strategy
4. **No Rate Limit Awareness**: Immediate failures upon hitting rate limits without graceful handling

### Problem Impact

This instability prevented reliable bulk processing and degraded the user experience, making it impossible to perform batch operations without manual intervention.

---

## Decision

We have decided to implement a **Centralized AI Gateway** pattern using a Singleton Client located in `lib/ai/core.ts`.

### Key Design Choices

1. **Singleton Instance**: All parts of the application must invoke AI operations through a single exported function `safeCompletion()` rather than instantiating `new OpenAI()` classes directly.

2. **Global Request Queue**: The client enforces strict sequential execution (or throttled concurrency) by chaining promises internally. A default delay (e.g., 2000ms) is enforced between requests to respect API provider limits.

3. **Automatic Retry with Backoff**: The client catches `429` errors and automatically retries the request after waiting for an exponentially increasing duration (2s, 4s, 8s).

4. **Robust Environment Loading**: The module internally handles the complexity of loading API keys (checking `.env` and `.env.local`), ensuring consistent behavior across both Next.js server runtime and standalone CLI scripts.

---

## Consequences

### Positive Impacts

- ✅ **Reliability**: `429` errors are effectively eliminated or handled gracefully, allowing long-running batch jobs to complete without supervision.
- ✅ **Maintainability**: API configuration (Base URL, Models, Keys) is centralized in one file. Changing providers (e.g. switching from Perplexity to another) only requires updating `lib/ai/core.ts`.
- ✅ **Simplicity**: Consuming code (scripts/routes) is cleaner, as it no longer needs to handle auth or error loops.
- ✅ **Consistency**: All AI operations use the same retry logic and rate limiting strategy.

### Negative Impacts

- ⚠️ **Performance**: Sequential processing significantly increases the total time for bulk operations compared to parallel execution. 
  - **Mitigation**: This is acceptable for background enrichment tasks where stability > speed.
- ⚠️ **Global State**: The queue relies on in-memory state. In a serverless environment (e.g., Vercel deployment), this state is not shared across lambda instances.
  - **Mitigation**: For the current local-first / single-user dashboard scope, this is sufficient. For scaled production, this would need to move to a persistent queue (Redis/BullMQ).

### Impact Assessment

| Area | Impact | Notes |
|-------|--------|-------|
| **Performance** | Medium | Sequential processing adds latency but improves reliability |
| **Maintainability** | High | Centralized configuration simplifies management |
| **Scalability** | Low | Memory-based state limits serverless scaling |
| **Reliability** | High | Eliminates rate limiting failures |
| **Developer Experience** | High | Simplifies AI integration across codebase |

---

## Implementation Status

### Completed Components

- ✅ **`lib/ai/core.ts`**: Core singleton implementation with rate limiting and retry logic
- ✅ **`app/api/ai/describe/route.ts`**: Refactored to use `safeCompletion()` instead of direct OpenAI client
- ✅ **`scripts/enrich-portfolio.ts`**: Refactored to use `safeCompletion()` for batch processing
- ✅ **Environment Handling**: Robust loading of API keys from multiple sources

### Integration Points

- **API Routes**: All `/api/ai/*` endpoints must use `safeCompletion()`
- **CLI Scripts**: All standalone scripts importing AI functionality must use the centralized gateway
- **Error Handling**: Centralized retry logic with exponential backoff

---

## Migration Strategy

### Phase 1: Code Migration
1. **Identify All AI Usage**: Audit codebase for direct `OpenAI` or `Perplexity` client instantiation
2. **Update Imports**: Replace with imports from `lib/ai/core.ts`
3. **Update Function Calls**: Replace direct client calls with `safeCompletion()`

### Phase 2: Testing & Validation
1. **Unit Testing**: Test retry logic and rate limiting behavior
2. **Integration Testing**: Verify bulk operations complete successfully
3. **Load Testing**: Test with multiple concurrent operations

### Phase 3: Monitoring & Optimization
1. **Performance Metrics**: Monitor request timing and success rates
2. **Error Tracking**: Log rate limit events and retry attempts
3. **Future Enhancement**: Consider persistent queue for production scaling

---

## Related Documents

### Referenced By
- [🏗️ Architecture Overview](../../ARCHITECTURE.md) - System architecture impact
- [🛠️ AI Integration Guide](../02-implementation/ai-integration.md) - Implementation details
- [📊 Monitoring Guide](../03-operations/monitoring.md) - Performance tracking

### References To
- [ADR-009](009-local-database-strategy.md) - Database strategy for AI operations
- [ADR-010](010-github-actions-governance.md) - CI/CD governance affecting batch operations
- [🔧 API Documentation](../05-reference/api-reference.md) - Updated AI endpoints

---

## Discussion

### Open Questions
- ❓ **Scaling Requirements**: When should we move to persistent queue for production scaling?
- ❓ **Multiple Providers**: Should we standardize on single AI provider vs. multi-provider support?

### Team Comments
- **@architecture-team**: Approved singleton approach for improved reliability
- **@devops-team**: Requested monitoring integration for production deployment

---

## Next Steps

### Immediate
1. **Complete Migration**: Finish converting all AI usage to centralized gateway
2. **Add Logging**: Implement detailed logging for rate limit events
3. **Update Documentation**: Reflect new AI integration patterns

### Short-term
1. **Performance Optimization**: Implement smart batching for compatible requests
2. **Caching Layer**: Add response caching for identical prompts
3. **Monitoring Dashboard**: Add AI usage metrics to operations dashboard

### Long-term
1. **Persistent Queue**: Evaluate Redis/BullMQ for production scaling
2. **Multi-Provider Support**: Design architecture for multiple AI providers
3. **Cost Optimization**: Implement cost tracking and optimization strategies

---

## Change History

### v1.0.0 (2025-12-12)
- ✨ Initial documentation of the decision
- 📋 Context and consequences documented
- 🔧 Implementation details specified

### v1.1.0 (2025-12-22)
- 📋 Standardized metadata to follow Documentation Governance Framework
- 🏗️ Added impact assessment table
- 🔗 Added related documents and discussion sections
- 📝 Enhanced implementation status tracking

---

**💡 Governance Note:** This ADR should be reviewed quarterly or when AI usage patterns change significantly. If performance requirements change, consider creating a new ADR that supersedes this one.