# 1. Use Spring Pulsar

## Status
Rejected

## Context
Working with the Pulsar Java library requires boilerplate code and an understanding of numerous options. A simpler programming model would improve the developer experience.

## Decision
~~We will use the [Spring for Apache Pulsar](https://github.com/spring-projects-experimental/spring-pulsar) project to develop the gateways to Pulsar.~~ Spring Integration currently integrates only with RabbitMQ and we want to leverage it to keep the code simple. Although it should be possible to host Pulsar in our Kubernetes cluster, we were unable to get it to come all the way up.  For that reason, we'll be using RabbitMQ as our message broker.

## Consequences
The project is in its infancy but seems to have progressed nicely, supporting the features that this project needs. As new milestones come up, we will upgrade as well as report any bugs found during development.