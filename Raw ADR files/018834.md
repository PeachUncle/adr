# ADR: Redesign of EventBridge Event Publishing

- **Date**: 2025-12-18
- **Status**: Approved
- **Deciders**: Akira Suenami, Daichi Miyazaki

## Context

Currently, EventBridge event publishing is implemented in `PublishEvents::PublishService`. This service is called from the following locations:

- `Users::UpdateService` (currently unused)
- `Users::DestroyService`
- `Users::EmailChangeService`
- `DeliveryAddresses::CreateService`
- `DeliveryAddresses::UpdateService`

However, the following issues exist:

1. Since `Users::UpdateService` was replaced by `UserForm`, events are no longer published when profiles are updated
2. The event format does not follow standard specifications such as CloudEvents
3. There is no versioning mechanism

## Decision

### 1. Create a new implementation without modifying the existing PublishService

Leave the existing `PublishEvents::PublishService` unchanged, create a new `PublishEvents::PublishWorker`, and enqueue it from the `UserEvent` model's `after_commit` callback.

### 2. Include event versioning in detail-type

Include the version in `detail-type` (e.g., `profile.changed.v1`). This allows parallel operation of old and new versions during breaking changes.

### Note: Transactional Outbox Pattern

This design corresponds to the [Transactional Outbox pattern](https://microservices.io/patterns/data/transactional-outbox.html).

1. Save `UserEvent` record to the database during business logic execution (within the same transaction)
2. Enqueue Sidekiq worker via `after_commit`
3. Worker reads `UserEvent` and sends to EventBridge
4. Record publication status in `eventbridge_published_at` to ensure idempotency

This guarantees consistency between database writes and event publishing.

#### Alternative Approaches for Outbox Pattern

The following methods were considered but deemed excessive for the current situation. We adopted Rails `after_commit` + Sidekiq instead.

| Method | Reason for Not Adopting |
|--------|------------------------|
| [AWS DMS](https://aws.amazon.com/dms/) | Costly. Primarily a data migration service; continuous CDC is possible but not its main purpose |
| [Kinesis Data Streams](https://aws.amazon.com/kinesis/data-streams/) / [DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html) | Over-engineering given the current scale and development schedule |
| [Debezium](https://debezium.io/) | A promising OSS for CDC, but requires infrastructure setup such as Kafka Connect |

We will reconsider these options if event volume increases or stricter ordering guarantees become necessary in the future.

## Rationale

### Reasons for not modifying the existing implementation

- Current consumers are limited to Triple and Caravan, which are internal products
- Since it's internal, the scope of impact is known and migration work can be completed internally
- Considering future expansion, redesigning at this point ensures maintainability and extensibility
- Existing consumers can continue operating with the existing format and switch when migration preparations are complete

### Reasons for including versioning in detail-type

- Enables filtering by version in EventBridge rules
- Follows the CloudEvents type attribute versioning approach (e.g., `com.example.object.deleted.v2`)
- We also considered having `schema_version` in `detail`, but this requires parsing `detail` during routing, which is inconvenient

## Impact

- Enables consumer development with the new event format
- Existing consumers are not affected
- The existing `PublishService` is planned to be deprecated in the future

## Related

- [docs/eventbridge-publishing.md](../eventbridge-publishing.md)
- [docs/eventbridge-publishing.ja.md](../eventbridge-publishing.ja.md)
