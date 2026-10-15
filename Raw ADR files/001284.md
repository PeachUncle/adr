# Communication between Presentation layer and Business logic layer

* Status: accepted
* Deciders: Alejandro Garcia Prada
* Date: 2025-10-25

## Context and Problem Statement

After selecting a three-tier architecture (client, business logic, and data), it is necessary to define how the Presentation layer will communicate with the Business logic layer. The system must support integration with external services while ensuring interoperability, security, and scalability.

The challenge is to choose a communication protocol and data format that:

* Enables integration with third-party APIs (e.g., Stripe, traffic data).
* Maintains layer independence and modularity.


## Decision Drivers

* RF-07 Comunicarse con servicio externo para datos de tráfico

## Considered Options

* 0002-1-HTTP/S-Communication
* 0002-gRPC

## Decision Outcome

Chosen option:  "0002-1-HTTP/S Communication", because this communication between the client and the business logic combines the universality and compatibility of HTTP with the flexibility to preserve context for multi-step business processes (e.g., order lifecycle, payment authorization, delivery updates).

### Positive Consequences

* Compatible with third-party HTTP services and internal APIs.
* Easier debugging, monitoring, and testing with standard HTTP tools.


### Negative Consequences

* Increased complexity in state management (need to use mechanism like cookies) and session synchronization when scaling horizontally.
* Slightly higher latency due to multiple HTTP exchanges between tiers.


## Pros and Cons of the Options

### 0002-1-HTTP/S Communication

The Presentation layer communicates with the Business Logic layer through standard HTTP or HTTPS requests. Each request includes the necessary context (headers, tokens, payloads), and the server responds with a structured message, typically in JSON format.

More info: https://developer.mozilla.org/en-US/docs/Web/HTTP

* Good, because it is universally supported by web, mobile, and third-party clients.
* Good, because it allows integration with third-party APIs, such as Stripe or traffic data services.
* Good, because debugging and monitoring are easier using standard HTTP tools (Postman, curl, browser developer tools).
* Good, because integration with existing firewalls, proxies, and load balancers is straightforward.
* Bad, because it has higher network overhead per request-response compared to binary protocols.
* Bad, because multiple HTTP exchanges between tiers can introduce additional latency.

## 0002-2-gRPC

gRPC is a high-performance Remote Procedure Call (RPC) framework that uses HTTP/2 and Protobuf for binary message serialization. It allows clients and servers to communicate efficiently, supports bidirectional streaming, and enforces strict contracts via .proto files.

More info: https://grpc.io/

* Good, because binary messages are more compact than JSON/XML, improving performance.
* Good, because bidirectional streaming allows real-time notifications or continuous data flows.
* Good, because it natively supports multiple languages, making it ideal for heterogeneous service stacks.
* Bad, because not all browsers support native gRPC; web clients require gRPC-Web.
* Bad, because infrastructure is more complex (persistent connections, load balancers, firewalls).
* Bad, because debugging and monitoring are more difficult compared to HTTP/REST.
