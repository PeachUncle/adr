# ADR 0001: Use Azure Functions Consumption Plan for Microservices

**Date**: 2025-10-18  
**Status**: Accepted  
**Feature**: 001-create-a-series  
**Deciders**: Technical Architecture Team

---

## Context

The Village Club management system requires a microservices architecture with the following constraints:
- **Low usage pattern**: Peak usage only Friday/Saturday evenings (8pm-12am), ~4-6 concurrent users
- **Cost efficiency**: Budget requires minimal operational costs (<$50/month total)
- **Scalability**: Must handle 50 concurrent users during events
- **Simplicity**: Small development team, prefer managed services over infrastructure management

The system will have 5 domain services (Membership, Events, Scheduling, Bar, Finance) plus an API Gateway.

## Decision

We will implement all microservices as **Azure Functions using the Consumption Plan** with .NET 8 isolated worker model.

## Rationale

### Cost Analysis
- **Consumption Plan**: ~$0 when idle, ~$0.20 per million executions
  - Estimated cost: $5-10/month for projected usage (8 hours/week peak)
  - Scale to zero automatically during idle periods (Mon-Thu, daytime)
  
- **Alternative costs**:
  - App Service Basic B1: ~$55/service × 5 = $275/month (always-on)
  - Azure Container Apps: ~$40/month minimum (similar complexity to Functions)
  - Functions Premium EP1: ~$200/month (always-warm, overkill for this scale)

### Technical Fit
- **Serverless scale-to-zero**: Aligns perfectly with intermittent usage pattern
- **Automatic scaling**: Handles variable load without manual intervention
- **Fully managed**: No VM or container orchestration management
- **.NET 8 isolated**: Better testability, modern C# features, async-first

### Performance Considerations
- **Cold start**: 3-5 seconds on first request after idle
  - **Mitigation**: Pre-warming via timer trigger during operating hours (7:45pm Fri/Sat)
  - **Acceptable tradeoff**: Users expect social club responsiveness, not millisecond SLAs
  
- **Execution limits**: 230 seconds max per request (far exceeds typical API response time)
- **Concurrency**: Automatic horizontal scaling up to 200 instances per function app

## Alternatives Considered

### Alternative 1: Azure App Service (Always-On)
**Pros**:
- No cold starts
- Predictable performance
- More control over runtime environment

**Cons**:
- **Cost**: $275/month minimum (5 services × B1 tier)
- Resource waste during idle periods (90%+ of the week)
- Manual scaling configuration required
- Doesn't align with "low usage and cost efficiency" requirement

**Rejected**: Cost prohibitive for stated requirements.

### Alternative 2: Azure Container Apps (Consumption)
**Pros**:
- Scale-to-zero like Functions
- Kubernetes-compatible if migration needed
- More control over container environment

**Cons**:
- More DevOps complexity (Dockerfile, image registry)
- Similar cost to Functions but steeper learning curve
- No significant benefit over Functions for HTTP APIs
- Team likely less familiar with containerization

**Rejected**: Additional complexity without corresponding benefit.

### Alternative 3: Azure Functions Premium Plan (EP1)
**Pros**:
- No cold starts (always-warm instances)
- VNET integration for private networking
- Longer execution time limits (unlimited)

**Cons**:
- **Cost**: ~$200/month for EP1 tier
- VNET and always-warm not needed for village club scale
- Over-engineered for requirements

**Rejected**: Cost doesn't justify features not needed.

## Consequences

### Positive
- ✅ **Operational costs stay within budget** (<$10/month for compute)
- ✅ **No infrastructure management** (no VMs, no containers to maintain)
- ✅ **Automatic scaling** handles variable load without configuration
- ✅ **Independent deployment** of each service (microservices benefit)
- ✅ **Built-in monitoring** via Application Insights integration
- ✅ **Familiar development model** for .NET developers (minimal learning curve)

### Negative
- ⚠️ **Cold start latency** on first request after idle (3-5 seconds)
  - Mitigated by pre-warming during operating hours
  - Acceptable for use case (social club, not financial trading)
  
- ⚠️ **Consumption plan has no SLA** (99.95% in practice, but not guaranteed)
  - Acceptable: Manual recovery acceptable within 15 minutes per requirements
  - Can upgrade to Premium if uptime becomes critical
  
- ⚠️ **230-second execution limit** per request
  - Non-issue: All API operations complete in <5 seconds typically
  - Long-running jobs (if needed) can use Durable Functions

### Risks
- **Risk**: Cold starts impact user experience negatively
  - **Mitigation**: Pre-warming timer, can upgrade to Premium if needed
  - **Likelihood**: Low (peak hours are predictable)
  
- **Risk**: Costs increase unexpectedly if usage patterns change
  - **Mitigation**: Set up cost alerts at $30/month threshold
  - **Monitoring**: Track execution counts and costs weekly
  
- **Risk**: Team unfamiliar with serverless paradigms
  - **Mitigation**: Quickstart guide, reference architecture, pair programming
  - **Likelihood**: Low (Functions are simpler than container orchestration)

## Migration Path

If requirements change, migration options exist:

1. **Upgrade to Premium Plan**: Single configuration change, same code
   - Cost: ~$200/month, eliminates cold starts
   - Use case: If uptime SLA becomes critical

2. **Move to Container Apps**: Containerize functions (minimal code changes)
   - Cost: Similar to Premium, more control
   - Use case: If Kubernetes compatibility needed

3. **Move to App Service**: Host functions in App Service (supported)
   - Cost: $55-150/month depending on tier
   - Use case: If predictable load increases

**All migrations preserve existing code and business logic.**

## Monitoring & Review

- **Metric**: Cold start frequency and duration (target <5s, <10 starts/week)
- **Metric**: Monthly execution costs (target <$10/month)
- **Metric**: 95th percentile response time (target <2s including cold starts)
- **Review**: Quarterly review of costs and performance, re-evaluate if patterns change

**Next review date**: 2026-01-18 (3 months after initial deployment)

---

## Related Decisions
- ADR 0002: Shared Database with Schema Isolation
- ADR 0003: JWT Authentication Strategy
- ADR 0004: Azure Blob Storage for Receipt Images

---

**Approved By**: [Technical Lead Name]  
**Date**: 2025-10-18
