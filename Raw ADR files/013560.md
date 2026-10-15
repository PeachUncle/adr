# 1. Use Spring HATEAOS

## Status
Accepted

## Context
Hypermedia has existed for quite some time and is potentially useful on both the client and server side. The key notion is that the response payload contains links to allowable operations, guiding the UI through the workflow.  Although we currently do not have plans to drive the UI, we do support the notion of an explicit context for all of our identifiers. Hypermedia and the HAL format supports that.

## Decision
Leverage the [Spring HATEOAS](https://spring.io/projects/spring-hateoas) framework to manage the hyperlinks provided in API responses. The framework simplifies the management of links, including understanding location of the application sitting behind an API Gateway or proxy.  Being a Spring project, it understands the programming model used, greatly reducing the amount of configuration and code required to support hypermedia.

## Consequences
By taking advantage of an exiting framework, we can use the linking concepts in the HAL format to ensure we're always using identifiers in an explicit context. In theory, the UI could be modified to take advantage of hypermedia to drive the workflow of operations. Using HAL, however, might prove to be a complication if we decide to introduce GraphQL. It is unclear how HAL can be generated when combining results from different services. 