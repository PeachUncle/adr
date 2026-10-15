# Architecture Decision Record (ADR)

**Title:** Event Streaming Broker Selection for IoT Data Processing

**Date:** [06/03/2024]

**Status:** Accepted

**Context:**

The Metrics Capturing System is tasked with the processing and analysis of data collected from a broad spectrum of IoT devices. Considering the typical characteristics of IoT data, such as the substantial amount of data coming from multiple sensors, it's essential to establish a robust event streaming system. This system must be adept at managing real-time data streams effectively, guaranteeing that data is swiftly processed and analyzed.

**Decision:**

After evaluating several event streaming brokers, the following brokers were identified as suitable for our IoT devices data:

1. **Apache Kafka**: A distributed streaming platform that is highly scalable, fault-tolerant, and capable of handling high volumes of real-time data.
2. **RabbitMQ**: An open-source message broker that supports multiple messaging protocols and is known for its robustness and ease of use.
3. **Apache Pulsar**: A cloud-native distributed messaging and streaming platform that offers low latency, high throughput, and scalability.
4. **Amazon Kinesis**: A fully managed service provided by AWS that can collect, process, and analyze real-time, streaming data.

**Rationale:**

- **Apache Kafka**: Offers high throughput, fault tolerance, and scalability, making it suitable for large-scale IoT data processing.
- **RabbitMQ**: Provides robust messaging capabilities and supports a wide range of messaging patterns, making it versatile for various IoT data processing needs.
- **Apache Pulsar**: Known for its low latency and high throughput, which are crucial for real-time data processing in IoT scenarios.
- **Amazon Kinesis**: Offers a fully managed service that simplifies the deployment and management of event streaming applications, making it an attractive option for teams already using AWS.

**Consequences:**

- **Pros:** The selected brokers offer a range of features that can meet the varying requirements of IoT data processing, from scalability and fault tolerance to low latency and ease of use.
- **Cons:** The choice of broker depends on the specific requirements of the project, including factors such as scalability, latency, and the existing technology stack.

**Decision Maker:** [Rami Chalhoub]

**Decision Approver:** [Kishore Allwynraj]

**Implementation Plan:**

1. **Initial Selection:** Based on the above analysis, the team will initially focus on **Apache Kafka** and **RabbitMQ** for their proven scalability and robustness.
2. **Technical Evaluation:** The team will conduct a technical evaluation of these brokers to assess their suitability for the project's specific requirements, including factors such as performance, scalability, and ease of integration.
3. **Integration:** Once the optimal broker is identified, the team will proceed with integrating it into the data processing pipeline for IoT devices data.
4. **Monitoring and Optimization:** After integration, the team will monitor the performance of the event streaming mechanism and optimize the configuration as necessary to ensure optimal performance.

**Review Date:** [06/03/2024]
