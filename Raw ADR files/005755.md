de000---
id: adrs-adr005
title: "ADR005: Business metrics aggregation"
description: >
  Architecture Decision Record (ADR) to implement a business metrics aggregation API for the client SDK
---

*Status: [Closed]*

## Background

Previously, the metrics implementation was done in a way to provide comparison and tracking of requests sent against requests received. These technical metrics, more or less, are used essentially for monitoring purposes and detecting divergences. The business metrics however are not provided to the client yet.

## Context

The context for this ADR is to propose two ways to fulfil the client need for a business metrics API that can be conveniently used to hydrate a dashboard. These metrics can also encompass the technical ones which were previously provided.

To address this need, we have decided to :
- Create a new service : Metrics service. This service will be responsible for providing the metrics to the client.
- Provide the client with an API in our SDK to retrieve the metrics from the newly created service.

The general rational is that this new SDK API will have to consume a metrics endpoint in our **Metrics Service**. However, this latter service itself needs a way to aggregate the desired information in order to serve it back.

## Proposed Solutions

### Solution 1: Implementing an event-sourcing based CDC pattern  

Description: Implementing Change Data Capture (CDC) using an event-based approach to aggregate metrics.

#### High-level view of the architecture and the interactions : 

![CDCArchitecture](https://github.com/pns-si5-al-course/al-newbank-23-24-al-23-24-b-v5/blob/main/adr/images/cdc-architecture.svg)

#### Pros : 
- Real-time data updates: Event-based CDC allows for real-time updates to metrics as transactions occur and services get consumed.
- Scalability: This approach can scale effectively, accommodating a growing volume of data changes without the need of long running batch jobs to select the updates and insert them manually

#### Cons :
- Implementation complexity: Setting up an event-based CDC system introduces a lot of complexity to the architecture in order to properly configure the newly added connectors.
- Resource consumption: Continuous monitoring of data changes will increase resource consumption. We are not sure if our hardware can handle this additional weight.

### Solution 2: Creating CronJob Services to mimick an async CDC pattern

Description: Implementing CronJob services to periodically poll and process data changes, mimicking an asynchronous CDC pattern.

#### High-level view of the architecture and the interactions : 

![CronArchitecture](https://github.com/pns-si5-al-course/al-newbank-23-24-al-23-24-b-v5/blob/main/adr/images/cron-architecture.png)

#### Pros:
- Simplicity: CronJob services are straightforward and easy to implement 
- Light resource usage: Scheduled jobs consume less resources usage by only running periodically at specified intervals.

#### Cons:
- Complexity in keeping track of last changes: Maintaining accurate timestamps or tracking mechanisms can be complex, potentially leading to inaccuracies in metrics.
- Scalability concerns with huge inserts and selects: As data grows, the solution might struggle to handle large amounts of data inserts and selects, impacting performance.

## Decision 

The event-based CDC was adopted to aggregate metrics from both the sharded redis data store that the services interact with when issuing a transaction and the postgres database which keeps tracks of all successful transactions which eventually get settled.
