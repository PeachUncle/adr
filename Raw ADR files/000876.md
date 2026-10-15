# ADR: Separation of WebAPI and Background Processing Services

## Decision Group

TD - Technology Decision

Proposed: 2024-11-10

## Problem/Issue

The current architecture combines the WebAPI and background processing services within a single deployment, leading to potential downtime during updates, maintenance, or failures in the background services. This impacts the perceived uptime from the client's perspective and could hinder scalability and flexibility.

## Decision

We have decided to separate the WebAPI from the background processing services. This decision is made to improve the perceived uptime for client applications, enhance system scalability and flexibility, and ensure a robust and fault-tolerant architecture. The WebAPI will immediately acknowledge client requests with a 202 Accepted response and enqueue these requests into Kafka for asynchronous processing by the background services.

## Considered Alternatives

- **Maintaining a Monolithic Architecture:** Keeping the WebAPI and background services together in a single deployment.
- **Serverless Functions:** Utilizing serverless computing models for background processing tasks.
- **Dedicated Queuing System Within the Application:** Implementing a custom queuing mechanism internally without separating services.

## Arguments

### Pro

- **Improved Availability and Fault Isolation:** Separating the WebAPI from background services allows for independent deployments, reducing downtime risks for the public interface and isolating faults.
- **Scalability:** Each component (WebAPI and background services) can be scaled based on their specific demands, optimizing resource utilization.
- **Asynchronous Processing:** Leveraging Kafka for event-driven architecture enhances the system's ability to handle high volumes of requests asynchronously, improving responsiveness and throughput.
- **Enhanced User Experience:** Immediate acknowledgment of client requests (202 Accepted) maintains a smooth user experience, even when the system is under heavy load.
- **Operational Flexibility:** Independent deployment and scaling provide the flexibility to update or maintain background services without affecting the WebAPI, and vice versa.

### Con

- **Increased System Complexity:** Introducing Kafka and managing two separate components adds to the architectural and operational complexity.
- **Operational Overhead:** Requires sophisticated monitoring and management tools to ensure seamless integration and communication between the WebAPI and background services.
- **Eventual Consistency Challenges:** Asynchronous processing introduces eventual consistency, necessitating additional strategies for handling data freshness and real-time requirements for some clients.

## Related Decisions

N/A

## Extends

N/A

## Related Requirements

N/A
