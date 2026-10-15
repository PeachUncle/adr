# Architecture Style Architectural Decision Record

* Status: accepted
* Date: 2025-10-24
* Decision-Makers: Oliver Sennett-Neilson, Harris Fiaz, Conner Bowen
* Consulted: Oliver Sennett-Neilson, Harris Fiaz, Conner Bowen
* Informed: Oliver Sennett-Neilson, Harris Fiaz, Conner Bowen

## Context and Problem Statement

The Advanced Media Library (AML) system requires a scalable and maintainable web application to support a growing user base. The architecture must enable modular testing, scalability management, and data integrity, while efficiently handling concurrent requests from thousands of users.

Given these requirements, an architecture isolating application layers is necessary to improve performance, facilitate debugging, and enhance security. Three-tier architecture meets these needs by clearly separating the presentation, application logic, and data layers.

## Decision Drivers

* Scalability: Each layer can be scaled independently, allowing the system to handle user growth and database expansion efficiently.
* Isolated Testing: Separation of concerns enables testing of individual layers, streamlining debugging and reducing development time.
* Data Integrity: Users interact only with the logic layer, minimizing risks to database integrity and improving security.
* Performance Optimization: The logic tier processes user requests before database interaction, reducing direct load on the database.
* Maintainability: Modular architecture simplifies updates and maintenance by isolating changes to specific layers.

## Considered Options

### 1. Three-Tier Architecture
* Presentation, logic, and data layers are separated to ensure modularity and scalability.

### 2. Two-Tier Architecture
* Combines logic and database tiers, simplifying design but limiting scalability and modularity.

### 3. Microservices Architecture
* Divides the system into independent services, each handling a specific function.

## Decision Outcome

Chosen option: Three-Tier Architecture

Justification:
Three-tier architecture balances complexity and scalability, making it ideal for AML's requirements. While microservices provide better scalability for enterprise-scale systems, their complexity introduces challenges for AML's timeline and team resources. Two-tier architecture, while simpler, falls short in scalability and testing, making it unsuitable for AML's anticipated user growth.

Three-tier architecture supports independent scaling of layers, ensures better data integrity, and aligns with AML's goal of a scalable and maintainable solution.

## Consequences

Good:
* Each layer can scale independently, improving scalability to meet yearly growth projections.
* Modular architecture simplifies isolated testing, making debugging and development more efficient.
* Better data security and integrity, as users do not directly interact with the database.

Bad:
* More complex than two-tier architecture, potentially increasing workload during initial implementation.
* Slightly longer processing times due to the additional logic layer.

## Confirmation

The implementation will be validated through:
* Code Reviews: Regular reviews to ensure layer separation and adherence to architectural principles.
* Load Testing: Verify scalability and responsiveness under anticipated peak loads.
* Integration Testing: Confirm that layers interact seamlessly and maintain data consistency.

## Pros and Cons of the Options

### Two-Tier Architecture
Good:
* Easier to implement for small to medium-sized systems.

Bad:
* Limited scalability as direct user interaction with the database creates bottlenecks.
* Less modular, making testing and updates more challenging.

### Microservices Architecture
Good:
* Highly scalable due to independent services.

Bad:
* Harder to maintain data consistency, as updates to one service may disrupt others.
* Increased complexity, requiring more effort in integration testing and service orchestration.

## More Information

References:
1. [Three-Tier Architecture Overview](https://docs.aws.amazon.com/whitepapers/latest/serverless-multi-tier-architectures-api-gateway-lambda/three-tier-architecture-overview.html)
2. [Comparison of Microservices and Monolithic Architectures](https://www.atlassian.com/microservices/microservices-architecture/microservices-vs-monolith)
3. [Pros and Cons of Two-Tier Architecture](https://www.geeksforgeeks.org/difference-between-two-tier-and-three-tier-database-architecture/)