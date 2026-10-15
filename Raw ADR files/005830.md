#  Redundant MQTT Brokers for Increased Reliability

**Date:** 2025-09-02  

## Status

Accepted  

## Context

In [ADR 0017: Migration to Private Servers with GitHub CI/CD Pipeline for Automated Deployment](./0017-migration-to-private-servers.md) we moved our deployment infrastructure from the university server to two privately managed servers.  
In [ADR 0009: Use MQTT as Communication Protocol](./0009-use-MQTT-as-communication-protocol.md) it was decided that all microcontrollers (e.g., Arduino MKR WiFi 1010) communicate with the backend using **MQTT** and a predefined JSON format with externally specified topic structure.  

Initially, a single MQTT broker instance was used. While this fulfilled the communication requirements, it introduced a **single point of failure**: if the broker became unavailable, all sensor data transmission and backend communication would stop.  

To mitigate this risk and increase availability, we evaluated the use of multiple MQTT brokers.  

## Decision

We migrated from a single MQTT broker to **two MQTT brokers running on different private servers**.  

Both brokers use the same configuration regarding authentication, topic structure, and message format.  
Clients (microcontrollers and backend consumers) are configured to support multiple broker endpoints, ensuring continued operation if one broker fails.  

This setup provides fault tolerance and improved reliability without changing the externally mandated MQTT protocol or topic/message format.  

## Consequences

* **Improved Reliability:** System remains operational even if one broker/server fails.  
* **Load Distribution:** Depending on client configuration, the two brokers can share traffic, preventing overload.  
* **Configuration Overhead:** Clients must be configured with multiple broker endpoints, which adds minor complexity.  
* **Operational Costs:** Running two brokers increases resource usage and administrative overhead.  
* **Consistency Management:** If both brokers operate independently (no clustering), ensuring synchronized state (e.g., retained messages) may require additional mechanisms.  
