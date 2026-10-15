# Adoption of Hexagonal Architecture

- Status: Accepted
- Deciders: [System Architect, Domain Expert, Development Team, ...]
- Date: [e.g., 2023-01-01]
- Technical Story: [e.g., Project setup | https://jira.project-name.com/issues/123]

## Context and Problem Statement

We are building a software system that needs to be resilient to change and easy to maintain in face of evolving requirements. The question is: "What is the best architectural style
to use for our software system?"

## Considered Options:

- Hexagonal Architecture
- Layered Architecture
- Microservices Architecture

## Decision Outcome:

Chosen option: "Hexagonal Architecture", because it provides a clear separation of concerns that decouples the core domain from peripheral concerns (like UI, databases, etc.). This
decoupling ensures that the core domain remains unaffected by the changes in the peripheral components, making it easier to maintain and evolve. Moreover, the enforcement of
Hexagonal Architecture will be done using Gradle project structure instead of ArchUnit for further clarity and modularity.

## Consequences:

**Positive Consequences**

- The domain logic and business capabilities of the system remain isolated and unaffected by infrastructure changes.
- It improves testability by allowing different parts of the system to be tested independently.
- It facilitates easy swaps or changes to infrastructure components (e.g., database, UI, etc.) without affecting the domain logic.

**Negative Consequences**

- The learning curve associated with this architecture might be steep for team members not familiar with it.
- Implementation of Hexagonal Architecture might initially take more effort and time due to its thoroughness in separation of concerns.

## Pros and Cons of the Options:

### Hexagonal Architecture

- Good, because it isolates the domain logic and business rules, making them independent of any peripheral changes.
- Good, because it facilitates better testability of software components.
- Bad, because it may be overkill for really simple or small-scale applications.

### Layered Architecture

- Good, because it is simple and easy to understand, making it suitable for small applications.
- Good, because it is a common pattern and widely adopted in the industry.
- Bad, because it can lead to 'high coupling' if not implemented carefully.

### Microservices Architecture

- Good, because it enables each service to be developed, deployed, and scaled independently.
- Good, because it enables the use of different technologies and languages across different services.
- Bad, because it adds complexity in terms of service coordination, deployment, and data consistency.

## Links:

- [Hexagonal Architecture Explanation](https://alistair.cockburn.us/hexagonal-architecture/)
- [Microservices Architecture](https://microservices.io/patterns/microservices.html)
