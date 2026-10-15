# ADR: EventBridge Event Format Design

- **Date**: 2025-12-19
- **Status**: Approved
- **Deciders**: Akira Suenami

## Context

We need to design the format of events published to EventBridge. EventBridge events have the following fields:

- `source`: Event source identifier
- `detail-type`: Event type
- `detail`: Event payload (JSON)

We need to determine the naming conventions and structure for these fields.

## Decision

### 1. Source Format

```
com.twogate.idp/{tenant_id}/users
```

- Use reverse domain notation with corporate domain `com.twogate`
- Append service name `idp`
- Include tenant ID and resource name as path

### 2. Detail-type Format

```
{resource}.{action}.{version}
```

Examples: `profile.changed.v1`, `delivery_address.added.v1`

- Resource names are singular (`profile`, `contact_address`, `delivery_address`)
- Actions are past tense (`signed_up`, `changed`, `added`, `removed`, etc.)
- Version is appended as suffix (`.v1`)

※ Specific event names will be determined separately.

### 3. Detail Payload Structure

```json
{
  "event_data": {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "occurred_at": "2025-12-19T10:30:00+09:00",
    "attr1": "value1",
    "attr2": "value2"
  },
  "resource": { ... }
}
```

- `event_data`: Event metadata and event-specific attributes
- `resource`: Full snapshot of the resource after the change

### 4. JSON Key Naming Convention

Use snake_case for all keys.

## Rationale

### Reasons for including tenant ID in source

- We considered whether to include it in `source` or `detail-type`
- EventBridge supports wildcard filtering
- To receive events from all tenants, filter with `com.twogate.idp/*/users`
- To receive events from a specific tenant only, specify directly in source
- Most consumers are internal products, making this approach convenient

### Reasons for using corporate domain com.twogate

- Initially considered `net.id-platform`
- However, the service name (idp) may change in the future
- Corporate domain `com.twogate` is stable and unlikely to change
- Even if the service name changes, consumers can handle it with `com.twogate.*` wildcard

### Reasons for using snake_case

- AWS event formats have no unified naming convention (EventBridge standard fields use kebab-case, but each service varies)
- The implementation language is Ruby, where snake_case is natural
- Custom fields in `detail` can be freely defined, so we follow project conventions

### Reasons for event_data / resource attribute names

- Candidates considered:
  - `payload` / `snapshot`
  - `input` / `state`
  - `changes` / `current`
  - `trigger` / `resource`
  - `event_data` / `resource`
- `event_data` clearly indicates it's data about the event
- `resource` aligns with REST concepts and is familiar
- This combination was judged to be the most understandable

### Reasons for singular/plural resource names

- Resource names in `detail-type` are singular: because an event represents "something that happened to one entity"
- Resource names in `source` are plural: because they indicate a "collection" of resources
- This is consistent with REST API conventions (`GET /users/{id}` retrieves an individual resource)

## References

- [CloudEvents Specification](https://github.com/cloudevents/spec)
  - `source`: URI-reference (MUST), absolute URI (RECOMMENDED)
  - `type`: reverse-DNS name (SHOULD)
- [AWS EventBridge Event Patterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html)

## Related

- [ADR: Redesign of EventBridge Event Publishing](../20251218-eventbridge-redesign/ADR.md)
- [docs/eventbridge-publishing.md](../eventbridge-publishing.md)
- [docs/eventbridge-publishing.ja.md](../eventbridge-publishing.ja.md)
