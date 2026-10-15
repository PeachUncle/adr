# Decision to Require Transaction IDs (TXID) on HTTP Requests

## Status

**Proposed**

## Context

In modern distributed systems, understanding the flow of a request as it traverses various components is critical for observability, debugging, and performance optimization. By requiring **Transaction IDs (TXID)** on every HTTP request, the application can achieve deep telemetry insights into overall usage and behavior.

This approach becomes especially valuable in scenarios where:
- Multiple clients consume the service.
- Downstream components generate logs for shared processes.
- All logs are aggregated in a central log event storage system.

A standardized TXID enables correlating events across these services, helping to identify issues, measure performance, and understand user behavior at a granular level.

The concept aligns with the goals of Microsoft's **[Correlation Vector](https://github.com/microsoft/CorrelationVector)** framework, which introduces a lightweight, hierarchical identifier for distributed tracing and telemetry. The Correlation Vector serves as an example of how structured transaction identifiers can enhance telemetry capabilities.

## Decision

The application will require a **Transaction ID (TXID)** to be included in every HTTP request header. If a client does not provide a TXID, the application will generate one. All downstream services will propagate the TXID as part of their requests.

### Implementation Details

1. **HTTP Header**: The TXID will be included in the `X-Transaction-ID` header of every request.
2. **Automatic Generation**: If a client does not provide a TXID, the application will generate a unique identifier (e.g., a UUID).
3. **Propagation**: The application will propagate the TXID to all downstream services, ensuring end-to-end correlation.
4. **Logging**: All log entries will include the TXID to enable correlation across services.
5. **Hierarchy Support**: Adopt a hierarchical identifier structure inspired by the Correlation Vector framework. For example:
    - Root request: `1.0`
    - Downstream component: `1.0.1`
    - Further downstream: `1.0.1.1`
6. **Validation**: The server will validate the format of incoming TXIDs to ensure compliance with the expected structure.

## Consequences

### Benefits

- **Enhanced Observability**: TXIDs provide deep insights into request flows across distributed systems.
- **Centralized Analysis**: Correlating logs from multiple services becomes straightforward, aiding debugging and performance tuning.
- **Telemetry**: Enables advanced telemetry features, such as analyzing request lifecycles and detecting bottlenecks.
- **Compatibility with Standards**: The hierarchical TXID structure aligns with existing frameworks like Microsoft's Correlation Vector.
- **Debugging**: Simplifies root cause analysis by allowing developers to trace individual requests across services.

### Drawbacks

- **Overhead**: Managing and propagating TXIDs adds some overhead to the system.
- **Adoption Costs**: Clients must update their integrations to include TXIDs in their requests.
- **Complexity**: Enforcing a hierarchical structure requires additional validation logic.

## Alternatives Considered

1. **No TXIDs**:
    - Rejected because it limits the ability to correlate logs across services, reducing telemetry insights.
2. **Random UUIDs per Service**:
    - Rejected because it does not provide hierarchical insights into the flow of requests.
3. **OpenTelemetry Trace Context**:
    - Considered but rejected for this ADR, as TXIDs are more lightweight and directly aligned with this project’s immediate goals. OpenTelemetry could be explored in a future ADR.

## Implementation Plan

1. **HTTP Middleware**:
    - Implement middleware to handle TXID extraction or generation.
2. **Logging Integration**:
    - Update logging frameworks to include the TXID in log entries.
3. **Client Guidance**:
    - Document the `X-Transaction-ID` header requirement for clients in the API documentation.
4. **Telemetry Enhancements**:
    - Configure central log storage systems to index logs by TXID for easy querying.
5. **Hierarchy Validation**:
    - Implement validation logic for hierarchical TXID structures.

## Conclusion

Requiring TXIDs on all HTTP requests will significantly enhance the application’s telemetry capabilities, enabling deep insights into request flows and overall system behavior. By adopting a lightweight, hierarchical identifier structure inspired by Microsoft's Correlation Vector, this approach ensures compatibility with industry practices while meeting the project’s specific observability needs.
