# ADR.1 Architecture Style

## Status `APPROVED`

## Description

The microkernel architecture consists of a core system and plug-in modules. The core system contains general business logic, and the plugins implement additional cases, rules and features, as well as specialized processing. The plug-in modules are usually independent components that extend the core system to produce additional business capabilities.

The event-driven architecture is a distributed asynchronous architecture pattern. It has 2 common implementation approaches - mediator topology and broker topology. The first approach relies on a central event mediator, whereas in the second approach the messages are distributed across event processors through a lightweight message broker providing the necessary event channels. 

## Rationale

For the Road Warrior implementation, we need a cost-effective easy-to-deploy and flexible architecture style that allows continuous system extension with additional functionalities and data sources. In addition, we have one central domain - Reservations - and almost all functionalities are related to this domain.

We believe that microkernel architecture style is very suitable for our context. We will create a core component (Reservation Persister), without which the system cannot work. Around this core, we will have "write" plugins, that can be both subdomain partitioned (airline, hotel, car rental, train) and technically partitioned (email parser, agency booking feeds, GDS interfaces, etc). Also, we will have several "read" plugins - dashboard presenter, single reservation viewer, trip sharer, bulk data provider.

In addition, we need a simple event processing flow to capture the reservations coming from various sources. The most common implementation approach is to apply event-driven architecture, where different event processors will process the incoming reservations and will publishing events ready for registration by the core component (Reservation Persister).

## Decision

We are designing a **hybrid** architecture combining the key aspects of the **microkernel** architecture and **event-driven** architecture pattern with broker topology.

## Consequences

### Positive

Combining microkernel and event-driven architecture, we will achieve:

 - Agility
 - Extensibility
 - Ease of deployment
 - Scalability at plug-in feature level

### Negative

Combining microkernel and event-driven architecture, we will have the following challenges:

 - Complex development due to asynchronous communication and integration of large number of plugins
