# ADR-0003: Reminder Scheduling Strategy (Dapr Jobs API)

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-29
- **Feature:** 007-phase5-cloud-deployment
- **Context:** Phase V requires sending reminder notifications at exact times specified by users (e.g., "Remind me at 4:00 PM UTC on December 31st"). Success Criterion SC-005 mandates ±30s accuracy. Polling-based approaches (check database every minute for `reminder_at` field) introduce 60s latency and waste CPU cycles. The scheduler must survive pod restarts and handle duplicate event processing (idempotency).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: ✅ Long-term consequence - affects reminder delivery reliability, pod restart recovery, accuracy guarantees
     2) Alternatives: ✅ Multiple viable options - Cron Bindings (mature), Celery Beat, Kubernetes CronJobs
     3) Scope: ✅ Cross-cutting concern - impacts Notification Service, State Store usage, event consumption
     All three tests passed - ADR justified. -->

## Decision

Use Dapr Jobs API (alpha feature, Dapr 1.12+) for exact-time reminder scheduling:

- **Scheduling Mechanism**: One-time jobs at specific UTC timestamp (not polling-based intervals)
- **Job Persistence**: Jobs stored in Dapr State Store (PostgreSQL) and survive pod restarts
- **Webhook Invocation**: Dapr invokes Notification Service HTTP endpoint (`POST /dapr/jobs/reminders`) at scheduled time
- **Accuracy**: ±1s under normal conditions (Dapr scheduler runs every 1 second), well within ±30s requirement
- **Retry Strategy**: Automatic retry with exponential backoff (1s → 2s → 4s), max 3 retries
- **Idempotency**: Use task_id in job name (`job_name = "reminder-{task_id}"`) - overwrites duplicate jobs

Application code schedules reminders via Dapr Jobs API HTTP POST:
```
POST http://localhost:3500/v1.0-alpha1/jobs/reminders
{
  "name": "reminder-123",
  "dueTime": "2025-12-31T16:00:00Z",
  "repeats": 1,
  "data": {"task_id": 123, "user_email": "user@example.com", "task_title": "Submit Q4 report"}
}
```

## Consequences

### Positive

- **Exact-Time Scheduling**: Schedule job at specific UTC timestamp (e.g., 2025-12-31 16:00:00), not fixed intervals
- **No Polling Overhead**: Dapr scheduler checks jobs every 1s (not querying database every 60s for `reminder_at` field)
- **High Accuracy**: ±1s typical latency (well within ±30s requirement from SC-005)
- **Pod Restart Recovery**: Jobs stored in Dapr State Store (PostgreSQL) - survive pod crashes and restarts
- **Automatic Retry**: Dapr retries failed webhook invocations (no manual retry logic needed)
- **Idempotency by Design**: Job name based on task_id - duplicate event processing overwrites existing job (only 1 reminder sent)
- **HTTP Webhook Invocation**: Notification Service exposes standard HTTP endpoint (easier to test than cron scripts)
- **Dapr Abstraction**: Scheduler configuration swappable via Dapr component YAML (future: use cloud-native schedulers like Azure Durable Entities)

### Negative

- **Alpha Feature**: Dapr Jobs API is alpha (Dapr 1.12+) with limited documentation and potential breaking changes in future versions
- **Learning Curve**: Engineers must understand Dapr Jobs API concepts (dueTime, repeats, job persistence) beyond Kubernetes CronJobs
- **State Store Dependency**: Requires Dapr State Store (PostgreSQL) for job persistence - adds infrastructure complexity
- **Webhook Timeout**: Dapr default webhook timeout 60s - if email sending takes >60s, job marked as failed (must handle async email sending)
- **Limited Community**: Fewer Stack Overflow answers, GitHub issues for Jobs API compared to Celery Beat or Kubernetes CronJobs
- **Debugging Complexity**: Two-hop architecture (Dapr scheduler → Dapr sidecar → webhook) makes tracing job failures harder

## Alternatives Considered

### Alternative A: Dapr Cron Bindings (Polling-Based)

**Components**:
- Dapr Cron Binding triggers Notification Service every 1 minute
- Service queries database: `SELECT * FROM tasks WHERE reminder_at <= NOW() AND reminder_sent = FALSE`
- Send reminders for matched tasks
- Update `reminder_sent = TRUE`

**Why rejected**:
- Fixed intervals only: Cannot schedule at specific timestamps (e.g., 4:00 PM), only intervals (every 1 minute, every 5 minutes)
- Higher latency: 1-minute polling interval = average 30s delay (violates ±30s accuracy if user creates reminder 59s before scheduled time)
- Wasted CPU: Queries database every minute even if no reminders due (99% of queries return empty result)
- No idempotency: Must manually track `reminder_sent` flag (race condition if service restarts mid-send)
- Not suitable for exact-time requirement: SC-005 requires ±30s accuracy - polling introduces unpredictable delays

### Alternative B: Celery Beat (Python Task Scheduler)

**Components**:
- Celery Beat scheduler with Redis backend
- Schedule reminder tasks at specific times
- Celery worker executes email sending task

**Why rejected**:
- Additional infrastructure: Requires Redis for task queue (increases operational complexity)
- No Dapr integration: Must use separate Celery library (loses Dapr abstraction benefits)
- Manual retry logic: Must implement exponential backoff manually (no built-in retry like Dapr)
- Python-specific: Not usable by frontend services (TypeScript/Node.js) if needed in future
- Higher resource usage: Celery Beat + Redis + Celery Worker = 3 additional components vs Dapr Jobs API (0 additional components)

### Alternative C: Kubernetes CronJobs

**Components**:
- Create Kubernetes CronJob for each reminder
- CronJob spec: `schedule: "0 16 31 12 *"` (4:00 PM on Dec 31)
- Job runs once at scheduled time
- Job container sends email and updates database

**Why rejected**:
- Kubernetes API overhead: Creating CronJob for every reminder = 100+ API calls/day (Kubernetes API rate limiting)
- Resource overhead: Each CronJob creates separate pod with startup time (~10s) - violates ±30s accuracy
- No idempotency: Must manually prevent duplicate job creation if event re-consumed
- Cleanup burden: Must delete completed CronJobs manually (Kubernetes doesn't auto-delete by default)
- Not portable: Kubernetes-specific (cannot run on non-Kubernetes platforms)

## References

- Feature Spec: [specs/007-phase5-cloud-deployment/spec.md](../../specs/007-phase5-cloud-deployment/spec.md) (Success Criterion SC-005: ±30s reminder accuracy)
- Implementation Plan: [specs/007-phase5-cloud-deployment/plan.md](../../specs/007-phase5-cloud-deployment/plan.md)
- Technical Research: [specs/007-phase5-cloud-deployment/research.md](../../specs/007-phase5-cloud-deployment/research.md) (Section 1.3: Scheduled Jobs)
- Dapr Jobs Component: [specs/007-phase5-cloud-deployment/contracts/jobs-scheduler.yaml](../../specs/007-phase5-cloud-deployment/contracts/jobs-scheduler.yaml)
- Related ADRs: ADR-0001 (Infrastructure Abstraction with Dapr - State Store for job persistence), ADR-0002 (Event-Driven Architecture - reminder.scheduled event)
- Dapr Jobs API Documentation: https://docs.dapr.io/developing-applications/building-blocks/jobs/jobs-overview/
- Clarifications: PHR-0002 Clarification #1 (UTC-only calculations - all reminder times in UTC)
