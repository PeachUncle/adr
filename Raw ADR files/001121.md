# Split event processing functions across domain boundaries

## Context
This ADR addresses the decision of splitting event processing functions across domain boundaries within the ClearView system. The goal is to improve modularity, scalability, and maintainability by separating concerns and promoting loose coupling between different parts of the system.

## Decision:
Based on the main characteristics we identified for the ClearView system, our goal is to go for a decentralized approach to processing such events. Although we must mention we do this only in certain domains that require it. We do not want to offload processing just to increase the complexity of the system in areas that does not require it.

The main areas we identify as good candidates for event driven processing are
* metrics & analytics
* resume processing
* survey & audit
* integration of external HR systems

## Status
Proposed

## Options
* Centralized processing: All processing logic is handled within a modular monolith.
* Decentralized event processing: Event processing functions are distributed across different domains, with each domain responsible for handling events related to its specific area of responsibility.

## Consequences
By separating event processing functions, we can improve the modularity and maintainability of the system.
This approach allows for better scalability, as individual domains can be scaled independently based on their specific load.
It promotes loose coupling between domains, reducing the risk of unintended side effects and making the system more flexible.

* Increased complexity: Splitting event processing functions can introduce additional complexity in terms of communication and coordination between domains.
* Potential for performance overhead: Inter-domain communication can add latency and overhead.
* Improved modularity and scalability: The approach can lead to more modular and scalable systems.
* Reduced coupling: Loose coupling between domains promotes better maintainability and reduces the risk of unintended side effects.
   

## Useful links
- [C4 diagram](https://github.com/octaviaah/ClearView/blob/main/2.ArchitectureVisualization/C4Diagram.md)
