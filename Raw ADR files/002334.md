# ADR 0001: Architecture Decisions

**Date**: 2025-10-18  
**Author**: Aditya R.  
**Status**: Accepted

## Context

Building a secure task execution service (Kaiburr Task 1) requires careful technology selection and architectural decisions to ensure security, maintainability, and extensibility.

## Decisions

### 1. Spring Boot 3 Framework

**Decision**: Use Spring Boot 3.2.0 with Java 17

**Rationale**:
- Mature, production-ready framework with extensive ecosystem
- Built-in dependency injection and configuration management
- Excellent integration with MongoDB via Spring Data
- Native support for OpenAPI, Actuator, and Micrometer
- Java 17 provides modern language features and performance improvements

**Alternatives Considered**:
- Quarkus: Faster startup but less mature ecosystem
- Plain Java: Too much boilerplate
- Node.js: Less suitable for system command execution

### 2. MongoDB for Persistence

**Decision**: Use MongoDB as the primary database

**Rationale**:
- Flexible schema for task executions (variable-length outputs)
- Native support for embedded documents (TaskExecution within Task)
- Excellent indexing capabilities for name searches
- Easy horizontal scaling for future needs
- Spring Data MongoDB provides clean repository abstraction

**Alternatives Considered**:
- PostgreSQL: More rigid schema, overkill for this use case
- Redis: Not suitable for persistent storage
- Elasticsearch: Overkill for simple CRUD + search

### 3. No Shell Invocation

**Decision**: Execute commands directly via ProcessBuilder, never invoking `/bin/sh`, `cmd.exe`, or any shell

**Rationale**:
- **Security**: Eliminates entire class of command injection vulnerabilities
- Shell metacharacter expansion is disabled by default
- Direct binary execution is more predictable
- Simpler to validate and audit

**Implementation**:
```java
// GOOD: Direct execution
ProcessBuilder pb = new ProcessBuilder("echo", "hello");

// BAD: Shell invocation (NEVER USE)
ProcessBuilder pb = new ProcessBuilder("/bin/sh", "-c", "echo hello");
```

**Trade-offs**:
- Cannot use shell features like pipes, redirects, or glob expansion
- Must tokenize commands carefully
- More restrictive but far more secure

### 4. Policy-as-Data Validation

**Decision**: Store security policy in external YAML file (`config/command-policy.yaml`)

**Rationale**:
- **Flexibility**: Update policies without recompiling
- **Transparency**: Security rules are explicit and auditable
- **Extensibility**: Easy to add new rules or adjust limits
- **Hot-reload**: Can reload policy at runtime (future enhancement)

**Structure**:
- Limits (length, args, timeout, output sizes)
- Allowlist (permitted binaries)
- Denylist (forbidden tokens, metacharacters, sequences)
- Validation rules (character restrictions, quote handling)

**Alternatives Considered**:
- Hard-coded rules: Inflexible, requires recompilation
- Database storage: Overkill, adds complexity
- Annotations: Not suitable for runtime changes

### 5. Correlation ID Tracking

**Decision**: Implement correlation IDs via servlet filter

**Rationale**:
- **Traceability**: Track requests across logs, audit trail, and responses
- **Debugging**: Correlate frontend errors with backend logs
- **Auditing**: Link command executions to specific API calls
- Standard practice in microservices architectures

**Implementation**:
- `CorrelationIdFilter` intercepts all requests
- Generates UUID if `X-Correlation-Id` header not provided
- Stores in `MDC` (SLF4J Mapped Diagnostic Context)
- Returns in response header

### 6. Timeout and Output Limiting

**Decision**: Hard timeouts (5s) and output truncation (128 KiB stdout, 64 KiB stderr)

**Rationale**:
- **DoS Prevention**: Prevents long-running or fork-bomb attacks
- **Resource Protection**: Limits memory consumption
- **Predictability**: Execution time and resource usage are bounded

**Implementation**:
- `Process.waitFor(timeout, TimeUnit.SECONDS)`
- Asynchronous stream consumption with size limits
- Forced process termination on timeout
- Clear error messages when limits exceeded

### 7. CommandRunner Interface

**Decision**: Abstract command execution behind `CommandRunner` interface

**Rationale**:
- **Extensibility**: Easy to add Kubernetes, Docker, or AWS ECS runners
- **Testability**: Mock execution in unit tests
- **Profile-based Selection**: Spring profiles activate different implementations

**Current Implementations**:
- `LocalCommandRunner`: Default, executes on host system
- `KubernetesCommandRunner`: Stub (throws 501), placeholder for Task 2

**Future Implementations**:
- Kubernetes Jobs
- Docker containers
- AWS Lambda
- Azure Container Instances

### 8. Optimistic Locking

**Decision**: Use `@Version` annotation for concurrent update protection

**Rationale**:
- Prevents lost updates when multiple clients modify same task
- Lightweight compared to pessimistic locking
- MongoDB supports atomic version increments

**Implementation**:
```java
@Version
private Long version;
```

**Behavior**:
- Version incremented on each save
- `OptimisticLockingFailureException` thrown on conflict
- Client must fetch latest version and retry

### 9. Audit Logging

**Decision**: Write JSON-line audit logs to `audit.log.jsonl`

**Rationale**:
- **Compliance**: Record of all command executions
- **Forensics**: Investigate security incidents
- **Analysis**: Parse logs with standard tools (jq, ELK stack)
- **Non-repudiation**: Command hash prevents tampering claims

**Format**:
```json
{"timestamp":"...","correlationId":"...","taskId":"...","owner":"...","commandHash":"...","exitCode":0,"durationMs":142}
```

**Security**:
- Command stored as SHA-256 hash (first 16 chars)
- Full command stored in MongoDB for authorized retrieval
- File append-only (immutable audit trail)

### 10. Error Response Schema

**Decision**: Standardized error response with correlation ID

**Rationale**:
- **Consistency**: All errors follow same structure
- **Client-Friendly**: Predictable error parsing
- **Traceability**: Correlation ID links error to logs

**Schema**:
```json
{
  "timestamp": "2025-10-18T10:30:45.123Z",
  "status": 400,
  "error": "Bad Request",
  "message": "Command validation failed: ...",
  "path": "/api/tasks",
  "correlationId": "a1b2c3d4-..."
}
```

## Consequences

### Positive

- ✅ Strong security posture with defense-in-depth
- ✅ Clear separation of concerns
- ✅ Easy to test and maintain
- ✅ Ready for future enhancements (Kubernetes, Docker)
- ✅ Production-ready observability

### Negative

- ⚠️ Limited to allowlisted binaries (by design)
- ⚠️ Cannot use shell features (pipes, globs)
- ⚠️ Requires MongoDB (additional infrastructure)

### Neutral

- 🔄 Policy changes require restart (hot-reload not yet implemented)
- 🔄 Audit logs grow unbounded (rotation not yet implemented)

## References

- OWASP Command Injection Prevention Cheat Sheet
- Spring Security Best Practices
- Twelve-Factor App Methodology
- Google SRE Book (Observability patterns)

---

**Next**: See [ADR 0002: Extensibility](0002-extensibility.md) for future enhancements.
