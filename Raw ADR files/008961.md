# ADR 006: Configuration Management with Spring Cloud Config Server

## Status
Accepted

## Context
In a microservices architecture, managing configuration across multiple services can become complex. We need a centralized solution to handle configuration for our services, ensuring consistency and ease of management.

## Decision
We will use Spring Cloud Config Server to manage configurations for our services, including the Discovery Server (Eureka).

### Config Server Setup
- **Port**: The Config Server runs on port `8888`.
- **Profile**: Uses the `native` profile to serve configurations from the local classpath.
- **Configuration Source**: Looks for configuration files in `classpath:/configurations`.

### Discovery Server Configuration
- **Port**: The Discovery Server (Eureka) runs on port `8761`.
- **Eureka Settings**:
  - Does not register with another Eureka server (`registerWithEureka: false`).
  - Does not fetch registry from other Eureka servers (`fetchRegistry: false`).
  - Uses `localhost` as the hostname for local development.

## Consequences

### Positive
- **Centralized Configuration**: Simplifies management by centralizing configuration in the Config Server.
- **Consistency**: Ensures consistent configuration across environments.
- **Flexibility**: Allows dynamic configuration changes without redeploying services.

### Negative
- **Dependency**: Services depend on the Config Server being available at startup.
- **Single Point of Failure**: If the Config Server is down, services may not start correctly.

## Related Files

### `config-server/src/main/resources/application.yml`
- **Purpose**: Configures the Config Server.
- **Key Settings**:
  - Runs on port `8888`.
  - Uses the `native` profile to load configurations from the classpath.

### `config-server/src/main/resources/configurations/discovery-server.yml`
- **Purpose**: Provides configuration for the Discovery Server.
- **Key Settings**:
  - Sets the Discovery Server to run on port `8761`.
  - Configures Eureka settings for standalone operation.

## Alternatives Considered
- **Git-based Configuration**: Using a remote Git repository for configurations. Rejected due to the simplicity and speed of local file access in development environments.

## Implementation
- Ensure the Config Server is started before any dependent services.
- Place all service-specific configuration files in the `classpath:/configurations` directory of the Config Server.
