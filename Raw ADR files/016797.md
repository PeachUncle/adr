# ADR 001: Strategy for resilience - choice of Retry/Fallback Library

## Status

Accepted

## Context

We require a solution to handle transient failures when calling external services (APIs, databases, message queues). This solution must implement automatic retries and provide a graceful fallback mechanism to ensure service stability and user experience (graceful degradation).

The application is built using **Spring Boot 4.x** (SNAPSHOT version).

Three primary options for implementing retry and fallback are under consideration:

1. **`Spring Retry`:** The native Spring framework library providing `@Retryable` and `@Recover` annotations.

2. **`Resilience4j`:** A modern, lightweight, third-party library that offers Circuit Breaker, Retry, Rate Limiter, and Bulkhead.

3. **`Built-in @Retryable annotation`:** Annotation built-in to Spring 4.x
 
4. **`Built-in Reactor methods`:** Annotation built-in to Spring Reactor

## Decision

The project will use the **Built-in Reactor methods**

## Rationale

The primary rationale for this decision is alignment with the existing Spring ecosystem, minimized dependency risk, and sufficient capability for current requirements:

1. **Native Integration & Stability:** Official Spring project, ensuring guaranteed compatibility and stable integration with the Spring Boot framework, including current (3.x) and future (4.x) versions.

2. **Sufficient Capability:** The core requirement—Retry with Fallback—is fully satisfied.

3. **Reduced Overhead:** By choosing the native solution, we avoid potential dependency conflicts or migration complexity associated with third-party libraries (like ensuring Resilience4j updates).

4. **Compatible with Webflux:** By choosing a solution compatible with Reactor.

## Alternatives Considered

### 1. Resilience4j

| Metric | Evaluation |
| :--- | :--- |
| **Fit for Purpose** | Excellent. Provides robust Retry, Circuit Breaker, Rate Limiting, and Bulkhead. |
| **Pros** | Industry standard for microservice resilience. Comprehensive set of patterns. Functional, lightweight design. |
| **Cons** | **Dependency Risk:** As a third-party library, compatibility with future major Spring Boot releases (e.g., 4.x) is not guaranteed to be immediate or seamless, requiring us to wait for the Resilience4j community to release the corresponding `spring-boot` adapter. |
| **Complexity** | Higher boilerplate configuration (YAML) compared to Spring Retry's simple method annotations. |

## Consequences

### Positive Consequences

* **Guaranteed Compatibility:** Future Spring Boot upgrades will automatically manage versions minimizing upgrade friction.

* **Simple Codebase:** Resilience logic is compatible with Reactor.

* **Low Maintenance:** No external configuration files for simple retry setups are necessary, reducing maintenance overhead.

### Negative Consequences

* **Limited Patterns:** no patterns like **Circuit Breaker**, **Bulkhead**, or **Rate Limiter**, we will have to introduce a second library (like Resilience4j) specifically for those patterns, or migrate fully at that time.

* **No Central Dashboard:** Metrics and status monitoring (like seeing if a circuit is open) is generally less centralized and standardized than with Resilience4j/Actuator integration.