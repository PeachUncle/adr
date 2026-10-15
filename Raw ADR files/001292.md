# Removal of Bridge in Client Tier

* Status: proposed
* Deciders: Jaime Ochoa de Alda Cerdán
* Date: 2025-11-12

## Context and Problem Statement

Previous iterations of the presentation tier relied on the Bridge Pattern, separating the abstraction (User, ClientPlatform) from its implementations (WebClient, DesktopClient, MobileClient). This structure aimed to support multiple client types with independent rendering logic.

However, with the architectural shift toward a centralized API Gateway, this bridge abstraction is no longer required. The gateway now acts as the unified access layer for all external clients—web, mobile, desktop, or future interfaces—handling routing, request transformation, and authentication uniformly.

Maintaining separate platform classes adds complexity without functional benefit, as all client types now interact with the same gateway endpoints.

The Bridge Pattern decision (0006-presentation-tier-description) is therefore annulled.

## Decision Drivers

* Simplify the presentation tier by removing platform-specific client abstractions that are no longer needed when using an API Gateway.
* Ensure support for new client types through the API Gateway, without requiring changes in the internal model.
* Centralize request routing and apply consistent access control rules through a single entry point.
* Ensure compatibility with current and future client origins, since all of them communicate with the system through standard HTTP/HTTPS requests to the API Gateway.

## Considered Options

* 0014-1-Unified-Client-via-API-Gateway

## Decision Outcome

Chosen option: 0014-1-Unified-Client-via-API-Gateway.
The presentation tier is simplified by removing platform-specific client classes and keeping a single client model. All external clients (web, mobile, desktop) now interact with the system exclusively through the API Gateway, which handles routing and request normalization. 

Communication is performed via HTTP/HTTPS, making the internal design independent of the client’s origin. This avoids duplicating logic already handled by the gateway and keeps the system extensible for future client types.

### Positive Consequences

* Reduces internal complexity by removing platform-specific classes that will become redundant once the Gateway handles client differentiation.
* Centralizes all client interactions, making the system easier to reason about and maintain.
* Improves extensibility, since new clients do not require new platform-specific classes, only Gateway configuration.
* Avoids adding unnecessary responsibilities inside the presentation tier, since request adaptation is already handled by the API Gateway.

### Negative Consequences

* The presentation tier removes its platform-specific classes, relying fully on the Gateway to provide a unified entry point.
* Internal components lose platform-specific hooks, which may require alternative mechanisms if platform-dependent logic is ever needed.

## Pros and Cons of the Options

## 0014-1-Unified-Client-via-API-Gateway

Replace platform-specific classes with a single Client entity that interacts with the system exclusively through the API Gateway. The gateway manages all external requests, providing device-agnostic access.

* Good, because it centralizes all external communication through the Gateway.
* Good, because it removes unnecessary abstractions that no longer provide value.
* Good, because new client types can be added without modifying internal classes.
* Bad, because platform-specific concerns now depend completely on external clients, which may require clearer documentation to ensure consistent integration.







