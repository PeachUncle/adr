# Integrating a Message Broker to connect the AI tool with functions for multiple features

## Context
As the system grows in complexity and scale due to the multiple integrations with HR systems, the functions inside the ClearView system increasingly require asynchronous communication to manage the high volume of traffic and events. A possible synchronous point-to-point communication model creates bottlenecks, increasing latency and making the system fragile to failures in dependent services.

To address these issues, we use a message broker, which serves as an intermediary to facilitate the communication between the AI tool used by ClearView and the functions that manage AI results.

## Decision: 
The decision is to implement a message broker physical component, which would facilitate data transmission between various types of devices and consumers, over wired and wireless communication.

We have decided to integrate a message broker into our architecture to support asynchronous communication and improve scalability. The selected message broker is RabbitMQ.

## Status
Proposed

## Options
  * Open-Source Message Broker: A great option would be to use an open-source message broker software due to low cost, ability of the software to provide extended functionality and flexibility.
  * Synchronous communication model: This approach is very simple, as it does not require additions components, but this model demands immediate feedback or acknowledgment from the service that receives the message, which can affect the choice of message broker.
 
As was mentioned in the Context, we consider an open-source message broker such as RabbitMQ a great solution due to our desire to have asynchronous communication inside the system, be flexible and agile.

## Consequences
  * Observability and Monitoring: The message broker comes with built-in metrics and observability tools that allows for better monitoring of the entire system's health. We will be able to track message throughput, queue lengths, and processing times, allowing them to proactively detect and address bottlenecks or failures before they affect end users.
  * Agility: As changes to one service don’t directly affect others, we can always come up to improvements to the application. This architectural flexibility leads to increased agility, as new features or services can be introduced and tested with less risk, fostering a more innovative development culture.
  * Fault tolerance: Persistent messages improve system uptime, ensuring the application's functions remain reliable. Features like message retries and dead-letter queues help recover gracefully from errors without manual intervention.
  * Security and Encryption: The message broker supports encryption at rest and in transit, ensuring data remains protected as it moves between services. Sensitive data can be transmitted securely over the network, minimizing the risk of interception.
   

## Useful links
- [C4 diagram](https://github.com/octaviaah/ClearView/blob/main/2.ArchitectureVisualization/C4Diagram.md)
- [Architectural Decision Record 1 - Choose an architectural style](https://github.com/octaviaah/ClearView/blob/main/3.ADRs/ADR001-EventDrivenArchitecture.md)
