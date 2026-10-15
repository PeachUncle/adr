# ADR-003: Hybrid API Access Strategy

Date: 2025-11-26
Status: Accepted

## Context
The NovaEco ecosystem consists of multiple distinct verticals (e.g., NovaAgro, NovaMind).
We initially considered routing all traffic through a single API Gateway (`api.novaeco.tech`) to act as a "front door."

However, enforcing this for our own internal applications (e.g., `mind.novaeco.tech`) creates significant drawbacks:
1.  **Single Point of Failure:** If the central gateway fails, all unrelated vertical apps go offline.
2.  **Performance Bottleneck:** Extra network hops and JSON serialization overhead for every request.
3.  **Coupling:** The central gateway team becomes a blocker for vertical teams wanting to expose new endpoints.

## Decision
We will adopt a **Hybrid Access Strategy** that distinguishes between Vertical Apps, the Central Dashboard, and Third-Party Integrators.

1.  **Direct Access for Vertical Apps:**
    Domain-specific frontends (e.g., `agriculture.novaeco.tech`) will communicate **directly** with their respective Backend APIs (e.g., `api.agriculture.novaeco.tech`).
    * *Mechanism:* Each backend handles CORS for its matching frontend.
    * *Benefit:* Lowest latency for heavy user operations.

2.  **Gateway Aggregation for Mission Control:**
    The **NovaAdmin** dashboard (`admin.novaeco.tech`) will consume the **Multiplexed Gateway** (`api.novaeco.tech`) to perform cross-domain aggregation (e.g., "Show me alerts from Agro AND Finance").
    * *Benefit:* Keeps the Dashboard decoupled from specific service implementations.

3.  **Multiplexed Gateway for External Traffic:**
    The Central Gateway (`api.novaeco.tech`) serves as the unified entry point for **External 3rd-Party usage**. It implements **Protocol Multiplexing** on Port 443:
    * **REST/JSON:** For standard web integrations.
    * **gRPC:** For high-performance external agents and IoT.
    * *Routing:* Traffic is routed based on `Content-Type` (`application/json` vs `application/grpc`).

## Consequences
### Positive
- **Fault Isolation:** A crash in the central Gateway affects the Dashboard and external APIs, but `NovaAgro` users can still manage their farms directly.
- **Latency:** Removed unnecessary "hops" for deep vertical workflows.
- **Unified Public Surface:** External developers have a single, strongly-typed endpoint for all interactions.

### Negative
- **Client Complexity:** Frontend configs must track specific service URLs (e.g., `NOVAAGRO_API_URL`) rather than just one gateway URL.
- **Infrastructure Complexity:** The Gateway ingress must handle HTTP/2 and demultiplex protocols correctly.
- **Security Config:** CORS and SSL termination must be configured on every microservice ingress, not just the gateway.