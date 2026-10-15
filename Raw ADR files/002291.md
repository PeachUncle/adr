# 2. System design assumptions and decisions

Date: 2023-07-01

## Status

Accepted

## Context

In the context of building an API to be used for opening a new "current account" of already existing customers, this
architectural decision record covers critical context and assumptions regards the system design.

## Decision

The system design reflects the use of microservice architecture, although this might currently be an overkill for the 
current simple acceptance criteria or requirements - it aims to illustrate knowledge of microservice architecture and 
event-driven systems.

## Consequences

Based on this decision, a structural difficulty is being introduced to in achieving our requirements. The decision to use
a microservice architecture results to having 2 independent services (AccountService, TransactionService) to achieve this 
simple and straightforward task, therefore extending the completion time of the assessment.

Two, it adds more early complexity to system design because there's a need to now manage and maintain the event transmission
between the 2 independent services.

Three, a complete system design using the microservice architecture requires the use of an API gateway/routing system that 
will not be covered in this assessment.

Four, the current implementation will illustrate a form of event-driven system between AccountService and TransactionService.
Also, taking into consideration that due to the availability of limited infrastructure for the assessment, the event communication
between the two services will be carried out using HTTP/REST calls - there are several risks of doing, like events getting lost
during to a downtime in a service. A future good solution to this is to use a data store or message broker like Kafka, RabbitMQ
et al. to manage the inter-service event communication.

Lastly, a benefit of this particular system design decision is to enable that our services are future-proof, individually 
scalable, flexible and help us take advantage of many benefits using the microservice architecture compared to monolith. 
See [advantages](https://www.atlassian.com/microservices/microservices-architecture/microservices-vs-monolith)