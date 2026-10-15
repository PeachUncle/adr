# Event Sourcing Architecture

## Purpose
This document records the decision to use event sourcing as the foundational data persistence pattern for Bartleby.

## Classification
- **Domain:** Architecture
- **Stability:** Static
- **Abstraction:** Structural
- **Confidence:** Established

## Content

### Context

Bartleby needs to provide:
1. Complete audit trail of all changes (for authors to understand evolution of their work)
2. Potential undo/redo functionality
3. Foundation for future collaboration features
4. Data integrity and recoverability

Traditional CRUD with update-in-place would lose history and make undo/collaboration difficult. The question was how to maintain history without adding significant complexity.

### Decision

**Adopt event sourcing with materialized views:**

- All state changes are recorded as immutable events in an append-only log
- Current state is derived by replaying events
- Materialized views (tables for cards, links, config) provide fast querying
- The event log is the single source of truth

### Status

Accepted

### Consequences

**Positive:**
- Complete audit trail of all changes with timestamps
- Can rebuild state by replaying events from any point
- Natural foundation for undo/redo (replay to previous state)
- Enables future event streaming for collaboration
- Data corruption recoverable (rebuild views from events)
- Easier debugging (can see exact sequence of operations)

**Negative:**
- Increased storage (events + materialized views)
- Additional complexity in write path (append event + update views)
- Event schema evolution requires migration strategy
- Potential performance overhead for long event logs

**Risks:**
- Event log growing too large over time (mitigated by periodic snapshots)
- Event replay becoming slow (mitigated by keeping views up-to-date)
- Schema changes requiring backfills (mitigated by versioning events)

**Trade-offs:**
- Storage space for audit trail and flexibility
- Write complexity for complete history
- Developer complexity for data integrity and recoverability

### Alternatives Considered

#### Alternative 1: Traditional CRUD with Audit Log

Separate audit/history tables tracking changes.

**Pros:**
- Simpler implementation
- Familiar pattern
- Less storage overhead

**Cons:**
- History tracking often incomplete or inconsistent
- Undo/redo requires custom logic per entity type
- Audit log separate from operational data (can diverge)
- No natural foundation for event streaming

#### Alternative 2: Append-Only Tables with Soft Deletes

Mark rows as deleted rather than removing them.

**Pros:**
- Simple to implement
- Preserves some history
- Still works with standard SQL queries

**Cons:**
- Only captures final state, not intermediate changes
- Loses fine-grained history (multiple edits to same field)
- Doesn't support undo beyond last change
- Query complexity increases (always filter deleted rows)

#### Alternative 3: Version Control System (Git-like)

Store snapshots of entire database at commit points.

**Pros:**
- Very familiar pattern for developers
- Rich diffing and merging capabilities
- Works well for text content

**Cons:**
- Overkill for structured data
- Requires learning git concepts
- Merge conflicts on concurrent edits
- Not optimized for real-time queries

### Implementation Notes

1. **Event Store:** Single `events` table with columns: id, timestamp, type, payload (JSON)

2. **Materialized Views:** Standard SQL tables (cards, links, config) updated synchronously after event append

3. **Event Replay:** On startup or corruption detection, can rebuild views by replaying all events in order

4. **Event Types:**
   - card.created, card.updated, card.deleted, card.moved
   - link.created, link.updated, link.deleted
   - config.updated

5. **Event Payload:** JSON containing all data needed to apply the change (e.g., for card.created: cardId, title, content, cardType, etc.)

6. **Future Optimizations:**
   - Snapshot every N events for faster replay
   - Archive old events (keep last N + periodic snapshots)
   - Async view updates for non-critical reads

## Relationships
- **Parent Nodes:** [foundation/principles.md]
- **Child Nodes:** None
- **Related Nodes:**
  - [data-model/overview.md] - implements - Data model uses event sourcing
  - [api-server/overview.md] - implements - API creates and processes events
  - [002-sqlite-database.md] - complements - SQLite stores both events and views

## Navigation Guidance
- **Access Context:** Reference when implementing persistence, debugging data issues, or planning undo/redo
- **Common Next Steps:** Review data model, API implementation patterns
- **Related Tasks:** Database schema design, event handler implementation, view rebuilding
- **Update Patterns:** Revisit if event log performance becomes problematic or storage constraints appear

## Metadata
- **Decision Number:** 001
- **Created:** 2025-11-14
- **Last Updated:** 2025-11-14
- **Updated By:** AI Agent (Claude)
- **Deciders:** Development team based on project requirements

## Change History
- 2025-11-14: Initial decision record created
