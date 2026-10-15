# ADR 001: Stack Architecture

## Title

Adopt MQTT to Prometheus Exporter Architecture

## Status

Accepted

## Context

The Smart Garden project requires a system to collect, process, and visualize data from various IoT sensors deployed in the garden. The system needs to be scalable, easy to monitor, and capable of integrating with existing monitoring and logging tools like Prometheus, Grafana, and Loki.

## Decision

We decided to build an MQTT to Prometheus Exporter for the following reasons:

1. **MQTT Protocol**: 
   - MQTT is a lightweight messaging protocol ideal for IoT devices.
   - It allows for efficient, low-latency communication between sensors and the broker.

2. **Prometheus**:
   - Prometheus is a robust, open-source monitoring solution.
   - It provides powerful querying capabilities and integrates well with Grafana for visualization.
   - Prometheus supports time-series data, which is essential for monitoring sensor data over time.

3. **Grafana**:
   - Grafana is an open-source platform for monitoring and observability.
   - It provides beautiful, customizable dashboards for visualizing Prometheus metrics.
   - Grafana supports alerting based on Prometheus queries.

4. **Loki and Promtail**:
   - Loki is a horizontally scalable, highly available, multi-tenant log aggregation system inspired by Prometheus.
   - Promtail is an agent that ships the contents of local logs to a private Loki instance or Grafana Cloud.
   - This combination allows for centralized, structured logging, making it easier to debug and monitor the system.

## Consequences

1. **Scalability**:
   - The system is highly scalable due to the use of lightweight protocols and efficient data handling mechanisms.
   - Additional sensors and components can be added with minimal changes to the existing infrastructure.

2. **Monitoring and Observability**:
   - Using Prometheus and Grafana provides a powerful and flexible monitoring solution.
   - Loki and Promtail enable detailed logging, which helps in diagnosing issues and understanding system behavior.

3. **Complexity**:
   - The architecture introduces complexity in terms of setting up and maintaining multiple components (MQTT broker, Prometheus, Grafana, Loki, and Promtail).
   - Proper configuration and management are required to ensure smooth operation.

4. **Community and Support**:
   - All chosen tools are widely used in the industry and have strong community support.
   - Extensive documentation and resources are available, which helps in troubleshooting and extending the system.

## Alternatives Considered

1. **Using HTTP for Sensor Communication**:
   - Pros: Simpler setup, widely understood.
   - Cons: Higher overhead, less efficient for low-latency communication.

2. **Using InfluxDB for Time-Series Data**:
   - Pros: Specifically designed for time-series data, powerful querying capabilities.
   - Cons: Additional complexity in integrating with existing monitoring and logging tools.

3. **Using Elasticsearch for Logging**:
   - Pros: Powerful search capabilities, widely used.
   - Cons: More resource-intensive, higher complexity in setup and management.

## Conclusion

The chosen architecture, based on MQTT for communication, Prometheus for monitoring, Grafana for visualization, and Loki for logging, provides a scalable, efficient, and powerful solution for the Smart Garden project. It leverages well-established tools with strong community support, ensuring long-term maintainability and extensibility.

