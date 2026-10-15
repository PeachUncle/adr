# ADR-005: Modulith Architecture for Spring Boot Application

## Status
Accepted

## Date
2025-03-01

## Context
Our team is developing a Spring Boot web application that needs to balance the benefits of a monolithic architecture (simplicity, development speed) with those of microservices (modularity, clear boundaries). We need an architectural approach that:

- Provides clear module boundaries and enforces them
- Allows for independent development of business domains
- Reduces complexity compared to a full microservices architecture
- Maintains deployment simplicity
- Supports future evolution, including potential extraction of microservices
- Aligns with our team size and organizational structure
- Addresses the complexity of our business domain without overengineering

We've observed challenges with both traditional monoliths (which tend to become tangled over time) and microservices (which introduce significant operational complexity and distributed system challenges).

## Decision
We will adopt a "Modulith" architecture style for our Spring Boot application, leveraging Spring Modulith for implementation. This architecture consists of:

1. **A single deployable application** that contains multiple well-defined business modules
2. **Explicit module boundaries** enforced through package structures and access controls
3. **Internal event-based communication** between modules when appropriate
4. **Module-specific persistence** where each module owns its data structures
5. **Shared kernel** for truly common components

The structure will follow these principles:

- Each business domain will be a separate module with its own package
- Modules will expose clear public APIs through interfaces or service classes
- Internal module implementations will be encapsulated and not accessible to other modules
- Cross-module communication will be explicit through published interfaces or events
- Each module will own its persistence concerns (tables, repositories)
- Circular dependencies between modules will be prohibited

## Implementation Structure

```
com.example.application
  ├── [app name]
  │    ├── ApplicationMain.java
  │    └── shared/  # Shared kernel - minimal common code
  │
  ├── catalog/      # Business module for product catalog
  │    ├── api/     # Public API of this module
  │    ├── internal/# Internal implementation (not accessible outside)
  │    └── data/    # Module-specific persistence concerns
  │
  ├── order/        # Business module for orders
  │    ├── api/
  │    ├── internal/
  │    └── data/
  │
  ├── customer/     # Business module for customer management
  │    ├── api/
  │    ├── internal/
  │    └── data/
  │
  └── [other business modules]
```

We will use Spring Modulith to verify and enforce module boundaries through its testing support.

## Consequences

### Positive
- Maintains the deployment simplicity of a monolith
- Provides clear module boundaries that prevent unwanted dependencies
- Enables parallel development by different teams on different modules
- Reduces the operational complexity compared to microservices
- Facilitates easier testing of the entire system
- Allows incremental migration to microservices if needed in the future
- Improves code organization and discoverability
- Provides a clearer mental model of the system architecture
- Reduces coordination overhead compared to microservices

### Negative
- Requires discipline to maintain module boundaries
- Shared database may become a bottleneck or coupling point if not carefully managed
- May still face some scaling challenges inherent to monolithic deployments
- Could lead to in-memory communication that hides important domain events
- Potential for "hidden" coupling through shared infrastructure or libraries
- Less flexibility in technology choices compared to microservices

## Alternatives Considered

1. **Traditional Layered Monolith**
   - Simpler to implement initially
   - Lacks enforced boundaries between business domains
   - Tends to become more tangled over time
   - Doesn't provide clear isolation of business domains

2. **Microservices Architecture**
   - Provides stronger isolation and independent scalability
   - Significantly increases operational complexity
   - Introduces distributed systems challenges
   - Requires more infrastructure and DevOps support
   - May be overengineering for our current scale and team size

3. **Hexagonal Architecture**
   - Focuses on isolation of the domain model from external concerns
   - Doesn't specifically address boundaries between business domains
   - Could be combined with the modulith approach

## Implementation Notes
- We will use Spring Modulith to enforce module boundaries
- Each module will have its own set of integration tests
- We'll use package-private visibility to restrict access to internal components
- Module interactions will be documented explicitly
- We'll implement a documentation approach that visualizes module dependencies
- Database schema will use table prefixes or schemas to indicate module ownership
- Event publishing will be used for cross-module communication where appropriate

## Compliance Verification
- Automated tests will verify module boundaries are not violated
- Code reviews will check for appropriate encapsulation
- We will generate and review module dependency graphs periodically
- Static analysis tools will be configured to flag unintended cross-module dependencies

## References
- Spring Modulith: https://spring.io/projects/spring-modulith
- Modular Monoliths by Simon Brown: https://www.youtube.com/watch?v=5OjqD-ow8GE
