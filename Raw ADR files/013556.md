# 1. Use Spring Integration

## Status
Rejected

## Context
The solution is centered around messaging and its accepted patterns, as described in [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/). Implementing those patterns should not be a concern of the project, allowing the team to focus on business value.

## Decision
We will not use [Spring Integration](https://spring.io/projects/spring-integration) be our implementation of those patterns. While we anticipate using some of the patterns, we want to keep things simple until something more complex is needed.

## Consequences
We'll either have to hand code messaging patterns or we'll have to look into other frameworks, e.g. [Spring AMQP](https://spring.io/projects/spring-amqp)