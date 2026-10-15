# 6. Architecture Pattern

Updated: 2024-04-14

## Status

Accepted

## Context
In the context of the course we are asked to build a microservice environment that is following an
Event-driven architecture (EDA) pattern.

We can choose one of the following four Event-driven architecture (EDA) patterns for our system:
* Event Notification
* Event-carried State Transfer
* Event Sourcing
* Command Query Responsibility Segregation (CQRS)

## Decision
We have decided to make use of the Event Notification pattern in most cases. Whenever there is a MQTT message
emitted from the FactorySimulator, we notify other services about the event via Kafka. This inverts
dependencies such that the station services are not dependent on the FactoryListener service, but rather
just listen to changes on the Kafka topic.

For the stock updates in the Warehouse we have decided to use the Even-carried State Transfer pattern.

## Consequences
The main benefit of using an Event-driven architecture (EDA) pattern is that it allows us to build a highly
decoupled system that is easy scalable and maintainable. It is more challenging to debug und maintain the
system, but the benefits outweigh the costs in our opinion.

By employing the Event Notification pattern we can easily add new services to the system without having to
worry about dependencies among then. This makes the system more flexible and easier to maintain. New servies
will just have to listen to the Kafka topic and react to the events that are emitted.

The Event-carried State Transfer pattern is used for the stock updates in the Warehouse. This pattern is
useful because we want to keep the stock information in the Warehouse service and additionally in the Order
service. Therefore, we don't need to contact the Warehouse service from the Order service if we want to check
the stock information. We can just listen to the stock updates on the Kafka topic and update the stock in the
Order service accordingly. This should improve the performance of the system and overall availability. On the
flip side, we have replicated data that could potentially get out of sync if not handled properly.

