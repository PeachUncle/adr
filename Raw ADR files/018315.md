# 2. Service granularity

Date: 2022-09-26

## Status

Accepted

## Context

Based on our five domains we checked against the integrators and disintegrators to see if we can divide or join the domains into microservices.

Service functionality:
The domains are already divided into the different functionalities therefore it's suitable to create one microservice for each domain.

Code Volatility: 
Inside the different microservices components have the same code volatility.

Scalability and Throughput:
Different scaled services are already divided into their own microservices, e.g. The Executor Pool need to scale differently than the Tasklist service based on calls per minute.

Fault Tolerance:
The services are independent if one service fails the others will still work, e.g. if the roster fails tasks and executors can still be added.

Data Security:
At this point no services need special security. In the future this could change based on data ownership requirements.

Extensibility:
The parts of the systems that need to be extended are separated into microservices, e.g. the auction house

Database transaction:

There are a few actions that requires a single data transaction that need to be executed in multiple services. Nevertheless, we decided not to join any services.

Workflow and choreography:
There are no services that need to execute tasks in synchronization, due to our ansynchronous implementation of the services. Therefore, the services work independently. This approach leads to reduced decoupling of services and improves the fault tolerance. 

Shared code:
As of now there are no shared libraries that are used in multiple services

Data relationships:
Each service handles their own data. Roster, executor and tasklist services could use the same database but can also be decoupled with ease. Based on advantages listed before we decided to decouple the services. 


## Decision

5 microservices are created: Tasklist, Roster, ExecutorPool, Executor, AuctionHouse

## Consequences

Decoupling the services into 5 services provides flexibility but also adds more complexity and overhead.