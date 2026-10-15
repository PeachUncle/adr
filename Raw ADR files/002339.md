# ADR-0005: Async Execution Option

**Status:** Accepted  
**Date:** 2025-10-19  
**Author:** Aditya R

## Context

Task 2 currently implements **synchronous execution**: the REST API blocks until the Kubernetes Job completes. This works for short commands (< 15s), but:

- Long-running commands may exceed HTTP client timeouts
- API server holds threads during execution
- No way to query execution status independently

We need an **optional async mode** for future extensibility.

## Decision

Add **config-driven async execution** behind `EXEC_ASYNC=true` environment variable.

## Architecture

### Synchronous Mode (default, `EXEC_ASYNC=false`)

```
Client → PUT /tasks/{id}/executions
           ↓
         API creates Job, waits for completion, fetches logs
           ↓
         Returns TaskExecutionResponse with full output
```

**Request:**
```http
PUT /api/tasks/task-001/executions
```

**Response (200 OK):**
```json
{
  "taskId": "task-001",
  "executionId": "exec-uuid-123",
  "exitCode": 0,
  "stdout": "Linux kaiburr 5.10.0",
  "stderr": "",
  "durationMs": 847,
  "timestamp": "2025-10-19T10:30:45.123Z"
}
```

### Asynchronous Mode (`EXEC_ASYNC=true`)

```
Client → PUT /tasks/{id}/executions
           ↓
         API creates Job, returns immediately
           ↓
         Returns 202 Accepted with execution ID
           
Client → GET /tasks/{id}/executions/{execId}  (poll)
           ↓
         API checks Job status, returns current state
```

**Request:**
```http
PUT /api/tasks/task-001/executions
```

**Response (202 Accepted):**
```json
{
  "taskId": "task-001",
  "executionId": "exec-uuid-123",
  "status": "RUNNING",
  "jobName": "exec-task-001-uuid-123",
  "startedAt": "2025-10-19T10:30:45.123Z",
  "links": {
    "self": "/api/tasks/task-001/executions/exec-uuid-123",
    "task": "/api/tasks/task-001"
  }
}
```

**Poll Request:**
```http
GET /api/tasks/task-001/executions/exec-uuid-123
```

**Response (200 OK) — Running:**
```json
{
  "taskId": "task-001",
  "executionId": "exec-uuid-123",
  "status": "RUNNING",
  "jobName": "exec-task-001-uuid-123",
  "startedAt": "2025-10-19T10:30:45.123Z",
  "elapsedMs": 1234
}
```

**Response (200 OK) — Complete:**
```json
{
  "taskId": "task-001",
  "executionId": "exec-uuid-123",
  "status": "SUCCEEDED",
  "exitCode": 0,
  "stdout": "Linux kaiburr 5.10.0",
  "stderr": "",
  "durationMs": 2345,
  "startedAt": "2025-10-19T10:30:45.123Z",
  "completedAt": "2025-10-19T10:30:47.468Z"
}
```

## Implementation

### Domain Model Extension

```java
public class TaskExecution {
    private String id;              // UUID
    private String jobName;         // K8s Job name
    private ExecutionStatus status; // PENDING, RUNNING, SUCCEEDED, FAILED, TIMEOUT
    private Instant startedAt;
    private Instant completedAt;
    private Integer exitCode;
    private String stdout;
    private String stderr;
    private Long durationMs;
}

public enum ExecutionStatus {
    PENDING,    // Job created, not yet scheduled
    RUNNING,    // Pod running
    SUCCEEDED,  // Exit code 0
    FAILED,     // Exit code != 0
    TIMEOUT     // activeDeadlineSeconds exceeded
}
```

### Controller Endpoints

```java
@RestController
@RequestMapping("/api/tasks")
public class TaskController {
    
    @Value("${exec.async:false}")
    private boolean asyncExecution;
    
    @PutMapping("/{id}/executions")
    public ResponseEntity<?> executeTask(@PathVariable String id) {
        if (asyncExecution) {
            TaskExecution execution = taskService.startExecutionAsync(id);
            return ResponseEntity.accepted()
                .location(URI.create("/api/tasks/" + id + "/executions/" + execution.getId()))
                .body(execution);
        } else {
            TaskExecution execution = taskService.executeTask(id);
            return ResponseEntity.ok(execution);
        }
    }
    
    @GetMapping("/{id}/executions/{execId}")
    public ResponseEntity<TaskExecution> getExecution(
            @PathVariable String id,
            @PathVariable String execId) {
        return taskService.getExecution(id, execId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
```

### Service Layer

```java
@Service
public class TaskService {
    
    @Value("${exec.async:false}")
    private boolean asyncExecution;
    
    public TaskExecution startExecutionAsync(String taskId) {
        Task task = taskRepository.findById(taskId)
            .orElseThrow(() -> new TaskNotFoundException(taskId));
        
        // Create execution record
        TaskExecution execution = new TaskExecution();
        execution.setId(UUID.randomUUID().toString());
        execution.setStatus(ExecutionStatus.PENDING);
        execution.setStartedAt(Instant.now());
        
        // Create Job (non-blocking)
        String jobName = commandRunner.createJobAsync(task, execution.getId());
        execution.setJobName(jobName);
        
        // Save immediately
        task.getExecutions().add(execution);
        taskRepository.save(task);
        
        // Schedule background status updater
        scheduleStatusUpdater(taskId, execution.getId());
        
        return execution;
    }
    
    private void scheduleStatusUpdater(String taskId, String execId) {
        scheduler.scheduleWithFixedDelay(() -> {
            updateExecutionStatus(taskId, execId);
        }, 1, 2, TimeUnit.SECONDS);
    }
    
    private void updateExecutionStatus(String taskId, String execId) {
        Task task = taskRepository.findById(taskId).orElse(null);
        if (task == null) return;
        
        TaskExecution execution = task.getExecutions().stream()
            .filter(e -> e.getId().equals(execId))
            .findFirst()
            .orElse(null);
        
        if (execution == null || execution.getStatus().isTerminal()) {
            return; // Cancel polling
        }
        
        // Check Job status
        ExecutionResult result = commandRunner.getExecutionStatus(execution.getJobName());
        execution.setStatus(result.getStatus());
        
        if (result.isComplete()) {
            execution.setExitCode(result.getExitCode());
            execution.setStdout(result.getStdout());
            execution.setStderr(result.getStderr());
            execution.setCompletedAt(Instant.now());
            execution.setDurationMs(
                Duration.between(execution.getStartedAt(), execution.getCompletedAt()).toMillis()
            );
        }
        
        taskRepository.save(task);
    }
}
```

## Alternatives Considered

### Option 1: Always Async (No Config)

**Pros:**
- Consistent API behavior
- Better scalability

**Cons:**
- Breaking change from Task 1 contract
- More complex client code (polling loop)
- Higher latency for simple commands

**Rejected** — breaks Task 1 compatibility.

### Option 2: Separate Endpoints

```
POST /api/tasks/{id}/executions/sync    → 200 OK with output
POST /api/tasks/{id}/executions/async   → 202 Accepted with execId
```

**Pros:**
- Explicit client choice
- Both modes always available

**Cons:**
- API surface duplication
- Confusing for users

**Rejected** — prefer config-driven behavior.

### Option 3: Async via Query Param

```
PUT /api/tasks/{id}/executions?async=true
```

**Pros:**
- Per-request control
- No config needed

**Cons:**
- Stateless API harder to implement (who polls?)
- Client must manage mode per request

**Deferred** — could add later.

## Consequences

### Positive

- Supports long-running commands
- Reduces API server thread contention
- Client can poll at their own pace
- Easy to enable/disable via config

### Negative

- More complex implementation (background polling, state management)
- Clients must implement polling logic
- Execution state must be persisted before completion
- Potential race conditions in status updater

### Migration Path

1. **Phase 1 (Current):** Sync-only, simple blocking API
2. **Phase 2 (Future):** Add async mode behind flag
3. **Phase 3 (Optional):** Support both modes simultaneously via query param

## Testing Strategy

### Unit Tests

- Sync mode returns complete execution
- Async mode returns pending execution with 202
- Polling endpoint returns correct status
- Status updater transitions states correctly

### Integration Tests

```java
@Test
public void testAsyncExecution() throws Exception {
    // Create task
    Task task = createTask("echo", List.of("hello"));
    
    // Start async execution
    MvcResult result = mockMvc.perform(put("/api/tasks/" + task.getId() + "/executions"))
        .andExpect(status().isAccepted())
        .andReturn();
    
    TaskExecution execution = objectMapper.readValue(
        result.getResponse().getContentAsString(),
        TaskExecution.class
    );
    
    assertThat(execution.getStatus()).isEqualTo(ExecutionStatus.PENDING);
    
    // Poll until complete
    await().atMost(30, TimeUnit.SECONDS).until(() -> {
        TaskExecution current = getExecution(task.getId(), execution.getId());
        return current.getStatus() == ExecutionStatus.SUCCEEDED;
    });
    
    // Verify final state
    TaskExecution completed = getExecution(task.getId(), execution.getId());
    assertThat(completed.getExitCode()).isEqualTo(0);
    assertThat(completed.getStdout()).contains("hello");
}
```

## Configuration

```yaml
# application.yml
exec:
  async: ${EXEC_ASYNC:false}  # Default sync for Task 1 compatibility
  poll-interval-seconds: 2
  max-poll-duration-seconds: 300
```

## References

- [HTTP 202 Accepted](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/202)
- [Kubernetes Job Status](https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/job-v1/#JobStatus)
- [Spring @Async and Task Scheduling](https://spring.io/guides/gs/async-method/)
