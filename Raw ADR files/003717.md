# ADR-002: Aurora Serverless v2 vs Traditional RDS

## Status
Accepted

## Context
Need a database solution that can handle variable workloads, provide high availability, and optimize costs for a SaaS application with unpredictable traffic patterns.

## Decision
Use Aurora Serverless v2 instead of traditional RDS instances.

## Rationale

### Aurora Serverless v2 Advantages
- **Auto-scaling**: 0.5 to 128 ACUs based on demand
- **Cost Efficiency**: Pay only for capacity used
- **High Availability**: Multi-AZ by default
- **Global Database**: Cross-region read replicas with <1s lag
- **Instant Scaling**: Sub-second scaling response

### Traditional RDS Considerations
- **Predictable Costs**: Fixed monthly pricing
- **Full Control**: Instance types, storage, configuration
- **Proven Stability**: Mature service with extensive tooling
- **Lower Complexity**: Simpler capacity planning

## Cost Analysis

### Aurora Serverless v2
```
Base Cost: $0.12/ACU-hour
Storage: $0.10/GB-month
I/O: $0.20/million requests

Example (variable load):
- Low: 2 ACUs × 8 hours = $1.92/day
- High: 16 ACUs × 4 hours = $7.68/day
- Average: ~$150/month
```

### RDS (db.r6g.large)
```
Instance: $0.192/hour = $138/month
Storage: 100GB × $0.115 = $11.50/month
Total: ~$150/month (fixed)
```

## Decision Factors

1. **Traffic Variability**: 10x difference between peak and off-hours
2. **Global Expansion**: Need for cross-region read replicas
3. **Development Velocity**: Serverless reduces operational overhead
4. **Cost Optimization**: Pay-per-use aligns with SaaS model

## Performance Characteristics

| Metric | Aurora Serverless v2 | RDS |
|--------|---------------------|-----|
| Scaling Time | <30 seconds | Manual (minutes) |
| Availability | 99.99% | 99.95% |
| Backup | Continuous | Point-in-time |
| Read Replicas | 15 (global) | 5 (regional) |
| Connection Pooling | Built-in | Manual setup |

## Consequences

### Positive
- Automatic scaling reduces operational burden
- Cost optimization for variable workloads
- Built-in high availability and disaster recovery
- Global database capabilities

### Negative
- Less predictable costs during traffic spikes
- Newer service with fewer third-party tools
- Cold start latency for very low traffic periods
- Limited configuration options vs traditional RDS

## Monitoring Strategy
- CloudWatch metrics for ACU utilization
- Performance Insights for query optimization
- Cost anomaly detection for unexpected scaling
- Automated alerts for sustained high utilization

## Fallback Plan
If costs exceed budget or performance issues arise:
1. Analyze traffic patterns and optimize queries
2. Consider Aurora Provisioned with auto-scaling
3. Implement connection pooling and caching layers
4. Migrate to traditional RDS if necessary

## Review Date
Q3 2024 - Evaluate cost trends and performance metrics