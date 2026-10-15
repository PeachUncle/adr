---
docid: ADR-095
title: ADR 051 Core Monitoring Infrastructure
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# Core Monitoring Infrastructure Architecture - ADR

**DocID**: `ADR-051`  
**Title**: Core Monitoring Infrastructure for Runtime Error Detection and Downtime Reduction  
**Date**: 7. Januar 2026  
**Status**: Draft  
**Deciders**: @Architect, @Backend, @DevOps, @Security  

---

## Context

B2X requires a comprehensive core monitoring infrastructure to detect runtime errors immediately and reduce system downtime. This goes beyond scheduler job monitoring (ADR-024) to cover all application services, infrastructure components, and business-critical processes.

**Requirements**:
- **Runtime Error Detection**: Immediate identification of application failures, exceptions, and performance issues
- **Downtime Reduction**: Proactive monitoring to prevent outages through early warning systems
- **Comprehensive Coverage**: All services, databases, external integrations, and infrastructure components
- **Scalability**: Support for microservices architecture with 100+ services
- **Multi-tenant Awareness**: Tenant-specific monitoring and isolation
- **Integration**: Leverage existing Aspire, Wolverine, and .NET infrastructure

**Business Impact**:
- Reduce mean time to detection (MTTD) from hours to minutes
- Reduce mean time to resolution (MTTR) through automated diagnostics
- Improve system availability to 99.95% SLA
- Enable proactive maintenance and capacity planning

---

## Decision

Implement **comprehensive monitoring infrastructure** using industry-standard tools with .NET-native integrations:

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Monitoring Control Plane                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │ Alert Manager   │  │ Incident        │  │ Dashboard      │  │
│  │ (Alertmanager)  │  │ Response        │  │ (Grafana)      │  │
│  └────────┬────────┘  └────────┬────────┘  └───────┬────────┘  │
└───────────┼─────────────────────┼──────────────────┼────────────┘
            │                     │                  │
            ▼                     ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Metrics & Observability Layer                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Prometheus   │  │ Jaeger        │  │ Elasticsearch       │  │
│  │ (Metrics)    │  │ (Tracing)     │  │ (Logs)              │  │
└─────────────────────────────────────────────────────────────────┘
            │                     │                  │
     ┌──────┴──────┬──────────────┴───────┬─────────┴────────┐
     ▼             ▼                      ▼                  ▼
┌─────────┐  ┌─────────┐  ┌────────────────────┐  ┌──────────────┐
│ API     │  │ Admin   │  │ ERP/PIM/CRM        │  │ Database      │
│ Gateway │  │ Services│  │ Integrations       │  │ Services      │
└─────────┘  └─────────┘  └────────────────────┘  └──────────────┘
     ▲             ▲                      ▲                  ▲
     └─────────────┼──────────────────────┼──────────────────┘
                   ▼
          ┌─────────────────┐
          │ OpenTelemetry   │
          │ Instrumentation │
          └─────────────────┘
```

### Service Boundaries

1. **Monitoring.Shared** - Core monitoring abstractions and OpenTelemetry instrumentation
2. **Monitoring.ControlPlane** - Alert management and incident response
3. **Per-Service Instrumentation** - Lightweight instrumentation in each service
4. **Infrastructure Monitoring** - Kubernetes, database, and external service monitoring

### Key Architectural Decisions

#### 1. Observability Stack
**Decision**: OpenTelemetry + Prometheus + Jaeger + Elasticsearch + Grafana

**Rationale**:
- **OpenTelemetry**: Vendor-neutral, comprehensive instrumentation (metrics, traces, logs)
- **Prometheus**: Industry standard for metrics collection and alerting
- **Jaeger**: Distributed tracing with .NET integration
- **Elasticsearch**: Log aggregation with powerful search capabilities
- **Grafana**: Visualization and dashboarding

**Alternatives Considered**:
- **Datadog/New Relic**: SaaS solutions, higher cost, less control
- **AWS X-Ray/Azure Monitor**: Cloud vendor lock-in
- **Custom solution**: Higher development cost, maintenance burden

#### 2. Instrumentation Strategy
**Decision**: Automatic instrumentation with manual enhancement

**Rationale**:
- **Automatic**: OpenTelemetry auto-instruments ASP.NET Core, HTTP clients, databases
- **Manual Enhancement**: Custom metrics for business logic and domain events
- **Performance**: Minimal overhead (<2%) through sampling and efficient collection
- **Consistency**: Standardized across all services

#### 3. Alerting and Incident Response
**Decision**: Alertmanager with automated incident creation

**Rationale**:
- **Alertmanager**: Flexible routing, silencing, and inhibition
- **Multi-channel**: Email, Slack, PagerDuty, webhook integrations
- **Incident Automation**: Auto-create tickets in issue tracking systems
- **Escalation**: Configurable escalation policies

#### 4. Data Storage and Retention
**Decision**: Tiered storage with configurable retention

| Data Type | Storage | Retention | Rationale |
|-----------|---------|-----------|-----------|
| Metrics | Prometheus | 1 year | Time-series optimization |
| Traces | Jaeger | 30 days | Debug transient issues |
| Logs | Elasticsearch | 90 days | Search and analysis |
| Incidents | PostgreSQL | Indefinite | Audit trail |

#### 5. Multi-tenant Isolation
**Decision**: Tenant-aware labeling and filtering

**Rationale**:
- **Labels**: All metrics/traces/logs tagged with tenant_id
- **RBAC**: Dashboard access controlled by tenant membership
- **Aggregation**: System-wide views for operators, tenant-specific for admins
- **Privacy**: Sensitive data masked in logs

### Technology Choices

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Metrics Collection** | OpenTelemetry .NET | Latest | Native .NET support |
| **Metrics Storage** | Prometheus | 2.x | Industry standard |
| **Distributed Tracing** | Jaeger | Latest | .NET integration |
| **Log Aggregation** | Elasticsearch | 8.x | Powerful search |
| **Visualization** | Grafana | Latest | Rich dashboards |
| **Alerting** | Alertmanager | Latest | Flexible routing |
| **Instrumentation** | OpenTelemetry SDK | Latest | Comprehensive coverage |

### Implementation Plan

#### Phase 1: Foundation (Sprint 2026-01)
- [ ] Create Monitoring.Shared project with OpenTelemetry setup
- [ ] Implement automatic instrumentation for ASP.NET Core services
- [ ] Set up Prometheus scraping configuration
- [ ] Configure basic health checks and metrics

#### Phase 2: Core Monitoring (Sprint 2026-02)
- [ ] Add Jaeger distributed tracing
- [ ] Implement Elasticsearch log aggregation
- [ ] Create Grafana dashboards for key metrics
- [ ] Set up Alertmanager with basic alerting rules

#### Phase 3: Advanced Features (Sprint 2026-03)
- [ ] Implement incident response automation
- [ ] Add custom business metrics
- [ ] Configure advanced alerting rules
- [ ] Set up log correlation with traces

#### Phase 4: Production Readiness (Sprint 2026-04)
- [ ] Performance optimization and scaling tests
- [ ] Security hardening and access controls
- [ ] Documentation and training
- [ ] Go-live monitoring and validation

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance overhead | High | Sampling, efficient instrumentation, monitoring of monitoring |
| Alert fatigue | Medium | Smart alerting rules, auto-silencing, incident correlation |
| Data volume | High | Retention policies, compression, tiered storage |
| Complexity | Medium | Phased implementation, training, documentation |

### Success Metrics

- **MTTD**: <5 minutes for critical issues
- **MTTR**: <1 hour for known issues, <4 hours for new issues
- **Availability**: 99.95% system uptime
- **Alert Accuracy**: >95% true positive rate
- **Instrumentation Coverage**: 100% of services instrumented

---

## Consequences

### Positive
- Immediate visibility into system health and performance
- Proactive issue detection and resolution
- Improved developer experience with rich debugging data
- Better capacity planning and resource optimization
- Enhanced compliance with monitoring and audit requirements

### Negative
- Initial setup complexity and learning curve
- Ongoing operational overhead for monitoring systems
- Potential performance impact (mitigated by design)
- Additional infrastructure costs

### Neutral
- Standardized on industry-leading tools
- Improved team knowledge and skills
- Better integration with existing .NET ecosystem

---

## References
- [OpenTelemetry .NET Documentation](https://opentelemetry.io/docs/net/)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)
- [ADR-024: Scheduler Job Monitoring](ADR-024-scheduler-job-monitoring.md)
- [REQ-117: Core Monitoring Infrastructure](REQ-117-core-monitoring-infrastructure.md)