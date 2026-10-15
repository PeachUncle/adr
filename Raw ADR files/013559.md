# 1. Use Spring AMQP

## Status
Accepted

## Context
In a message centric solution, routing of messages to the correct handler is both crucial and complex. Over time, those routing rules will change and we want a mechanism that allows for easy evolution of the system.

## Decision
Leverage the [Spring AMQP](https://spring.io/projects/spring-amqp) framework to manage the routing of messages in the system. AMQP has different type of exchanges that properly route Command and Event messages to interested consumers.

## Consequences
By taking advantage of an exiting framework, we can avoid writing code that really has nothing to do with the business. We want to focus on business value, taking advantage of the loose coupling that messaging provides.