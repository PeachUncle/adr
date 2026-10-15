# ADR 0004: Docker-Based Environments Testing with Testcontainers

## Context:
The project consists of multiple microservices relying on Kafka for asynchronous communication and PostgreSQL for persistent storage. Testing locally without real infrastructure does not reproduce realistic service interactions. Additionally, deploying and running microservices consistently across environments requires containerization.

## Decision:
Adopt Docker as the standard for both deployment and testing, using Testcontainers for ephemeral integration and end-to-end (E2E) testing. Key points include:
- **Service containerization**: All microservices, databases, and Kafka brokers run as Docker containers in development, CI, and production-like environments.
- **Integration and E2E tests**: Testcontainers spins up ephemeral Kafka clusters and PostgreSQL instances, validating the full message flow and persistence.
- **Schema verification**: Works with Kafka + Schema Registry to ensure message compatibility between producers and consumers.
- **Environment consistency**: Docker ensures the same configurations, dependencies, and networking across developer machines and CI/CD pipelines.

## Rationale:
- **Isolation**: Each test runs in a fresh, independent environment, avoiding conflicts with local or shared services.
- **Realism**: Tests run against real Kafka and PostgreSQL instances, reflecting production-like behavior.
- **End-to-End Validation**: Ensures that messages produced are correctly consumed, processed, and persisted across the full flow.
- **Schema Verification**: Works seamlessly with Kafka + Schema Registry to validate message structures.
- **Embedded Kafka Limitation**: Embedded Kafka is lightweight but not fully representative of production clusters. It lacks multi-broker support, persistence guarantees, and realistic networking behavior.
- **Reproducibility**: Containers can be versioned and configured consistently, making CI/CD pipelines predictable and reliable.
- **Maintainability**: Tests are decoupled from developer machine setups and external dependencies.
- **Operational unification**: Using Docker for both deployment and testing simplifies CI/CD pipelines and reduces discrepancies between environments.

## Consequences:
- **Longer execution time**: Integration tests take more time compared to embedded tests.
- **Resource overhead**: Requires CPU and memory to run ephemeral containers for each test.
- **Operational complexity**: Requires managing Docker-based test lifecycles and cleanup, and building all images can be time-consuming.
- **High confidence in correctness**: Despite cost, Testcontainers ensures tests are realistic, catching issues that unit or embedded tests would miss.
