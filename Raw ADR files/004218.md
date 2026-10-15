# ADR-015: Communication Protocols for Hardware and Software

## Date:
2024-04-04

## Status:
Accepted

## Context:
The context for this decision is to define the communication protocols between hardware devices (sensors, cameras, etc.) and software components in the Fishy Watch system, considering both online and offline scenarios with or without internet connectivity.

## Decision:
After evaluating connectivity requirements, data transfer needs, reliability, and compatibility with hardware devices, we have identified the following communication protocols for Fishy Watch:

### Communication Protocols with Internet Connectivity:
1. **MQTT (Message Queuing Telemetry Transport)**:
   - Use MQTT for lightweight, publish-subscribe messaging between hardware devices and cloud-based software.
   - MQTT is suitable for real-time data streaming, asynchronous communication, and efficient resource utilization.

2. **HTTP(S) RESTful APIs**:
   - Implement RESTful APIs over HTTP or HTTPS for bi-directional communication, data retrieval, and command execution between hardware and software.
   - RESTful APIs provide standardization, scalability, and interoperability with web-based systems and services.

### Communication Protocols without Internet Connectivity (Local Network):
1. **MQTT-SN (MQTT for Sensor Networks)**:
   - Use MQTT-SN for communication within local sensor networks, allowing MQTT-like messaging over constrained networks.
   - MQTT-SN supports topic-based communication, QoS levels, and lightweight protocols suitable for low-power devices.

2. **CoAP (Constrained Application Protocol)**:
   - Employ CoAP for resource-constrained devices and low-power networks, offering RESTful communication, efficient message formats, and scalability.
   - CoAP supports UDP-based communication, asynchronous messaging, and resource discovery in local network environments.

3. **Custom Binary Protocols**:
   - Develop custom binary protocols optimized for low-latency, high-throughput communication between hardware and software components.
   - Custom protocols can be tailored to specific data formats, device constraints, and network conditions for efficient data exchange.

## Consequences:
### Pros:
- Defined communication protocols cater to diverse connectivity scenarios, including internet-connected and local network environments.
- MQTT, HTTP(S), MQTT-SN, and CoAP offer standardized, reliable, and scalable communication for data transfer, command execution, and status updates.
- Custom binary protocols provide flexibility and performance optimization for specialized hardware communication requirements.

### Cons:
- Managing multiple communication protocols requires protocol-specific implementations, configuration, and maintenance efforts.
- Compatibility and interoperability challenges may arise when integrating hardware devices with software components using different protocols.
