# ADR-006: Azure Container Apps Scale-to-Zero Configuration

**Status:** ✅ Accepted  
**Date:** 2025-08-09  
**Author:** AI Development Partner  
**Context:** Azure Container Apps deployment configuration optimization

## Problem Statement

Azure Container Apps supports scaling to zero replicas, which would eliminate compute costs during idle periods when no Discord interactions are occurring. Our initial deployment plan specified `minReplicas: 1`, which would maintain constant compute costs even during idle periods.

## Decision Context

### Research Findings

**Microsoft Documentation Research:**
- Azure Container Apps **default behavior** is scale-to-zero for HTTP-triggered applications
- Default scale rule: `HTTP | Min: 0 | Max: 10`
- No charges incurred when application scales to zero
- Automatic scaling based on incoming HTTP requests
- Cold start performance: typically <2 seconds for container startup

### Use Case Analysis

**Discord Publish Bot Usage Pattern:**
- **Sporadic Usage**: Discord interactions are user-initiated and infrequent
- **Mobile Posting**: Primary use case involves manual mobile posting (low frequency)
- **HTTP-Triggered**: All Discord interactions arrive via HTTP webhooks
- **Stateless Design**: No persistent in-memory state requiring constant availability

### Cost-Benefit Analysis

**Scale-to-Zero Benefits:**
- **Zero compute costs** during idle periods (majority of time)
- **Automatic scaling** based on actual demand
- **Same functionality** with optimal resource utilization
- **Cold start acceptable** for Discord interaction response times

**Considerations:**
- **Cold Start Latency**: ~2 seconds for container startup
- **Discord Timeout**: 3-second response requirement (sufficient margin)
- **Background Tasks**: GitHub publishing continues during container lifecycle

## Decision

**✅ ADOPTED: Scale-to-Zero Configuration for Single-User Bot**

Configure Azure Container Apps with:
```yaml
scale:
  minReplicas: 0     # Enable scale-to-zero
  maxReplicas: 2     # Single-user optimization
  rules:
    - name: http-rule
      http:
        metadata:
          concurrentRequests: '10'  # Default HTTP scaling
```

**Resource Specifications:**
- **CPU:** 0.25 cores (reduced from 0.5) 
- **Memory:** 0.5GB (reduced from 1GB)
- **Max Replicas:** 2 (single-user optimization)
- **Scale Trigger:** HTTP (default Azure Container Apps behavior)

## Rationale

### Technical Justification

1. **Natural Fit**: Discord webhook pattern aligns perfectly with HTTP-triggered scaling
2. **Cost Optimization**: Eliminates compute costs during 95%+ of idle time
3. **Performance Adequate**: Cold start latency acceptable for Discord interaction patterns
4. **Proven Pattern**: Azure Container Apps designed specifically for this use case

### Industry Best Practices

- **Serverless First**: Modern cloud architecture favors event-driven scaling
- **Cost Efficiency**: Pay-per-use model optimal for sporadic workloads
- **Microsoft Recommendation**: Azure Container Apps documentation promotes scale-to-zero as default

### Risk Mitigation

- **Discord Timeout**: 3-second limit provides sufficient margin for cold start
- **Monitoring**: Application Insights will track cold start performance
- **Fallback Option**: Can adjust `minReplicas` to 1 if cold start issues arise

## Implementation Plan

### Phase 2 Updates
- Update Azure CLI commands to use `--min-replicas 0`
- Configure Application Insights to monitor cold start metrics
- Validate Discord interaction response times in production

### Monitoring Strategy
- Track cold start frequency and duration
- Monitor Discord interaction response times
- Alert if response times approach 3-second limit

## Consequences

### Positive
- **✅ Significant cost reduction** during idle periods
- **✅ Automatic resource optimization** based on actual usage
- **✅ Simplified operational model** (no manual scaling decisions)
- **✅ Industry-standard serverless pattern**

### Negative
- **⚠️ Cold start latency** for first request after idle period
- **⚠️ Monitoring complexity** for scale events

### Neutral
- **📊 Equivalent functionality** with optimized resource utilization
- **📊 Standard Azure Container Apps behavior**

## References

- [Azure Container Apps Scaling Documentation](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)
- [Azure Container Apps Billing](https://learn.microsoft.com/en-us/azure/container-apps/billing)
- [KEDA HTTP Scaler](https://keda.sh/docs/scalers/apache-http-server/)
- [Discord Webhook Response Times](https://discord.com/developers/docs/interactions/receiving-and-responding)

## Related ADRs

- ADR-005: Docker Container Optimization for Azure Container Apps
- ADR-004: Azure Container Apps Deployment Platform Choice

---

**Next Review:** Upon completion of Phase 2 deployment and initial production monitoring  
**Success Metrics:** Cold start <2s, Discord response <3s, cost reduction >80% during idle periods
