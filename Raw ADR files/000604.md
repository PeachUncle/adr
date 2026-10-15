# Using Service-Oriented Architecture | Date: 13/10/25

## Context and Problem Statement
I am currently creating a container diagram and want to re-evaluate what architectural style I am using. This is because I have now looked further into non-functional requirements and have a better understanding
of the system as a whole. The main focus for the project is to be scalable and extensible over the performance value which needs to be efficient but there is less priority on needing immediate responses.

The current architecture may not be optimal for the system I am creating. As mentioned in chapter 10 of *Fundamentals of Software Architecture* [Richard & Ford, 2020],  a key issue for Layered Architecture is the deployability and testability rating is very low e.g. 3 line code change requires entire deployment unit to be redeployed. This is not feasible for an application that needs to reliably handle communication of complaints between consumers and staff.

The problem is we need to research to see if there is a more suitable option out there with the benefits provided from the layered architecture and the deployability issue given the Complaint Management System will have future implementations of an AI chatbot and is crucial as many Consumers and Staff will be on the system all times of the day.

## Considered Options

* Service-Oriented Architecture (Selected)
* Layered Architecture
* Microservices Architecture

## Decision Outcome
I have changed my decision to Service-Oriented Architecture because it fixes the issues I have mentioned earlier. As mentioned again by [Richard & Ford, 2020] deployments for SOA have less risk than a large monolith because it divides the application into separately deployed domain services. It also improves the modularity which is necessary given how the application is quite large. For example if the Notification Service needs updating it will not impact the main Complaint Management Service.

Similarly, Microservices would be too complex for the system we are building as services would be very small and require extra infrastructure for orchestration, monitoring and testing [Richards, 2016]. For example, when creating the services we do not need to break them down too much further as this isn't a large scale project.

I researched further into Layered Architecture but ultimately came to the conclusion it would not be a suitable when considering future development and maintenance. While it is very simple, the tight coupling and low deployability means a small change in one layer requires redeployment of the entire system, which is not practical for an application with millions of users.

### Consequences
**Positive**
* Highly modular - beneficial for maintenance and scalability
* Easier deployment with less risk compared to monolithic structures
* Easy integration with external APIs (email, telephone services)

**Negative**
* Service orchestration complexity
* Performance overhead from inter-service communication = e.g. performance delay for notification service

### References
Richards, M., & Ford, N. (2020). Fundamentals of software architecture : an engineering approach. O’reilly.

Richards, M. (2016). Microservices vs. Service-Oriented Architecture [Review of Microservices vs. Service-Oriented Architecture]. O’Reilly Media, Inc. https://learning.oreilly.com/library/view/microservices-vs-service-oriented/9781491975657/
