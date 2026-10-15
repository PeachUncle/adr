# Name
Implementation of Event Sourcing

## Status
Proposed

## Context
This ADR serves as a guide for the development of the structure and behavior of our application service, specifically focusing on implementing Event Sourcing. Event Sourcing is a design pattern that captures all changes to an application's state as a sequence of events. These events are then used to reconstruct the state of the application at any given point in time.

To illustrate the workflow and interactions within the application service, we have provided the PlantUML text used to generate the UML sequence diagram:

To illustrate the workflow and interactions within the application service, we provided a UML sequence diagram:

![Event source implementation sequence diagram](https://github.com/dddsphere/quanta/blob/new/wip/docs/adr/image/20230531-01-implementation-of-event-sourcing-01.png)

### Source

```
@startuml
participant Client as Client
    participant Controller as Controller
    participant CommandHandler as CommandHandler
    participant Command as Command
    participant Aggregate as Aggregate
    participant EventStore as EventStore
    participant EventBus as EventBus
    participant DomainEvent as DomainEvent
    participant Projection as Projection
    participant ReadModel as ReadModel

    Client->>Controller: HTTP Request
    Controller->>CommandHandler: Process Command
    CommandHandler->>Command: Extract Command
    Command-->>Controller: Command Result
    Controller->>Aggregate: Apply Command
    Aggregate-->>CommandHandler: Aggregate Result
    CommandHandler->>EventStore: Save Events
    EventStore-->>CommandHandler: Event List
    CommandHandler->>EventBus: Publish Events
    EventBus->>DomainEvent: Handle Event
    DomainEvent->>Projection: Update Projection
    Projection-->>ReadModel: Updated Read Model
@enduml
```

## Consequences
The implementation of Event Sourcing in our application service follows the following technical decisions:

1. **Event Store using PostgreSQL**: We have chosen PostgreSQL as the backend database for our Event Store. This provides a reliable and scalable solution for storing and retrieving the sequence of events captured by the application.

2. **Event Bus using Go process**: Our design goal is to reduce the number of moving parts in the system. Therefore, we will use a Go process to handle event management. This approach simplifies the system and minimizes dependencies. However, we remain open to extending the implementation with a full-fledged Event Bus in the future to accommodate larger use cases.

3. **Projections using MongoDB**: The projections, responsible for updating the Read Model, will be implemented using MongoDB. MongoDB's document-oriented nature and powerful querying capabilities offer flexibility and scalability for storing and retrieving projected data.

## Date
May 31, 2023
