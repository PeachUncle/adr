# ADR-002: P1v3 App Service Plan (Cost-Optimized)

## Status

Accepted

## Date

2025-12-04

## Context

The Contoso patient portal has a strict budget constraint of $800/month. We need to balance performance,
availability, and cost while meeting the 99.9% SLA requirement. Unlike the e-commerce platform, this
healthcare application doesn't require zone redundancy—single-region deployment is acceptable.

### Requirements

- $800/month maximum budget
- 99.9% SLA target
- Support 60+ concurrent users (1% of 10K patients + 50 staff)
- VNet integration for private backend access

### Considered Alternatives

1. **Basic B1** - $13/month, no VNet integration, 99% SLA
2. **Standard S1** - $73/month, VNet integration, 99.95% SLA
3. **Premium P1v3** - $146/month, VNet integration, 99.95% SLA
4. **Premium P1v4** - $206/month, zone redundancy, 99.95% SLA

## Decision

We selected **Azure App Service Plan P1v3** (Linux):

| SKU  | vCPU | RAM  | VNet Integration | Zone Redundant | Monthly Cost |
| ---- | ---- | ---- | ---------------- | -------------- | ------------ |
| B1   | 1    | 1.75 | ❌               | ❌             | $13          |
| S1   | 1    | 1.75 | ✅               | ❌             | $73          |
| P1v3 | 2    | 8    | ✅               | ❌             | $146         |
| P1v4 | 2    | 8    | ✅               | ✅             | $206         |

### Why P1v3 Over S1?

- **Performance**: 2 vCPU vs 1 vCPU, 8 GB vs 1.75 GB RAM
- **Deployment Slots**: P1v3 includes 5 slots (S1 has 5 but limited)
- **Auto-scaling**: Better scaling responsiveness
- **Future Growth**: Room for patient growth without SKU change

### Why Not P1v4?

- **Zone Redundancy Not Required**: Single region acceptable for this use case
- **Cost Savings**: $60/month ($720/year) saved
- **Budget Optimization**: Keeps total cost at $207 vs $267 (26% vs 33% of budget)

### Capacity Calculation

- Expected concurrent users: 60 (1% of 10K patients + 50 staff)
- Requests per user: ~1 req/sec
- Total requests: ~60 req/sec
- P1v3 capacity: ~200 req/sec
- Headroom: 70%

## Consequences

### Positive

- 70% of budget available for future enhancements
- VNet integration for private endpoint connectivity
- Adequate capacity for projected workload
- Deployment slots for zero-downtime updates

### Negative

- No zone redundancy (acceptable for this use case)
- Single point of failure at regional level
- May need to upgrade during significant growth

### Mitigations

- Configure auto-restart on failure
- Set up alerts for availability degradation
- Document upgrade path to P1v4 if zone redundancy needed
- Consider geo-replication for DR (within budget)

## References

- [App Service Pricing](https://azure.microsoft.com/pricing/details/app-service/)
- [App Service Plans Comparison](https://learn.microsoft.com/azure/app-service/overview-hosting-plans)
- [VNet Integration](https://learn.microsoft.com/azure/app-service/overview-vnet-integration)
