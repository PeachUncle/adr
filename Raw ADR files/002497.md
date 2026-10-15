# AML System Architecture Decision Record (ADR)

## Context

Selecting an architecture style for the Advanced Media Library (AML) system to improve scalability and flexibility to have consistent user experiences and operational efficiencies, ensuring seamless acess to its media services across multiple channels.

## Problem Statement

The current AML system lacks the scalability and flexibility needed to manage media services effectively lealding to operational inefficiencies and inconsistent user experiences. The architecture style chosen must address these concerns and support future growth.

## Considered Options

1. **Microservices Architecture**
2. **Service Oriented Architecture (SOA)**
3. **Monolithic Modular Architecture**

## Chosen Architecture: **Microservices Architecture**

After reviewing several options, **Microservices Architecture** has been chosen as the most efficient architecture style to meet AML’s requirements for scalability, flexibility, and improved user experience.

## Consequences of the Decision

- **Scalability**: AML will be able to scale its services independently as the user base grows.
- **User Experience**: The system will provide seamless, continuous access across multiple channels (online, phone, in-branch).
- **Resilience**: The system will be resilient to service-level failures, ensuring high availability.
- **Flexibility**: AML will easily integrate new features or services, ensuring long-term flexibility.
- **Operational Efficiency**: Centralized budget control and procurement efficiency will be achieved, reducing operational overhead.

## Pros of Microservices Architecture

- No downtime when adding or updating services.
- The system can handle the anticipated 10% annual user base growth without performance bottlenecks.
- Centralized control for procurement and budgeting.
- Breaks the application down into small, independent services each responsible for specific functions enables enhanced flexibility, scalability and resilience.
- Compatible to develop with different programming languages.
- Teams can work on different services simultaneously which speeds up progress and encourages innnovation.

## Cons of Microservices Architecture

- Requires robust DevOps practices.
- Higher operational complexity due to service orchestration and monitoring.
- More maintenance and resources required (memory, CPU).
- Ensuring data consistency across services becomes more complex.
- Testing microservices application has more complexity.
- More prone to having latency and performance issues as it requires robust infrastructure and tooling.

## Confirmations

This architecture style has been reviewed and determined to be the most efficient out of the options.

---

## Pros and Cons of Other Considered Options

### 1. Service Oriented Architecture (SOA)
- **Pros**: Good for loosely coupled services that can be reused. Similar to microservices where services can be deployed independently.
- **Cons**: Communication between services can introduce latency and complexity. Managing data consistency across services is challenging.

### 2. Monolithic Modular Architecture
- **Pros**: It is simple to develop as everything is unified in one single component and easier to maintain data consistency. 
- **Cons**: If the system gets bigger, the codebase becomes harder to manage when everything is unified. 

---

## Conclusion

The **Microservices Architecture** was chosen for AML due to its superior scalability, flexibility, and resilience to failure, making it the best fit to handle AML’s growth and improve user experience across multiple channels. While it introduces complexity in terms of DevOps and service orchestration, the long-term benefits of independent service scaling and modularity make it the optimal solution for AML's evolving needs.
