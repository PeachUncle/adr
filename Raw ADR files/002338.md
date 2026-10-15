# ADR-0003: Kubernetes Job Runner for Command Execution

**Status:** Accepted  
**Date:** 2025-10-19  
**Author:** Aditya R

## Context

Task 2 requires offloading command execution from the application process to Kubernetes, maintaining the same REST API contract as Task 1. We must choose between:

1. **Kubernetes Jobs** — Batch workload, managed lifecycle, TTL cleanup
2. **Raw Pods** — Direct pod creation, manual cleanup required
3. **CronJobs** — Scheduled workload, not suitable for on-demand execution
4. **Deployments** — Long-running services, not suitable for one-time execution

## Decision

We will use **Kubernetes Jobs** for command execution.

## Rationale

### Why Jobs Over Pods

| Criteria | Jobs | Raw Pods |
|----------|------|----------|
| **Lifecycle Management** | ✅ Automatic restart policy, completion tracking | ❌ Manual state management |
| **TTL Cleanup** | ✅ `ttlSecondsAfterFinished` auto-deletes | ❌ Must implement manual cleanup |
| **Failure Handling** | ✅ `backoffLimit`, `activeDeadlineSeconds` | ❌ Manual retry logic |
| **API Semantics** | ✅ Designed for batch work | ❌ Designed for long-running services |
| **Auditability** | ✅ Job history, completion time in status | ❌ Pod GC removes history |

### Job Configuration

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: exec-<taskId>-<uuid>
  namespace: kaiburr
  labels:
    app: kaiburr-exec
    taskId: <taskId>
    execUuid: <uuid>
spec:
  ttlSecondsAfterFinished: 120      # Auto-cleanup after 2 minutes
  activeDeadlineSeconds: 15         # Kill if exceeds 15 seconds
  backoffLimit: 0                   # No retries (commands must be idempotent)
  template:
    spec:
      restartPolicy: Never
      serviceAccountName: kaiburr-runner
      containers:
      - name: executor
        image: kaiburr-executor:dev
        command: ["/usr/bin/echo"]
        args: ["hello"]
        resources:
          requests:
            cpu: "50m"
            memory: "64Mi"
          limits:
            cpu: "200m"
            memory: "128Mi"
        securityContext:
          runAsNonRoot: true
          runAsUser: 65532
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
          capabilities:
            drop: ["ALL"]
          seccompProfile:
            type: RuntimeDefault
```

### Execution Flow

1. **Validate Command** — `CommandValidator` checks policy
2. **Create Job** — `KubernetesCommandRunner` calls Kubernetes API
3. **Wait for Completion** — Poll Job status with timeout
4. **Fetch Logs** — Read stdout/stderr from Pod logs
5. **Persist Execution** — Save `TaskExecution` to MongoDB
6. **TTL Cleanup** — Kubernetes deletes Job after 120s

### Alternative Considered: Raw Pods

**Pros:**
- Slightly simpler API (no Job wrapper)
- Marginally faster creation

**Cons:**
- Must implement manual cleanup (watching pod phase, deleting)
- No built-in deadline/TTL semantics
- Lose Job history after pod deletion
- No restart policy management
- Harder to audit (pods disappear quickly)

**Rejected** because Jobs provide better lifecycle management and auditability.

## Consequences

### Positive

- Kubernetes handles lifecycle, retries, and cleanup
- TTL controller auto-deletes completed Jobs
- `activeDeadlineSeconds` enforces timeout without polling
- Job status provides clear completion/failure state
- Audit trail preserved until TTL expires

### Negative

- Extra API object (Job wraps Pod)
- Slightly higher resource overhead
- Must handle Job creation failures separately from execution failures

### Migration Path

If we need async execution later, we can:
- Return `202 Accepted` immediately after Job creation
- Add `GET /api/tasks/{id}/executions/{execUuid}` to poll status
- Store Job name in `TaskExecution` for tracking

## Implementation Notes

- Use label selectors `app=kaiburr-exec,execUuid=<uuid>` to find Pods
- Set `restartPolicy: Never` to avoid retries (commands may not be idempotent)
- Use `backoffLimit: 0` to fail fast
- Fetch logs only after Job completes (avoid partial logs)
- Handle `DeadlineExceeded` as timeout error

## References

- [Kubernetes Jobs Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [TTL Controller for Finished Resources](https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
