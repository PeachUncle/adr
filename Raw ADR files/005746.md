---
id: adrs-adr002
title: 'ADR002: Collection and Sending of Merchant Payment Metrics to Prometheus in the SDK'
description: >
   Architecture Decision Record (ADR) to Collect and Send of Merchant Payment Metrics to Prometheus in the SDK
---
*Status: [Superseded]*


## Context

Merchants need to collect metrics related to payments made using the SDK we provide. These metrics are crucial for monitoring system performance, 
identifying bottlenecks, and detecting potential errors. they also need a centralized way to store and visualize these metrics.

## Decision

We have decided to integrate a metrics collection feature into our  SDK, which will send these metrics to a centralized Prometheus server. 
The SDK  enables the creation of a local client metrics server, which will collect the metrics during its usage before sending them to a centralized internal Prometheus instance.

## Considered Alternatives
* Custom Metric Storage: We considered a custom solution for payment metric storage but acknowledged its potential limitations compared to the robust features of Prometheus. While custom solutions offer tailored development, they might lack Prometheus' real-time visualization capabilities. Developing additional services for data retrieval and customization might be needed in a custom approach.

## Consequences
Pros:

* Centralization of payment metrics for global analysis.
* Ease of integration with the existing Prometheus instance.
* Utilizing Prometheus allows for real-time visualization of metrics.
* Prometheus is known for its scalability, making it well-suited for handling increasing volumes of metrics as the system expands.

Cons:

* Potential Network Latency : Sending metrics from the SDK to a centralized Prometheus server introduces network communication. Depending on the network conditions, there could be potential latency issues in metric transmission, impacting real-time monitoring
* Dependency on  Promotheus server : Relying on a centralized Prometheus server introduces a dependency. Any disruptions or outages in the Prometheus server may temporarily impact the ability to collect and analyze metrics
* Additional complexity in the SDK for metrics collection and exposition.


## Additional Documentation
[Prometheus Metric Exposition Documentation](https://prometheus.io/docs/instrumenting/exposition_formats/) 
