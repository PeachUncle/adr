# Adoption of Monolithic Architecture for Phoenix

## Status
Accepted

## Context
We envision Phoenix, an automatic backup system that uploads files to a configurable secondary cloud based storage. The application runs on client machine(s) and deals with files/folders that are mounted to the machine. There is a need for efficiency and performance to minimize CPU taxation and network usage. It needs to be lightweight and performant in order to seem "invisible" and not impend the daily actions of the user. Our team is currently facing a tight schedule and is not familiar with the development of microservices based or event driven applications.

### Alternatives Considered:
- Monolith
- Microservice
- Event Driven

## Decision
In this context, we propose using a **monolithic architecture** by taking note of the following:  
- Phoenix is a low level application and performance must be a top priority. It should use a bit of resources but ensure high throughput backup to the secondary storage
- At this low level, it is hard to divide Phoenix into microservices or as an event driven architecture though they provide better extensibility in the long run since
    - there are a limited number of independent units Phoenix can be divided into
    - each independent unit does not use an independent database
    - the overhead of inter-service communication or the event bridge will significantly impact performance
- The team is not well versed with developing microservices or event driven applications. In addition to the problems mentioned above regarding performance, it can also result in incorrect application of the pattern, can result in unintended technical debt, deployment and monitoring issues.

## Consequences
- Simplicity in development and deployment (fast time to market) - The codebase is relatively smaller with lesser configuration required since components can communicate with each other easily. Since the team members are familiar with the architecture, it will also speed up operations and reduce errors.
- Performance - Monolithic applications are more performant and efficient for low level applications due to integration of components.
- Easier testing - The unified nature simplifies testing since there are no external dependencies or inter-service communication.
- Scalibility concerns - Scaling a monolith is harder since the entire application will have to be replicated, but since our current requirement is only a single instance per machine, this is not a concern at the moment.
- Limited flexibility and extensibility - Future modifications and extensions can be hard to implement due to the coupling between modules. 