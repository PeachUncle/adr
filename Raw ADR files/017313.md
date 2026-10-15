### **Status:** Selected

### **Date:** 07.07.2025

### **Author:** Pohorilets Vladyslav 

## **Context**:

We plan to split the current app into small microservices (weather, subscriptions, emailers, metrics). These services need a way to talk to each other. The tool must:

- work well with Node.js and Docker;
- let services send messages without waiting long;
- retry messages if something fails;
- scale when we add more messages or more services;
- be easy to monitor and fix.

## Reviewed options:

1. **RabbitMQ**
   Pros:
    - Easy to understand, lots of guides
    - Light on resources, simple Docker image
    - Friendly UI for queues and metrics
    - Good plugins for retries and dead-letter queues

    Cons:
    - Needs extra care for high traffic (clustering, tuning)
    - Stateful, so scaling is not as simple as adding pods

2. **Apache Kafka**
   Pros:
    - Very high throughput, good for event streams
    - Keeps messages for long time, supports replay

    Cons:
    - Heavy setup, many moving parts (Zookeeper or KRaft)
    - Steeper learning curve for developers
    - Overkill for our current message volume

3. **Redis Pub/Sub / Streams**
   Pros:
    - Super fast, in-memory
    - We already use Redis as cache

    Cons:
    - Data loss if Redis restarts (unless we enable AOF/RDB)
    - Basic delivery features, no built-in retries
    - Streams API still young, less tooling

4. **Direct HTTP (REST) API**
   Pros:
    - No extra infra, simple to start
    - Human-readable, easy to test with curl/Postman
    - Fits simple request/response actions

    Cons:
    - Tight coupling, caller waits for receiver
    - Harder to add retries and back-pressure
    - Not great for fire-and-forget jobs
    - Verbose payloads, more network overhead

5. **gRPC calls**
   Pros:
    - Fast and efficient protobuf messages
    - Built-in streaming and bi-directional channels
    - Strong typed contracts with code generation

    Cons:
    - Needs learning curve and extra tooling
    - Less human-readable; harder to debug manually
    - Still synchronous, caller must wait (unless we add queues)

## Decision taken:
Pick **gRPC** for service-to-service communication

## Arguments

- One clear way for services to call each other. No extra broker to run.
- gRPC is very fast. Small binary messages mean less network cost.
- We get strong contracts with protobuf, so the compiler catches many bugs.
- Built-in streaming works great for live data like weather updates and metrics.
- Runs fine in Docker and Kubernetes. Scaling is just adding more pods.

## Consequences:

Positive
- Less infrastructure
- Lower latency. Calls feel almost real-time
- Auto-generated client code
- Streaming lets us push data instead of polling

Negative
- Calls are synchronous. If a service is down we must retry or handle errors fast
- Not as easy to debug by hand as plain HTTP or a queue UI
- Team needs to learn protobuf and the tooling