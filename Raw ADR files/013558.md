# 1. Use Message Routing

## Status
Accepted

## Context
In a message centric solution, routing of messages to the correct handler is both crucial and complex. Over time, those routing rules will change and we want a mechanism that allows for easy evolution of the system.

## Decision
Leverage the [Message Router](https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageRouter.html) pattern both at the external (AMQP) and internal (Spring Integration) messaging levels. In particular, messages should provide a `label` field that can be used to make routing decisions based on pattern matching.

## Consequences
Altering what component handles a particular class of message should be a trivial configuration change, requiring only small code changes.  For example, one day the label `command.character.new` could be routed to a component that handles all character commands but on the next day, that same label could be routed to a component dedicated to handling that command only.  Such flexibility should reduce the maintenance cost of the system. AMQP specifies the `Topic Exchange` and Spring Integration the `HeaderValueRouter` for just this purpose.