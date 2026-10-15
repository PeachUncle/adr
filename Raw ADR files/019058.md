# ADR-0017: Reminder Scheduling Strategy with Dapr Jobs API

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-30
- **Feature:** 002-phase-5-cloud-deploy
- **Context:**

Phase 5 requires in-app notifications when reminders are due (US8). Users can schedule reminders for tasks (e.g., "Remind me 1 hour before deadline"). The system must deliver reminders at exact times reliably.

Key requirements:
- Exact-time delivery: Reminder must fire at scheduled time (NFR-PERF-004: within 1 minute)
- Job state persistence: Reminders must survive server restarts
- Job management: Create, update, delete reminder jobs
- Integration with event-driven architecture: Publish reminder events on job trigger
- Past-due handling: If reminder time is in past, fire immediately

Spec NFR-PERF-004 states: "Reminder delivery MUST be within 1 minute of scheduled time"

US11 requires: "Dapr Jobs API for scheduled reminders" with exact-time delivery.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines reminder delivery mechanism
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Dapr Jobs vs Cron vs Celery Beat vs APScheduler considered
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects Backend API, Notification Service, reminder persistence
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use Dapr Jobs API for exact-time reminder scheduling with callback endpoint to publish reminder events.

**Reminder Scheduling Stack:**
- **Scheduler**: Dapr Jobs API (HTTP callback pattern)
- **Persistence**: Dapr-managed (jobs survive pod restarts)
- **Job Management**: Create on reminder create, update on reminder change, delete on reminder cancel
- **Trigger**: Dapr calls HTTP callback endpoint at scheduled time
- **Event Publishing**: Callback publishes to `reminders` topic for Notification Service
- **Past-Due Handling**: Check if reminder time < now, fire immediately if within 1 minute

**Implementation Pattern:**
```
User sets reminder → Backend API creates reminder entity
                                   ↓
                          Schedule Dapr Job (POST /v1.0-alpha1/jobs)
                                   ↓
                         Job stored in Dapr state (survives restarts)
                                   ↓
                ┌─────────────────────────────────────┐
                │  Scheduled time arrives                │
                │                                     │
                ↓                                     │
        Dapr calls callback endpoint                 │
        /api/dapr/jobs/remind-{id}              │
                ↓                                     │
        Publish reminder event to topic             │
                │                                     │
        Notification Service receives event        │
        │                                     │
        ↓                                     │
        Send in-app notification               │
        │                                     │
        Publish to task-updates for WebSocket     │
                └─────────────────────────────────────┘
```

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

**Exact-Time Delivery:**
- Dapr guarantees callback at scheduled time (within 1 minute as per NFR-PERF-004)
- No polling overhead (event-driven, not time-based checks)
- Precise scheduling (down to second granularity)

**State Management:**
- Jobs persisted by Dapr state store (survives pod restarts)
- No need to implement job persistence in application
- Automatic state synchronization across Dapr replicas

**Resilience:**
- Built-in retry for failed callbacks
- Job state tracking (pending, running, completed, failed)
- Automatic cleanup of completed jobs

**Scalability:**
- Dapr Jobs API scales horizontally (Dapr sidecars distributed)
- No single point of failure for job scheduling
- Independent of Backend API pod count

**Operational Simplicity:**
- Single HTTP endpoint for all job callbacks
- No separate job scheduler service to deploy
- Dapr manages job lifecycle

**Integration:**
- Consistent with ADR-0013 (Dapr Abstraction Layer)
- Event publishing uses same Dapr Pub/Sub API
- No direct database access in callback (event-driven)

### Negative

**Complexity:**
- Requires understanding of Dapr Jobs API (newer feature)
- Callback endpoint registration and routing
- Job lifecycle management (create, update, delete)

**Latency:**
- Additional hop through Dapr sidecar for callback invocation
- Callback may be delayed if Dapr is under load
- Job state updates may lag slightly behind actual execution

**Debugging:**
- Distributed debugging (app callback → Dapr → event → notification)
- Harder to trace job failures across systems
- Job state in Dapr state store (not directly accessible)

**Limitations:**
- Dapr Jobs API is alpha/stable (may have breaking changes)
- Limited to HTTP callbacks (no gRPC/WebSocket callbacks)
- Job TTL and cleanup policies need configuration

**Past-Due Edge Case:**
- Requires immediate firing logic (check time vs now)
- May overwhelm Notification Service if many past-due reminders
- User experience issue (notifications firing for already-passed times)

## Alternatives Considered

**Alternative A: Database Polling with Celery Beat**

**Rejected because:**
- Polling overhead (check every minute, not exact-time)
- Requires separate Celery worker deployment
- Database queries on every poll (inefficient)
- Job state must be managed in application database
- No guarantee within 1 minute (poll interval latency)

**Why rejected:** Polling creates inefficiency and doesn't guarantee exact-time delivery. Requires additional infrastructure (Celery) with operational overhead.

**Alternative B: APScheduler (In-Memory Scheduler)**

**Rejected because:**
- Job state lost on pod restart (all reminders would disappear)
- No high availability (single point of failure)
- Requires leader election for multi-pod deployments
- In-memory state (not persistent across restarts)

**Why rejected:** In-memory schedulers don't survive restarts. Dapr Jobs API provides persistent state management out-of-the-box.

**Alternative C: Cron Bindings (Dapr Scheduled Bindings)**

**Rejected because:**
- Deprecated pattern in Dapr (Jobs API is replacement)
- Less precise (cron syntax limits to minute granularity)
- No callback guarantees (best-effort invocation)
- Harder to manage individual job lifecycle

**Why rejected:** Jobs API is the recommended replacement for cron bindings. Jobs API provides exact-time scheduling with better guarantees.

**Alternative D: Cloud Scheduler (AWS EventBridge, GCP Cloud Scheduler)**

**Rejected because:**
- Cloud vendor lock-in (AWS/GCP specific)
- Doesn't align with Dapr abstraction (ADR-0013)
- Additional external service dependency
- More complex integration with local development
- Separate cost and credential management

**Why rejected:** Dapr Jobs API provides scheduling capability within our chosen stack. Adding external cloud scheduler adds complexity and vendor lock-in.

**Alternative E: Direct Database Triggers (PostgreSQL pg_cron)**

**Rejected because:**
- Database-level concern (shouldn't be in application layer)
- Limited to PostgreSQL-specific (not portable)
- No event integration (would need app code to publish)
- Harder to test and debug
- Callback mechanism not native

**Why rejected:** Database triggers couple application to PostgreSQL. Dapr Jobs API provides abstraction and fits better with event-driven architecture.

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: [specs/002-phase-5-cloud-deploy/spec.md](../../specs/002-phase-5-cloud-deploy/spec.md)
- Implementation Plan: [specs/002-phase-5-cloud-deploy/plan.md#architecture-decisions](../../specs/002-phase-5-cloud-deploy/plan.md#architecture-decisions)
- Dapr Jobs API: https://docs.dapr.io/developing-applications/building-blocks/jobs/
- Constitution Phase 5: [constitution-prompt-phase-5.md](../../constitution-prompt-phase-5.md)
- Related ADRs: ADR-0013 (Dapr Abstraction Layer), ADR-0014 (Microservice Decomposition)
- Evaluator Evidence: None (initial decision)
