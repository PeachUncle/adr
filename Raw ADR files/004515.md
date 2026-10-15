# 12. Architectural Design Pattern Decision
Date: 20/11/2023
## Context and Problem Statement

What architectural design pattern to implement into the system in order to promote a secure and ultimately more managable system.

## Considered Options

* CQRS
* Event sourcing

## Decision Outcome

I have considered two main system design patterns to implement into the AFS visa processing system. 

Firstly there is the potential to implement the concept of CQRS a design pattern which essentially separates CRUD operations often by having separate databases or tables within the database and then separate logic running for querying the database and writing to it. This means that asymetrically you can utilise the concept of one service writing to the database and another reading simulateously. The main disadvanatage is when a resource is trying to be accessed by both services which if designed incorrectly can cause deadlocks in the system.

I will not implement CQRS as a design pattern into the system due to the complexity and especially when a simple CRUD style operations running on a single service should be necessary even when the system is scaled up. (Microsoft, n.d.)

Alternatively there is the potential to implement event sourcing a way to trace actions performed on the database and the system in general. The main advantages of this includes enforcing non-repudiation to trace who has taken what actions on the system. But also to monitor the business entity as it changes and evolves as processes are performed on it throughout the system. In our case this would be visa application itself as it is the most critical business entity. (Richardson, n.d.)

Therefore I have decided on Event sourcing as I believe it is an essential and very applicable concept to this system. 

### Consequences

* A clear traceable log of how the visa application moves and changes through the system.
* A way to prove who makes what changes within the system for auditing purposes.

### References 
Richardson, C. (n.d.). Pattern: Event sourcing. Microservices.io. Retrieved November 26, 2023, from https://microservices.io/patterns/data/event-sourcing.html
<br>
Microsoft. (n.d.). CQRS pattern - Azure Architecture Center. Microsoft Learn. Retrieved November 26, 2023, from https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
