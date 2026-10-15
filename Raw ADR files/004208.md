# ADR-005: Data Acquisition Approach

## Date:
2024-04-03

## Status:
Accepted

## Context:
The context for this decision is to define the data acquisition approach for Fishy Watch, including techniques to acquire data from hardware devices and communication protocols for seamless integration between hardware and software.

## Decision:
After evaluating the requirements and considerations, we have defined the following data acquisition approach for Fishy Watch:

### Techniques for Data Acquisition from Hardware:
1. **Direct Sensor Integration**:
   - Utilize APIs or drivers provided by hardware manufacturers to directly integrate sensors with the software system.
   - Examples: Using libraries or SDKs for water monitors, underwater cameras, and fish-ual recognition devices.

2. **IoT Protocols**:
   - Use IoT protocols such as MQTT (Message Queuing Telemetry Transport) or CoAP (Constrained Application Protocol) for data exchange between hardware devices and the software backend.
   - Implement MQTT or CoAP clients on hardware devices to publish data to MQTT brokers or CoAP servers.

3. **Edge Computing**:
   - Employ edge computing techniques to process and filter data at the edge (near the hardware devices) before sending relevant data to the central software system.
   - Use edge devices or gateways to preprocess data, reduce latency, and optimize bandwidth usage.

### Communication Protocols:
1. **With Internet Connectivity**:
   - **HTTP/HTTPS**: Use RESTful APIs over HTTP/HTTPS for communication between hardware and software when internet connectivity is available.
   - **MQTT over TCP/TLS**: Implement MQTT over TCP/TLS for efficient and reliable communication, especially for real-time data streaming and command/control operations.

2. **Without Internet Connectivity**:
   - **Local Network Communication**: Use local network protocols such as UDP or TCP/IP for communication between hardware and software within the same network, suitable for offline environments.
   - **Offline Data Storage and Sync**: Implement mechanisms for offline data storage on hardware devices and periodic synchronization with the central software system when connectivity is restored.

## Consequences:
### Pros:
- Efficient Data Acquisition: Using direct sensor integration and IoT protocols ensures efficient and real-time data acquisition from hardware devices.
- Scalability: Edge computing techniques enable scalable data processing at the edge, reducing load on the central system.
- Internet Connectivity Flexibility: Supporting multiple communication protocols facilitates communication with and without internet connectivity.
- Reliability: Implementing reliable protocols like MQTT over TCP/TLS ensures secure and robust communication between hardware and software.

### Cons:
- Complexity: Managing multiple data acquisition techniques and communication protocols adds complexity to system architecture and implementation.
- Compatibility: Ensuring compatibility and interoperability between hardware devices and software components may require careful integration and testing.
