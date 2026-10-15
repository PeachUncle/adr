# ADR 0004 — Two-Phase Job Enqueue with Database Persistence

### ADR Details

Title: "Two-Phase Job Enqueue with Database Persistence" Number: 0004
(following existing sequence) 
Status: Accepted Date: 2025-11-04 
Tags: #adr #architecture #database #queue #persistence #error-handling

### Context

Problem Statement:

• Original system used queue-only approach for transcription job management
• No persistent record of transcription requests
• Queue failures could result in lost requests
• No audit trail or status history
• Inconsistent state between queue and any potential database records

Forces Driving Decision:

• Need for reliable job tracking across service restarts
• Requirement for audit trail of all transcription requests
• Prevention of orphaned jobs or database records
• Maintaining API compatibility while adding persistence
• Error handling for both database and queue failures

### Decision

Two-Phase Commit Pattern:

1. Phase 1: Create database record with 'pending' status
2. Phase 2: Enqueue job using database ID as identifier
3. Phase 3: Update database status to 'queued' after successful enqueue
4. Cleanup: Mark database record as 'failed' if any phase fails

Status Flow:

'pending' → 'queued' → 'processing' → 'done'/'failed'

### Rationale

Why Two-Phase Commit:

• Atomicity: Ensures both database record and job exist, or neither
• Consistency: Prevents orphaned records or jobs
• Audit Trail: Complete history of request lifecycle
• Error Recovery: Failed attempts are tracked and can be cleaned up
• Debugging: Clear visibility into system state at each phase

Alternatives Considered:

1. Database-First Only:
 • ✅ Simple implementation
 • ❌ Queue failures create orphaned records
2. Queue-First Only:
 • ✅ No orphaned database records
 • ❌ No persistence if queue succeeds but database fails
3. Parallel Operations:
 • ✅ Potentially faster
 • ❌ Complex transaction management and race conditions


### Consequences

Benefits:

• Reliability: No lost transcription requests
• Transparency: Clear status tracking throughout lifecycle
• Recovery: Can identify and retry failed operations
• Monitoring: Better observability of system health
• Scalability: Foundation for future enhancements

Trade-offs:

• Complexity: More moving parts than queue-only approach
• Latency: Additional database operations add slight overhead
• Dependencies: Both database and queue must be operational

### Implementation Details

Controller Integration:

// Phase 1: Create pending record
transcriptionRepository.create({...status: 'pending'});

// Phase 2: Enqueue job
await transcriptionQueue.add(transcriptionId, {...});

// Phase 3: Update to queued
transcriptionRepository.updateStatus(transcriptionId, 'queued');

Error Handling:

• Database failures: No job enqueued, client gets 500 error
• Queue failures: Database record marked as 'failed', client gets 500 error
• Cleanup logic prevents orphaned records

### Future Evolution

Potential Enhancements:

• Background cleanup jobs for old 'failed' records
• Retry mechanisms for 'pending' records
• Metrics and monitoring on status transitions
• Transaction support for complex operations
• Database migrations for additional metadata

Triggers for Re-evaluation:

• Performance bottlenecks from database operations
• Need for distributed transactions
• Changes in queue technology or architecture

### Related ADRs

• ADR 0001 /0001%E2%80%91database%E2%80%91location.md - Database location
decision
• ADR 0002 /0002%E2%80%91decoupling%E2%80%91database%E2%80%91access.md -
Repository pattern implementation
• ADR 0005 /0005-service-failure-recovery.md - Service failure recovery and data consistency
• ADR 0006 /0006-audio-file-retention-strategy.md - Configurable audio file retention strategy

This ADR documents the critical architectural decision that ensures reliable
job processing and data persistence while maintaining system consistency and
error resilience.