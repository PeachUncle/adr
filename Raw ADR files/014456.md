# 1. Rest API Versioning Strategy

## Status

Accepted

Date: 2025-06-19

## Context

As our service architecture grows and following Lean Agile practices with continuous deployment, we need a 
versioning strategy that:

- Supports rapid iteration and evolution of services
- Maintains reasonable backward compatibility
- Provides clear migration paths for clients
- Optimizes for development speed and maintainability
- Is easily understandable by API consumers
- Balances the cost of maintaining multiple versions

## Decision

We will implement URI-based versioning following these principles:

1. Version Format
   - Use semantic versioning in the URI path: `/v{major}.{minor}/`
   - Example: `/v1.2/customers/register`
   - Major version indicates significant architectural changes or high-maintenance cost changes
   - Minor version indicates iterative changes, including some breaking changes when maintenance cost is low

2. Version Lifecycle
   - Support multiple versions based on maintenance cost and business needs
   - Deprecate versions when maintenance cost exceeds benefits
   - Include deprecation headers for endpoints planned for removal
   - Deprecate the endpoints with a minimum of 3 months notice

3. Change Classification
   - Major version increment (when):
     - Code reuse is low
     - Changes make the codebase complex or complicated
     - Significant cognitive changes in API conventions
     - Complete restructuring of resources or business logic
   - Minor version increment (when):
     - High-code reuse is possible
     - Breaking changes with manageable maintenance cost:
       - Adding/removing required fields
       - Modifying field types
       - Changing response structures
     - Non-breaking changes:
       - Adding new endpoints
       - Adding optional fields
       - Extending enums
       - Bug fixes

4. Documentation Requirements
   - OpenAPI/Swagger documentation for each supported version
   - Changelog maintenance with clear indication of breaking changes
   - Migration guides for version transitions
   - Clear documentation of differences between versions

## Consequences

### Positive

- Faster API evolution and iteration
- Better alignment with Lean Agile practices
- Reduced overhead for small breaking changes
- Efficient code reuse across versions
- Clear cost-based versioning decisions
- Clear visibility of an API version in URIs

### Negative

- More complex version management
- Potential for more concurrent versions
- Higher importance of code design for reusability
- Increased URI length
- Additional deployment complexity

### Neutral

- Need for regular assessment of maintenance costs
- Importance of clear communication with API consumers
- Need for careful breaking change management

## Implementation Notes

1. URI Structure:
    ```
    https://api.example.com/v{major}.{minor}/{resource}/{id}
    ```

2. Version Header (for deprecation notices):
    ```
    Deprecation: date="2025-12-31"
    Sunset: date="2026-06-30"
    Link: <https://api.example.com/v2.0/customers>; rel="successor-version"
    ```

3. Version Management Strategy:
   - Design for code reuse between versions
   - Use feature flags for gradual rollout
   - Track version usage metrics
   - Regular assessment of version deprecation needs

## Related Documents

- [OpenAPI Specification 3.0.3](https://spec.openapis.org/oas/v3.0.3)

## Contributors

- Àlex Grau Roca
