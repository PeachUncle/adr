---
id: adrs-adr009
title: "ADR009: Enhancing Metrics service Availability with an Active-Active Redundancy Pattern"
description: >
    Architecture Decision Record (ADR) to enhance the availability of the Metrics service by implementing an Active-Active redundancy pattern.
---

*Status: [Final]*

## Background

The Metrics service is an extremely sollicited component of the NewBank system. It is responsible for aggregating and providing metrics to the client SDK to be visualized on dashboards. The service is currently deployed on a single node, which is a single point of failure. If the node fails, the service will be unavailable until the node is restored.
## Context

The context for this ADR is to propose a solution to enhance the availability of the Metrics service by implementing an Active-Active redundancy pattern.

## Decision

We decided to implement an Active-Active redundancy pattern to enhance the availability of the Metrics service. This pattern consists of deploying multiple instances of the Metrics service on different nodes. Each instance will be responsible for aggregating and providing metrics to the client SDK. If one instance fails, the other instances will continue to provide metrics to the client SDK.

## Consequences

### Pros:

* **High Availability:** The Active-Active redundancy pattern ensures that the Metrics service is always available, even if one of the instances fails.
* **Scalability:** The Active-Active redundancy pattern allows for horizontal scaling of the Metrics service. If the load on the service increases, we can deploy more instances to handle the load.
* **Fault Tolerance:** The Active-Active redundancy pattern ensures that the Metrics service is fault tolerant. If one instance fails, the other instances will continue to provide metrics to the client SDK.

### Cons:

* **Increased Resource Consumption:** The Active-Active redundancy pattern increases the resource consumption of the Metrics service. We need to deploy multiple instances of the Metrics service, which will increase the resource consumption.
* **MongoDB bottleneck:** Both instances of the Metrics service will be using the same MongoDB database. This can lead to a bottleneck if the load on the service increases.




