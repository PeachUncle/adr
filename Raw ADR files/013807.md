# ADR-008 — CloudEvents adoption for domain events

Status: Accepted
Date: 2025-10-15

## Context

We publish domain events from the Tenants service to RabbitMQ. We already standardized on Avro for event data (see ADR-003 for message versioning). To interoperate with external systems and future event gateways, we want our events to comply with [CloudEvents 1.0](https://cloudevents.io/).

CloudEvents defines a small set of metadata attributes (id, source, type, specversion, time, subject, datacontenttype, dataschema, etc.) and multiple transport bindings (HTTP, Kafka, AMQP 1.0, NATS, etc.). RabbitMQ uses AMQP 0.9.1 which does not have an official CloudEvents binding, but CloudEvents allows binary content mode where attributes are carried as transport-native metadata (headers/properties).

## Decision

- Adopt CloudEvents core specification v1.0.
- Use Binary Content Mode: event data is the Avro-encoded bytes; CloudEvents attributes are mapped to message headers.
- Transport: RabbitMQ (AMQP 0.9.1). We map CloudEvents attributes to AMQP message headers using the conventional `ce_` prefix as follows:
  - `ce_specversion` = `1.0`
  - `ce_type` = event name (e.g., `tenant.created.v1`)
  - `ce_source` = logical emitter id: `tenants-service` (subject to future configuration)
  - `ce_id` = unique event id (UUID) — aligns with Avro field `eventId`
  - `ce_time` = RFC3339 timestamp — aligns with Avro field `occurredAt`
  - `ce_subject` = domain identifier relevant to the event (`tenantId` for tenant events, `userId` for user events)
  - `ce_datacontenttype` = `application/avro`
  - `ce_dataschema` = URI identifying the schema. We use `urn:avro:schema:<full.avro.namespace.Name>` (e.g., `urn:avro:schema:com.eureckah.banking.events.v1.TenantCreated`).
- Exchange strategy is unchanged: topic exchanges per event type (`events.v1.<event>`). Routing key remains configurable (default: `events`).

## Consequences

- External consumers that understand CloudEvents can treat our messages as CloudEvents 1.0 using the binary-mode mapping.
- Our Avro contracts remain the source of truth for the event data payload; CloudEvents attributes live in headers.
- We avoid introducing an additional SDK; the mapping is implemented via message headers to keep the change minimal.

## Alternatives considered

- Structured mode (serialize full CloudEvent as JSON): Rejected. Would complicate Avro usage or require nested JSON + Avro; binary mode better fits Avro binary payloads.
- Using CloudEvents SDK for Java: Deferred. Not necessary for the minimal scope; may be adopted later for validation and builder APIs.

## Follow-up

- Consider making `ce_source` configurable via environment variable if multiple emitters are introduced.
- If we add Kafka or HTTP outputs, define corresponding CloudEvents bindings explicitly.
