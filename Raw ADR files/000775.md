---
docid: ADR-060
title: ADR 024 Scheduler Job Monitoring
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# Scheduler Job Monitoring Architecture - ADR

**DocID**: `ADR-024`  
**Title**: Scheduler Job Monitoring with Centralized Aggregation and Distributed Probes  
**Date**: 2. Januar 2026  
**Status**: ✅ Accepted  
**Deciders**: @Architect, @Backend, @Frontend, @DevOps, @Security, @Enventa

---

## Context

B2X requires comprehensive monitoring for scheduler jobs handling ERP/PIM/CRM integrations. The system needs to provide:

- **Health monitoring** for all scheduler jobs and connected services
- **Real-time status updates** for job progress and system health
- **Error logging and analysis** for communication failures
- **Resource monitoring** (CPU/memory) for connected services
- **Management dashboard** for administrators
- **CLI tools** for DevOps monitoring
- **Scalable architecture** supporting multi-tenant operations

**Requirements**:
- Must support **real-time updates** for job status changes
- Must handle **high-volume logging** from ERP integrations
- Must provide **resource monitoring** for connected services
- Must be **scalable** across multiple tenants and bounded contexts
- Must integrate with **existing infrastructure** (PostgreSQL, Elasticsearch, Wolverine)

---

## Decision

Implement **hybrid monitoring architecture** with centralized aggregation and distributed probes:

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Admin BFF (B2X.Admin)                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │ Health API      │  │ Job Status API  │  │ Metrics API    │  │
│  └────────┬────────┘  └────────┬────────┘  └───────┬────────┘  │
└───────────┼─────────────────────┼──────────────────┼────────────┘
            │                     │                  │
            ▼                     ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Monitoring Service (Shared)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Health       │  │ Job State    │  │ Metrics Aggregator   │  │
│  │ Aggregator   │  │ Manager      │  │ (OpenTelemetry)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
            │                     │                  │
     ┌──────┴──────┬──────────────┴───────┬─────────┴────────┐
     ▼             ▼                      ▼                  ▼
┌─────────┐  ┌─────────┐  ┌────────────────────┐  ┌──────────────┐
│ Catalog │  │ Search  │  │ ERP Provider       │  │ PIM/CRM      │
│ Domain  │  │ Domain  │  │ (enventa Actor)    │  │ Provider     │
└─────────┘  └─────────┘  └────────────────────┘  └──────────────┘
```

### Service Boundaries

1. **Monitoring.Shared** - Core monitoring abstractions and interfaces
2. **Monitoring.Infrastructure** - Persistence, Elasticsearch integration
3. **Admin.Monitoring** - API endpoints for admin frontend
4. **Per-Domain Health Probes** - Lightweight probes in each bounded context

### Key Architectural Decisions

#### 1. Centralized vs. Distributed Monitoring
**Decision**: Hybrid approach - centralized aggregation with distributed probes

**Rationale**:
- **Centralized aggregation** provides unified view and consistent APIs
- **Distributed probes** minimize performance impact on domain services
- **Scalable** - can add probes to new bounded contexts without central changes
- **Resilient** - probe failures don't affect central monitoring

**Alternatives Considered**:
- **Fully Centralized**: High coupling, single point of failure
- **Fully Distributed**: Inconsistent APIs, harder to aggregate data

#### 2. Real-time Updates Protocol
**Decision**: SignalR hub for live job status push to frontend

**Rationale**:
- **Native .NET support** - integrates well with existing ASP.NET Core stack
- **WebSocket-based** - efficient for real-time updates
- **Scalable** - supports horizontal scaling with Redis backplane
- **Frontend compatible** - Vue.js SignalR client available

**Alternatives Considered**:
- **WebSockets direct**: More complex, no built-in scaling
- **Server-Sent Events**: One-way only, less efficient for bidirectional
- **Polling**: Higher latency, more server load

#### 3. Data Storage Strategy
**Decision**: PostgreSQL for job state, Elasticsearch for logs/metrics

**Rationale**:
- **PostgreSQL**: ACID transactions for job state consistency
- **Elasticsearch**: Full-text search, time-series queries, aggregation
- **Separation of concerns**: State vs. analytics data
- **Existing infrastructure**: Both already in use in B2X

**Alternatives Considered**:
- **Single database**: Would require compromises on either consistency or analytics
- **Time-series database**: Additional complexity for job state management

#### 4. Scalability Approach
**Decision**: Horizontal scaling via Kubernetes, job queues via Wolverine

**Rationale**:
- **Kubernetes**: Native scaling, resource management, health checks
- **Wolverine**: Existing job scheduling framework, proven scalability
- **Container-based**: Consistent deployment across environments
- **Resource monitoring**: Built-in metrics collection

**Alternatives Considered**:
- **Vertical scaling**: Limited by hardware, single point of failure
- **Custom scaling**: Higher maintenance, reinventing Kubernetes features

### Technology Choices

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Real-time Hub** | SignalR | Native .NET, Vue.js client, scalable |
| **Job State** | PostgreSQL | ACID, existing infra, multi-tenant |
| **Logs/Metrics** | Elasticsearch | Search, aggregation, time-series |
| **Metrics Collection** | OpenTelemetry | Industry standard, Aspire integration |
| **Job Scheduling** | Wolverine | Existing framework, proven reliability |
| **Health Checks** | ASP.NET Core Health Checks | Native, extensible, configurable |

### Data Models

#### Core Entities
```csharp
public record SchedulerJob
{
    public Guid Id { get; init; }
    public string JobType { get; init; } // ERP_SYNC, PIM_IMPORT, CRM_EXPORT
    public string TenantId { get; init; }
    public JobStatus Status { get; init; }
    public int ProgressPercent { get; init; }
    public DateTime CreatedAt { get; init; }
    public DateTime? StartedAt { get; init; }
    public DateTime? CompletedAt { get; init; }
    public string? ErrorMessage { get; init; }
    public Dictionary<string, object> Metadata { get; init; }
}

public record ConnectedService
{
    public Guid Id { get; init; }
    public string Name { get; init; }
    public ServiceType Type { get; init; } // ERP, PIM, CRM, Database
    public string Endpoint { get; init; }
    public ServiceStatus Status { get; init; }
    public DateTime LastChecked { get; init; }
    public DateTime? LastSuccessful { get; init; }
    public double AverageLatencyMs { get; init; }
    public double UptimePercent { get; init; }
    public ResourceMetrics Resources { get; init; }
}

public record ResourceMetrics
{
    public double CpuPercent { get; init; }
    public double CpuAverage { get; init; }
    public double CpuPeak { get; init; }
    public long MemoryUsedBytes { get; init; }
    public long MemoryTotalBytes { get; init; }
    public double MemoryPercent { get; init; }
    public long MemoryPeakBytes { get; init; }
    public int ConnectionPoolActive { get; init; }
    public int ConnectionPoolTotal { get; init; }
    public int ThreadCount { get; init; }
    public int QueueDepth { get; init; }
    public DateTime Timestamp { get; init; }
}
```

### API Design

#### Health Endpoints
```
GET  /api/admin/health/summary          → Overall system health
GET  /api/admin/health/components       → Per-component health status
GET  /api/admin/health/history          → Health history (last 24h)
```

#### Job Status Endpoints
```
GET  /api/admin/jobs                    → List jobs (paginated, filtered)
GET  /api/admin/jobs/{id}               → Job details with logs
GET  /api/admin/jobs/{id}/logs          → Detailed execution logs
POST /api/admin/jobs/{id}/retry         → Retry failed job
POST /api/admin/jobs/{id}/cancel        → Cancel running job
```

#### Connected Services Endpoints
```
GET  /api/admin/services                → List all connected services with status
GET  /api/admin/services/{id}/status    → Current availability status
GET  /api/admin/services/{id}/errors    → Error log for service (paginated)
POST /api/admin/services/{id}/test      → Execute connection test
GET  /api/admin/services/{id}/latency   → Historical latency data
GET  /api/admin/services/{id}/resources → Current resource metrics
GET  /api/admin/services/{id}/communication-errors → Communication error log
```

#### Real-time Hub
```
Hub: /hubs/job-status
  → JobStatusChanged(jobId, status, progress)
  → HealthStatusChanged(component, status)
  → AlertTriggered(alert)
  → ResourceMetricsUpdated(serviceId, metrics)
  → ResourceAlertTriggered(serviceId, alert)
```

### CLI Integration

Extend existing `B2X.CLI` with monitoring commands:

```bash
# Health monitoring
b2c monitor health
b2c monitor health --component catalog
b2c monitor health --history 24h

# Service monitoring
b2c monitor services
b2c monitor services --test enventa-erp
b2c monitor services --errors pim-system
b2c monitor services --resources crm-db

# Job monitoring
b2c jobs list --status failed
b2c jobs show 123e4567-e89b-12d3-a456-426614174000
b2c jobs logs 123e4567-e89b-12d3-a456-426614174000
b2c jobs retry 123e4567-e89b-12d3-a456-426614174000
```

---

## Consequences

### Positive

- **Unified Monitoring**: Single source of truth for all monitoring data
- **Real-time Visibility**: Live updates for job status and system health
- **Scalable Architecture**: Horizontal scaling via Kubernetes
- **Resource Awareness**: CPU/memory monitoring prevents resource exhaustion
- **Error Analysis**: Detailed communication error logging with context
- **DevOps Friendly**: CLI tools for automation and troubleshooting
- **Multi-tenant Ready**: Tenant isolation in all monitoring data

### Negative

- **Complexity**: Hybrid architecture requires coordination between services
- **Performance Overhead**: Distributed probes add monitoring load
- **Data Duplication**: Job state in PostgreSQL, logs in Elasticsearch
- **SignalR Scaling**: Requires Redis backplane for multi-instance deployments

### Risks

- **Probe Performance Impact**: Health probes could affect domain service performance
- **Data Consistency**: Potential lag between job state and log aggregation
- **SignalR Connection Limits**: WebSocket connections may hit browser/server limits
- **Elasticsearch Complexity**: Additional operational complexity for log management

### Mitigation Strategies

- **Probe Optimization**: Lightweight probes, sampling for high-frequency checks
- **Async Processing**: Non-blocking log aggregation and metric collection
- **Connection Management**: SignalR connection pooling and cleanup
- **Data Retention**: Configurable retention policies for logs and metrics

---

## Implementation Plan

### Phase 1: Core Infrastructure (2 sprints)
- [ ] Create Monitoring.Shared project with core abstractions
- [ ] Implement health check framework with distributed probes
- [ ] Set up PostgreSQL tables for job state
- [ ] Configure Elasticsearch indices for logs/metrics

### Phase 2: Job Status & Services (2 sprints)
- [ ] Implement job status tracking with Wolverine integration
- [ ] Build connected services monitoring with resource metrics
- [ ] Create Admin BFF API endpoints
- [ ] Implement SignalR hub for real-time updates

### Phase 3: Error Logging & Analysis (1 sprint)
- [ ] Add communication error logging with request/response details
- [ ] Implement error pattern analysis
- [ ] Build error export functionality for support tickets

### Phase 4: CLI & Frontend Integration (1 sprint)
- [ ] Extend B2X.CLI with monitoring commands
- [ ] Build admin frontend dashboard components
- [ ] Implement real-time updates in Vue.js frontend

### Phase 5: Production Readiness (1 sprint)
- [ ] Add alerting and notification system
- [ ] Implement monitoring dashboards in Grafana
- [ ] Performance optimization and load testing
- [ ] Documentation and training

---

## Related Documents

- **Requirements**: [REQ-001-monitoring-scheduler-jobs.md](.ai/requirements/REQ-001-monitoring-scheduler-jobs.md)
- **Backend Analysis**: Section in REQ-001
- **Frontend Analysis**: Section in REQ-001
- **Security Analysis**: Section in REQ-001
- **DevOps Analysis**: Section in REQ-001

---

## Status

**Status**: ✅ Accepted  
**Implementation**: Phase 1 GitHub issues created (#117-#121)  
**Owner**: @Architect  
**Review Date**: 15. Januar 2026

---

*Deciders: @Architect, @Backend, @Frontend, @DevOps, @Security, @Enventa | Owner: @Architect*