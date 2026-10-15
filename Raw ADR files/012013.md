# ADR 003: Configuration Approach

## Title

Use Environment Variables for Configuration

## Status

Accepted

## Context

The MQTT to Prometheus Exporter requires several configuration parameters, such as the address and port of the MQTT broker, the MQTT topic to subscribe to, and the port for the Prometheus metrics server. The configuration needs to be flexible to allow easy changes without modifying the source code.

## Decision

We decided to use environment variables for configuring the project. This approach includes the following considerations and practices:

1. **Environment Variables**:
   - Use environment variables to configure essential parameters such as `MQTT_BROKER`, `MQTT_PORT`, `MQTT_TOPIC`, `PROMETHEUS_PORT`, and `RETRY_INTERVAL`.
   - Environment variables provide a flexible way to manage configuration, making it easy to change settings without altering the code.

2. **Docker Compose Integration**:
   - Configure environment variables in the `docker-compose.yml` file to ensure they are correctly set when the Docker containers are started.
   - This allows for easy deployment and management of configuration in containerized environments.

3. **Default Values**:
   - Implement default values for environment variables in the code to handle cases where variables are not set.
   - This ensures the application can run with sensible defaults and reduces the risk of misconfiguration.

## Consequences

1. **Flexibility**:
   - Environment variables provide a flexible way to manage configuration, allowing easy changes without modifying the source code or rebuilding the application.
   - They support different configurations for development, testing, and production environments.

2. **Simplicity**:
   - Using environment variables simplifies the configuration management process, especially in containerized environments.
   - It reduces the complexity of configuration files and makes it easier to understand and manage configuration settings.

3. **Security**:
   - Environment variables can securely store sensitive information, such as passwords and API keys, without hardcoding them into the source code.
   - However, care must be taken to ensure that environment variables are managed securely and not exposed in logs or version control.

4. **Environment Management**:
   - Requires careful management of environment variables to ensure consistency across different environments (development, staging, production).
   - Environment variables must be documented clearly to ensure that all required variables are set correctly.

## Alternatives Considered

1. **Configuration Files**:
   - Pros: Centralized configuration, easy to version control.
   - Cons: Requires parsing configuration files, more complex to manage in containerized environments.

2. **Command-Line Arguments**:
   - Pros: Easy to override for specific runs.
   - Cons: Less flexible for containerized environments, harder to manage for multiple parameters.

3. **Hardcoded Values**:
   - Pros: Simplest approach, no external dependencies.
   - Cons: Inflexible, requires code changes for configuration updates, insecure for sensitive information.

## Conclusion

Using environment variables for configuration provides a flexible, simple, and secure way to manage the configuration of the MQTT to Prometheus Exporter. This approach integrates well with Docker Compose and supports different configurations for various environments, ensuring the project can be easily deployed and maintained.
