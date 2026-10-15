# Decision to Implement Client Registration via API Keys

## Status

**Proposed**

## Context

To ensure secure and controlled access to the API, a mechanism is required to authenticate and identify clients making requests. Implementing client registration via **API keys** provides a straightforward yet effective method for achieving this. Each client will be issued a unique API key during the registration process, which they must include in the `Authorization` header of every request.

Client registration will be handled by an **external system** dedicated to managing API clients. This external system will handle client creation, API key issuance, and lifecycle management, ensuring the core API remains focused on its primary responsibilities.

This approach not only helps track and manage API usage per client but also lays the foundation for integrating authentication and authorization mechanisms, such as role-based access control (RBAC). This integration would further align with the ADR on [enforcing authentication and authorization](link-to-authentication-authorization-adr).

## Decision

The API will enforce client registration and require an API key to be passed with every request. Clients will use the following header format:

```
Authorization: ApiKey <client-api-key>
```

### Implementation Details

1. **Client Registration via External System**:
    - An external system will provide APIs for registering clients and managing their API keys.
    - Example registration API payload:
      ```json
      {
        "client_name": "Example Client",
        "email": "example@client.com"
      }
      ```
    - The external system will generate a secure, unique API key for each registered client and return it in the response.

2. **API Key Validation**:
    - Each incoming request to the core API will validate the API key against the external system's validation service or a synchronized cache of valid keys.
    - Invalid or missing API keys will result in a `401 Unauthorized` response.

3. **Client Management**:
    - The external system will provide endpoints for managing API keys (e.g., revoke, regenerate):
        - `DELETE /clients/{id}/api-key`: Revoke an API key.
        - `POST /clients/{id}/api-key`: Regenerate an API key.

4. **Telemetry and Monitoring**:
    - Log API usage per client to support monitoring and billing (if applicable).
    - Track metrics like request counts, error rates, and data usage per API key.

5. **Integration with Authentication and Authorization**:
    - Combine API key-based client identification with user-level authentication and RBAC for sensitive endpoints.
    - Use the client ID associated with the API key to enforce additional access policies.

## Consequences

### Benefits

- **Enhanced Security**: Ensures only registered clients can access the API.
- **Client Accountability**: Enables tracking of client-specific API usage and behavior.
- **Foundation for Authorization**: Facilitates integration with RBAC for fine-grained access control.
- **Scalability**: Offloads client registration and management to an external system, ensuring the core API remains lightweight.
- **Telemetry**: Provides insights into API usage patterns, helping optimize performance and resource allocation.

### Drawbacks

- **Dependency on External System**: Adds a reliance on an external service for client registration and API key management.
- **Implementation Complexity**: Requires coordination between the external system and the core API.
- **Client Burden**: Requires clients to implement logic for securely storing and including API keys in requests.

## Alternatives Considered

1. **Anonymous Access**:
    - Rejected because it does not provide accountability or security for sensitive data and operations.

2. **OAuth 2.0**:
    - Considered for its robust authentication and authorization features but deemed unnecessary as a first step.
    - Could be revisited in conjunction with API key-based client registration for advanced use cases.

3. **Static Tokens**:
    - Rejected because static tokens do not provide flexibility for client management and revocation.

## Implementation Plan

1. **External System Integration**:
    - Configure the core API to interact with the external client registration system for API key validation.

2. **Middleware**:
    - Implement middleware in the core API to extract and validate the API key for each request using the external system.

3. **Logging and Telemetry**:
    - Integrate API key usage metrics into the telemetry system.

4. **Documentation**:
    - Update API documentation with instructions for client registration and API key usage.
    - Provide references to the external system's client registration API.

## Conclusion

Implementing client registration via an external system with API keys enhances the API’s security and observability while providing a foundation for future integration with authentication and authorization mechanisms like RBAC. This approach balances simplicity and effectiveness, ensuring secure and controlled access to the API for all clients while delegating client lifecycle management to a specialized service.
