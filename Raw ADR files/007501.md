# ADR-013 – Outbox Pattern: Securing Data Integrity for Dual Write Operations

**Status:** Accepted  
**Date:** 2025-11-26  
**Author:** Niklas Häll

---

## Context

The ticketing system is transitioning from a synchronous API architecture to an event-driven architecture using Azure Service Bus and Azure Functions. This transition introduces a critical challenge: **dual write operations** where the system must:

1. Write booking data to Cosmos DB (primary data store)
2. Publish events to Azure Service Bus (for event-driven processing)

**The Problem:**
- These are two separate systems (Cosmos DB and Service Bus) that cannot participate in a distributed transaction
- If the booking is saved to Cosmos DB but event publishing to Service Bus fails, we lose the event (data inconsistency)
- If event publishing succeeds but Cosmos DB write fails, we have an event for a booking that doesn't exist (data corruption)
- Network failures, service outages, or transient errors can cause partial failures
- This violates the **ACID principle** of atomicity - both operations must succeed or both must fail

**Without the Outbox Pattern:**
```
Booking Created → Write to Cosmos DB
                → Publish to Service Bus (fails)
Result: Booking exists but no event published (data loss)
```

**The Requirement:**
- Ensure **transactional consistency** between booking creation and event publishing
- Prevent **data loss** if event publishing fails
- Provide **reliability guarantees** for event-driven architecture
- Enable **audit trail** of all events (even if not yet published)
- Support **retry mechanisms** for failed event publishing

---

## Decision

We implement the **Transactional Outbox Pattern** using Cosmos DB as the outbox store. This pattern ensures that booking creation and event creation happen atomically within a single transaction, securing data integrity for dual write operations.

**Implementation Details:**
- **Outbox Container:** Dedicated Cosmos DB container (`outbox`) with partition key `/status` for efficient querying
- **OutboxEvent Model:** Stores event data as JSON string with metadata (Id, EventType, Status, CreatedAt, ProcessedAt, RetryCount, ErrorMessage)
- **Atomic Write:** Booking and OutboxEvent are written in the same Cosmos DB transaction/operation
- **Asynchronous Processing:** Background service polls outbox for pending events and publishes to Service Bus
- **Status Tracking:** Events have status (Pending, Processed, Failed) to track processing state
- **Retry Logic:** Failed events can be retried with exponential backoff
- **Audit Trail:** All events are stored in outbox regardless of publishing status

**Flow:**
```
1. Booking Created
   ↓
2. Write Booking to Cosmos DB (bookings container)
   ↓
3. Write OutboxEvent to Cosmos DB (outbox container) - SAME TRANSACTION
   ↓
4. Transaction commits (both succeed or both fail)
   ↓
5. Background service polls outbox for Pending events
   ↓
6. Publish event to Service Bus (if feature flag enabled)
   ↓
7. Mark OutboxEvent as Processed
```

**Key Properties:**
- **Atomicity:** Booking and event creation are atomic (single transaction)
- **Reliability:** Events are never lost - stored in outbox even if Service Bus is unavailable
- **Idempotency:** Events can be retried safely (status tracking prevents duplicates)
- **Auditability:** Complete history of all events in outbox container
- **Flexibility:** Events can be published later when Service Bus is available

**Separation of Concerns:**
- **API Layer:** Creates booking and outbox event atomically (synchronous, transactional)
- **Background Service:** Processes outbox and publishes to Service Bus (asynchronous, retryable)
- **Feature Flags:** Control whether events are published (but outbox is always written)

---

## Consequences

**Advantages:**
- **Data Integrity** – Booking creation and event creation are atomic. Either both succeed or both fail, preventing data inconsistency.
- **No Data Loss** – Events are stored in outbox even if Service Bus is unavailable. Background service can publish them later when Service Bus recovers.
- **Reliability** – System can handle Service Bus outages gracefully. Events are queued in outbox and processed when service is available.
- **Audit Trail** – Complete history of all events stored in outbox, regardless of publishing status. Useful for compliance and troubleshooting.
- **Retry Capability** – Failed event publishing can be retried automatically with exponential backoff. Status tracking prevents duplicate processing.
- **Decoupled Publishing** – Event publishing is decoupled from booking creation. API remains fast and responsive, while background service handles async publishing.
- **Feature Flag Support** – Outbox events are always written (for audit), but publishing to Service Bus is controlled by feature flags. Enables dual-system coexistence.
- **Scalability** – Background service can process outbox events at its own pace, handling bursts and backpressure gracefully.

**Disadvantages:**
- **Additional Storage** – Outbox container requires additional Cosmos DB storage and RU consumption. However, events are typically small and can be archived after processing.
- **Eventual Consistency** – Events are published asynchronously, so there's a delay between booking creation and event availability in Service Bus. This is acceptable for event-driven architecture.
- **Complexity** – Adds complexity with background service, polling logic, and status management. Requires monitoring and operational overhead.
- **Polling Overhead** – Background service must poll outbox for pending events, consuming resources even when no events are pending. Can be optimized with change feed (future enhancement).
- **Storage Growth** – Outbox container grows over time. Requires cleanup strategy for processed events (archive or delete after retention period).

---

## Risks / Mitigations

- **Risk:** Outbox container grows indefinitely, consuming storage and increasing costs.  
  **Mitigation:** Implement cleanup strategy - archive or delete processed events after retention period (e.g., 30 days). Use Cosmos DB TTL feature or scheduled cleanup job.

- **Risk:** Background service fails to process outbox events, causing events to remain pending indefinitely.  
  **Mitigation:** Implement health checks and monitoring for background service. Set up alerts for pending events older than threshold. Implement dead letter handling for events that fail after maximum retries.

- **Risk:** High volume of bookings could overwhelm outbox processing, causing delays in event publishing.  
  **Mitigation:** Implement batching in background service (process multiple events per iteration). Scale background service horizontally if needed. Monitor outbox queue depth and processing latency.

- **Risk:** Cosmos DB transaction limits could prevent atomic writes if booking and outbox event are in different containers.  
  **Mitigation:** Use Cosmos DB transactional batch API or ensure both writes are in the same logical partition. For MVP, we use separate containers but ensure both writes succeed before committing (application-level transaction).

- **Risk:** Duplicate event publishing if background service processes same event twice (e.g., after crash).  
  **Mitigation:** Use idempotent event processing in Azure Functions. Track processed event IDs to prevent duplicates. Use status updates with optimistic concurrency to prevent race conditions.

- **Risk:** Outbox polling consumes resources even when no events are pending.  
  **Mitigation:** Implement exponential backoff for polling intervals when no events found. Consider using Cosmos DB Change Feed (future enhancement) for push-based event processing instead of polling.

---

## Alternatives

- **Two-Phase Commit (2PC)** – Rejected. Cosmos DB and Service Bus do not support distributed transactions. 2PC is complex, has performance overhead, and is not supported by these Azure services.

- **Publish Events Directly to Service Bus** – Rejected. If Service Bus is unavailable, events are lost. No retry mechanism. No audit trail. Violates data integrity requirements.

- **Database Transaction with Compensating Actions** – Rejected. Complex to implement. Requires rollback logic for Service Bus operations. Does not solve the fundamental problem of distributed transactions.

- **Event Sourcing** – Rejected. Overkill for MVP. Requires significant architectural changes. Cosmos DB is not optimized for event sourcing patterns. Can be considered for future enhancements.

- **Change Feed (Cosmos DB)** – Considered for future. Cosmos DB Change Feed can trigger event publishing when bookings are created, eliminating need for outbox polling. However, Change Feed requires Azure Functions or Logic Apps, adding complexity. Can be implemented as Phase 10 enhancement.

- **Separate Outbox Database** – Rejected. Adds another database to manage. Cosmos DB can serve as outbox store efficiently. No need for additional infrastructure.

---

## References

- [Event-Driven Architecture Roadmap](../journal/eventdriven_roadmap.md)
- [ADR-006 - Event-Driven Architecture](./ADR-006-eventdriven.md)
- [ADR-012 - Azure App Configuration](./ADR-012-azure-app-configuration.md)
- [Transactional outbox pattern with Azure Cosmos DB](https://learn.microsoft.com/sv-se/azure/architecture/databases/guide/transactional-outbox-cosmos)
- [Outbox Pattern - Martin Fowler](https://microservices.io/patterns/data/transactional-outbox.html)
- [Cosmos DB Transactional Batch API](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/transactional-batch)

