# Infrastructure Stack for Task Execution (Redis + Celery)

- Status: accepted
- Date: 2025-05-28
- Tags: infrastructure, celery, redis, task orchestration, mvp, asynchronous execution

## Context

To ensure reliable asynchronous execution of tasks across modules in the SPLit MVP, we adopt a task orchestration stack based on Redis and Celery. This approach offers modularity, independent task processing, scalability, and fault tolerance with minimal overhead.

MySQL and the ORM layer (Peewee) are covered in separate ADRs. This document outlines the remaining infrastructure components needed to support task execution.

## Decision

### Components to Deploy

1. **Redis (Docker container)**  
   Serves as the message broker and task queue backend for Celery.  
   Runs with a basic configuration (port 6379, no password in dev environment).  

   In production, Redis must be secured with a password and network-level restrictions. Persistence should also be enabled to avoid task loss during unexpected shutdowns. Redis supports two persistence modes:

   - **RDB (snapshotting)**: Periodically saves a snapshot of the data to disk. Can lead to data loss if Redis crashes between snapshots.
   - **AOF (append-only file)**: Logs each write operation to disk immediately. Provides better durability, especially in `always` or `everysec` modes.

   In SPLit, task loss in Redis is not critical due to comprehensive logging in `eventSrv`. Still, AOF is recommended in production to minimize discrepancies.

2. **Celery Workers (Docker containers)**  
   Each worker is dedicated to a specific Redis queue, allowing separation by module and task type. This supports better scalability, isolation, and monitoring.

   At MVP level, three queues and corresponding workers are required:
   - `yahoo_tasks` → for `yahooAPIGateway`
   - `init_filter_tasks` → for `initlFilter`
   - `final_sel_tasks` → for `finalSel`

   Workers are defined as separate services in `docker-compose.yml`. This architecture allows:
   - Independent scaling of specific processing stages
   - Isolated error tracking and performance tuning
   - Easier debugging and support

   Local worker execution (via `celery -A ... worker --queues=...`) is allowed for development only and should not be the default mode.

3. **Celery App**  
   Defines the broker config, queue routing, and application-specific settings.  
   Typically initialized in `src/celery_app.py`.

4. **eventSrv**  
   Handles system-wide task lifecycle logging via events from three sources:

   1. **Task initiators** (e.g., `portfolioMngr`, `dataOrchestrator`) send `task_created` events with:
      - task type,
      - initiator ID,
      - tickers list,
      - session ID,
      - timestamp,
      - target module.

   2. **Celery Workers** send system-level events (`task_started`, `task_succeeded`, `task_failed`, `task_retried`) via Celery’s built-in signals (`task_postrun`, `task_failure`, `after_task_publish`) or explicit calls from within tasks. This ensures even failed or interrupted tasks are logged.

   3. **Task executors** may (optionally) emit `task_business_result` events with domain-specific context (e.g., number of records processed, validation errors).

   This tri-source approach enables complete task traceability, supporting recovery even if Redis or Celery fail mid-process.

5. **logSrv**  
   Responsible for technical logging into `split_logs`.  
   Supports debugging, auditing, and forensic diagnostics by capturing detailed traces of system activity. Runs silently in the background, separate from the task processing flow.

### Interaction Flow

- Tasks are dispatched between modules via Redis.
- Initiating modules (e.g., `portfolioMngr`, `dataOrchestrator`) use Celery APIs (`send_task`, `apply_async`) to enqueue tasks.
- Executor modules subscribe to their respective queues and implement Celery task handlers.
- `eventSrv` and `logSrv` receive signals from Celery Workers or explicit calls (`notify_task_status(...)`) inside the task code.

### Celery Result Backend

SPLit does not rely on Celery's `result_backend` to retrieve return values or task outcomes. All essential task states are tracked via `eventSrv`, and final results are persisted in MySQL.

Nonetheless, to ensure proper signal handling (`task_postrun`, `task_failure`, etc.), it is recommended to configure `result_backend` as `rpc://` or `redis://` — even if return values are not used directly.

### Error Handling and Retries

SPLit uses Celery’s built-in retry mechanisms (`task.retry()`, `autoretry_for`) to gracefully recover from transient failures (e.g., network hiccups, rate limits).

Each retry attempt emits a `task_retried` signal and is logged in `eventSrv` with status `RETRY`. This enables detailed analysis of system resilience and retry patterns.

Consider storing a `retry_count` or `attempt` field in the event payload or log entry for future observability.

### Task Statuses

To track the lifecycle of a task in `split_events.events_log.status`, the following statuses are used:

- `PENDING`: Task has been created but not queued
- `QUEUED`: Task submitted to Redis/Celery
- `RECEIVED`: Worker received the task
- `PROCESSING`: Task is executing (used for long-running operations)
- `SUCCESS`: Task completed successfully
- `FAILURE`: Task raised an exception
- `RETRY`: Task is being re-executed
- `CANCELLED`: Task was manually or systemically cancelled
- `TIMEOUT`: Task exceeded its allowed duration
- `NO_DATA`: Task executed but no action was necessary (e.g., data already current)

The `PROCESSING` status should be set explicitly inside long-running tasks to indicate active computation.

## Consequences

- ⚠️ Monitoring of queues and workers is **not included in the MVP**, but the SPLit architecture anticipates future observability tools. Tools like Flower, Prometheus, or Grafana can be integrated later to support system health and performance tracking.
- ⚠️ All tasks **must be idempotent** — repeated execution with the same parameters must not cause duplicate data or inconsistent state. This is essential for safe retries and recovery based on `eventSrv` logs.
- ✅ Modules can be developed and tested independently by adhering to queue naming and task contracts.
- ✅ Task loss in Redis does not lead to unrecoverable states, since `eventSrv` acts as a durable event journal.
- ✅ It is feasible to implement automated recovery of failed or incomplete tasks using `split_events` logs.

## Links

- [Initial Module Set for the MVP](20250528-initial-module-set-for-the-mvp.md)
- [Limit initial MySQL schema to five core databases](20250527-limit-initial-mysql-schema-to-five-core-databases.md)
- [Logger Module Description](20250525-logger-module-description.md)
