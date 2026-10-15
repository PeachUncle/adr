# ADR-005: gRPC/ProtoBuf Standard

Date: 2025-11-26
Status: Accepted

## Context
The NovaEco is a distributed system of systems involving diverse actors: internal microservices, external high-frequency trading agents, and IoT telemetry aggregators.

Relying solely on JSON for machine-to-machine communication introduces significant risks:
1.  **Loose Typing:** JSON lacks schema enforcement, leading to runtime errors when services drift.
2.  **Performance Overhead:** Text-based serialization adds latency, which is unacceptable for high-throughput loops (e.g., Grid Balancing or Trading).
3.  **Inefficient Development:** Developers must manually write client wrappers for every REST endpoint.

## Decision
We adopt **gRPC with Protocol Buffers (ProtoBuf)** as the standard protocol for **synchronous machine-to-machine communication**, regardless of whether the consumer is internal or external.

1.  **Internal Mesh:** Core services (e.g., `NovaAgro` $\leftrightarrow$ `Auth`) communicate directly via gRPC for maximum throughput.
2.  **Public Access:** External agents access specific gRPC interfaces (e.g., `VerificationService`) via the **Multiplexed Gateway** (`api.novaeco.tech`) on Port 443 (see [ADR-003](./adr-003-hybrid-api-access.md)).
3.  **Schema-First Development:** The `.proto` files are the single source of truth. We use them to automatically generate and publish client SDKs (e.g., `novaeco-auth-client`) to PyPI/npm.

## Consequences
### Positive
- **Strict Contracts:** ProtoBuf enforces schema compatibility, preventing integration bugs before deployment.
- **Unified Surface:** External agents get the same high-performance interface as internal services.
- **Productivity:** Developers (internal and external) simply import the generated SDK to get a fully-typed, auto-validated client.

### Negative
- **Versioning Rigor:** Since our `.proto` definitions are public APIs, we must strictly adhere to semantic versioning. Fields cannot be renamed or removed without a long deprecation cycle to avoid breaking external integrations.
- **Tooling Friction:** Debugging requires specialized tools (like `grpcurl` or Postman with gRPC support) rather than standard browsers.