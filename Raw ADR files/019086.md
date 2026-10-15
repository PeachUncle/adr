# ADR-008: Snapshot Strategy for Event Sourcing

## Status

Accepted

## Context

The platform uses Event Sourcing with Neon Postgres as the canonical event store. Rebuilding aggregates by replaying their entire event stream can become slow when aggregates accumulate many events. We need an operationally simple, consistent snapshot strategy to improve aggregate rehydration performance while preserving correctness and replayability.

## Decision

- **Snapshot frequency:** Create a snapshot **every 100 events per aggregate**.
- **Storage location:** Store snapshots in the **same Postgres database** as the event store (Neon), in a dedicated `snapshots` table.
- **Snapshot contents:** Each snapshot record will include:
  - `aggregate_id` (string)
  - `aggregate_type` (string)
  - `last_event_version` (integer) — the version number of the last event applied to the snapshot
  - `state` (JSONB) — serialized aggregate state
  - `snapshot_version` (integer) — schema version of the snapshot payload
  - `created_at` (timestamptz)
  - optional `metadata` (JSONB)
- **Snapshot creation trigger:** After appending events to an aggregate, if the aggregate's current event count since the last snapshot >= 100, create or replace the snapshot for that aggregate in the same DB transaction or in an immediately-following transaction that ensures eventual consistency of the snapshot.
- **Snapshot read path:** On aggregate load:
  1. Query the `snapshots` table for the latest snapshot for the aggregate (by `aggregate_id` and `aggregate_type`).
  2. If found, rehydrate aggregate from snapshot state and replay subsequent events with sequence > `last_event_version`.
  3. If no snapshot found, replay from event stream from sequence 1.
- **Schema evolution for snapshots:** Each snapshot has a `snapshot_version`. If a snapshot's version is older than the current aggregate schema version, the application layer must run a deterministic **migration/upgrade function** to convert the snapshot into the current shape before rehydration. If migration is not possible, fallback to full replay from events.
- **Consistency guarantees:** Events remain the source of truth. Snapshots are an optimization. If a snapshot is missing or corrupt, the system must be able to rebuild state by replaying events.
- **Idempotency and replacement:** Snapshot writes are idempotent for an aggregate: creating a new snapshot replaces the previous snapshot for that `aggregate_id` and `aggregate_type` (based on `last_event_version`).
- **Tooling & maintenance:** Add tooling for:
  - Snapshot inspection and deletion for debugging/operations.
  - Rebuilding snapshots (recompute by replaying events and writing a new snapshot) as an offline/maintenance job.
  - Monitoring snapshot age and size, and metrics for snapshot hit/miss rate on aggregate loads.

## Rationale

- Choosing **every 100 events** is a pragmatic default: it reduces replay cost significantly for high-activity aggregates while keeping snapshot storage modest. This threshold can be tuned per aggregate type if needed.
- Storing snapshots in the **same DB** simplifies transactions and reduces operational complexity; it also ensures backups can capture both events and snapshots together.
- Snapshot versioning and upgrade functions allow safe schema evolution while keeping domain logic isolated from infra concerns.

## Consequences

- Developers must implement snapshot creation logic in the application/infrastructure layer; domain logic remains unaware of snapshot mechanics.
- CI and testing must include snapshot migration tests to ensure upgrades succeed across snapshot versions.
- Backups must include the snapshots table to ensure disaster recovery can use snapshots if desired.
- Projections and other read-side components are unaffected; snapshots only impact aggregate rehydration on the write side.

## Implementation Notes

- Recommended Postgres table schema (example):

```sql
CREATE TABLE snapshots (
  aggregate_type TEXT NOT NULL,
  aggregate_id TEXT NOT NULL,
  last_event_version INT NOT NULL,
  snapshot_version INT NOT NULL DEFAULT 1,
  state JSONB NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (aggregate_type, aggregate_id)
);
```

- Example load flow (pseudocode):

```text
function loadAggregate(aggregateType, aggregateId):
  snapshot = snapshots_repo.fetch_latest(aggregateType, aggregateId)
  if snapshot:
    aggregate = deserialize(snapshot.state)
    events = event_store.fetch_events_after(aggregateId, snapshot.last_event_version)
  else:
    aggregate = aggregateFactory.createEmpty()
    events = event_store.fetch_all_events(aggregateId)
  for event in events:
    aggregate.apply(event)
  return aggregate
```

- Example save flow (pseudocode):

```text
function saveAggregate(aggregate):
  events = aggregate.getUncommittedEvents()
  event_store.append(aggregate.streamId, events, expectedVersion=aggregate.version)
  if shouldSnapshot(aggregate):  // e.g., events_since_last_snapshot >= 100
    snapshot = aggregate.serializeState()
    snapshots_repo.upsert(aggregate.type, aggregate.id, aggregate.version, snapshot)
```

- `shouldSnapshot` default implementation:
  - Track `last_snapshot_version` per aggregate (from snapshots table).
  - If `aggregate.version - last_snapshot_version >= 100`, return true.

## Next Steps

1. Add `snapshots` table schema to the infra Terraform/Postgres migrations.
2. Implement snapshot repository adapter (Postgres JSONB) in the infra layer for services that manage aggregates.
3. Add unit tests and integration tests that verify snapshot creation, loading, and migration paths.
4. Provide admin tooling to list, delete, and rebuild snapshots for maintenance.
