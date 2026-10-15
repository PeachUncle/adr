# ADR-006: API Proxy and gRPC Module Communication

## Status

Accepted — 2025-03-05

## Context

We are splitting the backend into independently deployable modules so we can scale domain capabilities at different cadences. Each module needs uniform security controls, yet we cannot duplicate authentication, authorization, or external exposure logic across them. We also must support both synchronous (HTTP) and asynchronous (RabbitMQ) ingress from external clients without leaking module boundaries.

## Decision

- Introduce a dedicated **API module** that terminates all external traffic, centralizes authentication/authorization, and acts as a proxy to downstream modules.
- Expose external interfaces exclusively via the API module:
  - HTTPS/REST endpoints for web and partner clients.
  - RabbitMQ consumers/producers for asynchronous integrations.
- Standardize **gRPC** as the protocol for API-to-module RPC. The API module invokes each business module over gRPC after enforcing security and tenant policies.
- Require every business module to expose a gRPC server port for the API proxy and remove any direct HTTP exposure from those modules.
- Keep all non-API inter-module collaboration asynchronous via RabbitMQ events; business modules publish and consume domain events instead of calling each other directly over gRPC.
- Allow the API module to call any module over gRPC so it can orchestrate composite workflows while preserving least-privilege checks.

## Consequences

- Security and access control become consistent because only the API module faces external clients.
- Modules must ship and operate gRPC servers, schemas, and client stubs; this adds build/runtime dependencies but keeps contracts explicit.
- Event-driven choreography remains the default between business modules, so each module must own RabbitMQ bindings for the events it emits and consumes.
- The API module becomes a critical path proxy. We need resiliency patterns (timeouts, retries, circuit breakers) to prevent cascading failures.
- Internal load balancing and service discovery for gRPC endpoints are now required as modules scale horizontally.
- Observability must include tracing across the API proxy and gRPC calls so we can diagnose cross-module flows.
