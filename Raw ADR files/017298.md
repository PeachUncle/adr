# ADR 0002: Microservices Migration for Weather App

**Status:** Proposed

**Date:** 2025-07-06

**Author:** Danyil Tymofeiev

## Context

The current application is a single NestJS service containing multiple modules:

- `weather` and weather provider clients
- `subscription` with PostgreSQL access via Prisma
- `notification` with cron-based email scheduling
- `email` for sending mails via Nodemailer
- shared modules for metrics, Redis caching and configuration

As usage grows, it becomes hard to scale and deploy this
monolith. Different concerns (fetching weather, persisting subscriptions, sending emails) have very different load
profiles and failure modes. Moving them to independent services lets us scale them separately and isolate failures.

## Considered Options for microservices

### **Weather Service**

* **Responsibilities**:
    * Communication with third‑party weather APIs (**WeatherAPI.com**, **Visual Crossing**).
    * Caching weather data in Redis to reduce API calls.
    * Managing provider priority calls with a `Chain of Responsibility` pattern using factory.
    * Validation of the city name with `class-validator` constraints.

* **Reasons to separate**:
    * API calls and caching logic are external‑resource heavy and may have different scaling and failure characteristics
      from the rest of the system. Isolating this service avoids third-party outages impacting the core workflow.

### **Subscription Service**

* **Responsibilities**:
    * Storing subscription data in PostgreSQL.
    * Handling subscription creation, confirmation, and deletions.
    * Token management for confirmation / un‑subscribe flow.
    * Validate DTOs & business rules (unique e‑mail+city).

* **Reasons to separate**:
    * The database workload grows with the user base and requires its own scaling and backup strategy. Separating it
      keeps transactional logic away from stateless components.
    * Clearly encapsulates the `Subscriptions` bounded context from a DDD perspective, allowing focused ownership of the
      schema and business logic by a dedicated team (person).

### **Notification Service**

* **Responsibilities**:
    * Sending email notifications based on user subscriptions.
    * Scheduling notifications using cron jobs according to the chosen frequency (hourly/daily).
    * Take the latest weather data via `Weather Service`.

* **Reasons to separate**:
    * CPU‑bound + schedule‑driven – needs horizontal scaling during spikes.
    * Decoupled worker execution – allows long-running background jobs to operate independently of request/response
      cycles, avoiding impact on API responsiveness.

### **Email Service**

* **Responsibilities**:
    * Sending emails using Nodemailer.
    * Managing email templates and configurations.
    * Handling email delivery failures and retries.

* **Reasons to separate**:
    * Isolating SMTP operations protects other services from email provider issues and allows dedicated scaling for
      spikes in outgoing mail.
    * Language freedom – could be re‑implemented in other languages for throughput without impacting TypeScript
      services.

### **API Gateway**

* **Responsibilities**:
    * Remains in front of these microservices to serve REST endpoints to clients, orchestrating calls to the internal
      services.
* **Reasons to separate**:
    * Provides a single entry point for clients while allowing internal services.
    * Can implement API versioning and monitoring.
    * Client contract stability – can evolve internal services without breaking external API.

## Considered Options for microservices communication

### **Sync HTTP / REST API**

* **Pros**:
    * Easy to use and debug (Postman/cURL).
    * Well-supported by NestJS with built-in decorators and interceptors.
    * Allows for clear API contracts with OpenAPI/Swagger.
    * Human-readable messages (JSON).

* **Cons**:
    * Larger payloads and higher latency.
    * No strong typing — risk of contract mismatch.
    * Requires manual request/response validation.

### **gRPC (Remote Procedure Calls)**

* **Pros**:
    * Efficient binary protocol with low overhead.
    * Strongly typed contracts via Protocol Buffers.
    * HTTP/2 multiplexing enables faster, concurrent streams.
    * Built-in support for bidirectional streaming.

* **Cons**:
    * Steeper learning curve and setup complexity.
    * Harder to inspect traffic without tooling.
    * Requires additional libraries for NestJS integration.
    * Less human-readable than JSON over HTTP.

### **Message Queues (RabbitMQ, NATS)**

* **Pros**:
    * Decouples producers/consumers — allows async workflows.
    * Built-in retry and dead-letter queue mechanisms.
    * Supports pub/sub patterns for event-driven architectures.
    * Can handle high throughput and scale independently.

* **Cons**:
    * Not suited for real-time request/response use cases.
    * Requires operational overhead to run and monitor the broker.
    * Delivery guarantees and order must be explicitly handled.

## Decision

We will extract the following modules into dedicated microservices and connect them primarily via **gRPC**:

1. **Weather Service**: Handles all weather API interactions and caching.
2. **Subscription Service**: Manages user subscriptions and PostgreSQL access.
3. **Notification Service**: Schedules jobs and orchestrates sending updates.
4. **Email Service**: Manages email delivery and templates.
5. **API Gateway**: Serves as the entry point for clients, orchestrating calls to internal services.
6. Modules like `config`, `logger`, `redis` and `metrics` stay as shared libraries reused by the services.

We have chosen `gRPC` because it enables highly efficient, strongly typed communication between internal services. With
HTTP/2 multiplexing and protobuf contracts, it reduces latency, improves performance under load, and ensures consistency
across languages and teams. `gRPC` tooling also makes it easier to evolve and monitor internal APIs compared to REST.

## Communication Flow Between Microservices

1. `Client` → `API Gateway`: all external HTTP requests (e.g., subscription creation, weather fetch) are handled via
   REST endpoints exposed by the API Gateway.
2. `API Gateway` → `Subscription Service`: forwards user subscription actions via gRPC.
3. `API Gateway` → `Weather Service`: fetches weather data via gRPC.
4. `Notification Service` → `Subscription Service`: at scheduled intervals (e.g., hourly), pulls due subscriptions
   directly via gRPC.
5. `Notification Service` → `Weather Service`: for each due subscription, fetches weather via gRPC.
6. `Notification Service` → `Email Service`: dispatches formatted messages via gRPC including a subject,
   body, recipient.

## Architecture Diagram

[Microservices architecture diagram](../pictures/microservices-communication.png)

## Consequences

**Positive:**

* Independent scaling of `Weather`, `Subscription`, `Notification` and `Email` workloads.
* Failures in one domain (e.g., weather provider outage) do not halt others.
* Typed contracts make inter‑service calls explicit and easier to maintain.
* Simplified reasoning about ownership, responsibilities, and deployment per domain.
* Enables flexible development — each service can be rewritten in another language if needed.

**Negative:**

* More moving parts to deploy and monitor.
* Inter-service contracts require additional tooling and strict versioning policies.
* Observability and tracing across service boundaries become more complex.