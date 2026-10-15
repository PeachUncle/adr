# ADR-003: P1v4 App Service Plan for Zone Redundancy

## Status

Accepted

## Date

2025-12-04

## Context

The e-commerce platform requires 99.9% SLA for the API tier. Azure App Service offers zone redundancy
to protect against datacenter failures, but this feature is only available on Premium v4 (P1v4+) SKUs.

### Requirements

- 99.9% availability SLA
- Support for 10,000 concurrent users at peak
- VNet integration for private backend access
- Zone redundancy for high availability

### Considered Alternatives

1. **Standard S1** - $73/month, no zone redundancy
2. **Premium P1v2** - $146/month, no zone redundancy
3. **Premium P1v3** - $146/month, no zone redundancy
4. **Premium P1v4** - $206/month, zone redundancy supported

## Decision

We selected **Azure App Service Plan P1v4** with zone redundancy enabled:

| SKU  | vCPU | RAM  | Zone Redundant | Monthly Cost |
| ---- | ---- | ---- | -------------- | ------------ |
| S1   | 1    | 1.75 | ❌             | $73          |
| P1v2 | 1    | 3.5  | ❌             | $146         |
| P1v3 | 2    | 8    | ❌             | $146         |
| P1v4 | 2    | 8    | ✅             | $206         |

### Why P1v4 Over P1v3?

Despite identical compute specs (2 vCPU, 8 GB RAM), P1v4 is required because:

- **Zone redundancy** is only available on v4 SKUs
- Azure automatically distributes instances across availability zones
- Provides protection against zone-level failures

### Capacity Calculation

- Expected concurrent users: 100 (1% of 10K patients active)
- Requests per user: ~2 req/sec
- Total requests: ~200 req/sec
- P1v4 capacity: ~500 req/sec
- Headroom: 60%

## Consequences

### Positive

- 99.9% SLA with zone redundancy
- Automatic failover across availability zones
- No application changes required for HA
- VNet integration included

### Negative

- $60/month premium over P1v3
- $133/month premium over S1
- Zone redundancy requires minimum 3 instances (1 per zone)

### Mitigations

- Use autoscaling to optimize costs during off-peak
- Consider 3-year reserved instance (36% savings)
- Monitor DTU usage and right-size if over-provisioned

## References

- [App Service Pricing](https://azure.microsoft.com/pricing/details/app-service/)
- [Zone Redundancy Requirements](https://learn.microsoft.com/azure/app-service/how-to-zone-redundancy)
- [App Service SLA](https://azure.microsoft.com/support/legal/sla/app-service/)
