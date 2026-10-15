# ADR 005: Monitoring Stack (Prometheus/Grafana/Loki)

**Date**: 2026-01-13  
**Status**: Accepted

## Context

The application needs observability: metrics, logs, and dashboards. Options:

1. **Prometheus + Grafana + Loki** - Self-hosted, open source
2. **AWS CloudWatch** - AWS-native monitoring
3. **Datadog/New Relic** - SaaS observability platforms
4. **ELK Stack** - Elasticsearch, Logstash, Kibana

## Decision

**Use Prometheus, Grafana, and Loki running in Docker on the same EC2.**

Stack:
```
┌─────────────────────────────────────────────────────┐
│                    Grafana                          │
│              (Dashboards & Alerts)                  │
│                   ▲         ▲                       │
│                   │         │                       │
│    ┌──────────────┴──┐  ┌───┴────────────┐         │
│    │   Prometheus    │  │      Loki      │         │
│    │   (Metrics)     │  │    (Logs)      │         │
│    └────────▲────────┘  └───────▲────────┘         │
│             │                   │                   │
│    ┌────────┴────────┐  ┌───────┴────────┐         │
│    │  Spring Boot    │  │    Promtail    │         │
│    │  /actuator      │  │ (Log shipper)  │         │
│    └─────────────────┘  └────────────────┘         │
└─────────────────────────────────────────────────────┘
```

## Consequences

### Pros
- **Zero cost**: All open source, runs on existing EC2
- **Full control**: Own your data, no vendor lock-in
- **Industry standard**: Prometheus is the de facto standard
- **Powerful queries**: PromQL and LogQL
- **Beautiful dashboards**: Grafana is excellent

### Cons
- **Resource usage**: ~500MB RAM for the whole stack
- **Self-managed**: Must update and maintain yourself
- **Single instance**: No HA (acceptable for starter app)

## What's Monitored

### Metrics (Prometheus)
```
# JVM
jvm_memory_used_bytes
jvm_gc_pause_seconds
jvm_threads_live

# HTTP
http_server_requests_seconds_count
http_server_requests_seconds_sum

# Custom
examples_total
users_registered_total
```

### Logs (Loki)
```
# Query by container
{container="starter-backend"}

# Filter errors
{container="starter-backend"} |= "ERROR"

# JSON parsing
{container="starter-backend"} | json | level="ERROR"
```

## Access

```
Grafana:  https://yourdomain.com/grafana
User:     admin
Password: (GRAFANA_PASSWORD from GitHub Secrets)
```

## When to Migrate to Managed Services

Consider CloudWatch or Datadog when:
- Need alerting with PagerDuty/Slack integration
- Need longer retention (>7 days)
- Team needs shared dashboards
- Compliance requires audit trails

## Cost Comparison

| Solution | Monthly Cost |
|----------|--------------|
| Self-hosted (current) | $0 |
| AWS CloudWatch | ~$10-30 |
| Datadog | ~$15/host + $0.10/GB logs |
| New Relic | ~$25/user |

## References

- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)


