# ADR-008: API Versioning Strategy for Spring Boot Application

## Status
Accepted

## Date
2025-03-01

## Context
As our application evolves, we will need to make changes to our APIs to support new features, fix issues, or improve design. Some of these changes might be breaking changes that could disrupt existing clients. We need a clear strategy for versioning our APIs that:

- Allows us to evolve our APIs without breaking existing clients
- Provides a clear migration path for clients when breaking changes are necessary
- Balances maintainability of our codebase with backward compatibility
- Establishes clear guidelines on when and how to version APIs
- Defines how long older API versions should be supported
- Works well with our Spring Boot application architecture
- Integrates with our API documentation approach

Without a well-defined versioning strategy, we risk either breaking client integrations with each API change or creating an unmaintainable codebase with numerous parallel implementations.

## Decision
We will implement an API versioning strategy with the following key elements:

### 1. Versioning Approach
We will use **URI Path Versioning** where the version is included in the URL path:

```
/api/v1/customers
/api/v2/customers
```

This approach was selected because:
- It's explicit and visible in API calls
- It's easily testable with standard tools
- It works well with API documentation tools
- It allows for clear separation in routing and implementation
- It's intuitive for API consumers

### 2. Version Numbering
- We will use a major version number only (v1, v2, etc.)
- Major version numbers will increment only for breaking changes
- Breaking changes include:
  - Removing or renaming fields in responses
  - Adding required fields to requests
  - Changing field types or formats
  - Changing response status codes
  - Removing endpoints
  - Significantly changing behavior of existing endpoints

### 3. Implementation Strategy
- Each API version will have its own controller classes
- Controllers for different versions will be organized in version-specific packages:
  ```
  com.example.api.v1.CustomerController
  com.example.api.v2.CustomerController
  ```
- We will use separate DTOs for each version when breaking changes are needed:
  ```
  com.example.api.v1.dto.CustomerDTO
  com.example.api.v2.dto.CustomerDTO
  ```
- Service layer will be version-agnostic where possible
- We will use mappers to convert between version-specific DTOs and internal domain models

### 4. Version Lifecycle
- We will maintain at least one previous major version when a new version is released
- Deprecated versions will be supported for a minimum of 6 months after a replacement is available
- Deprecation notices will be included in API documentation and HTTP headers
- Deprecated endpoints will return a warning header: `Warning: 299 - "This endpoint is deprecated and will be removed on YYYY-MM-DD. Please migrate to /api/v2/..."`

### 5. Non-Breaking Changes
- Non-breaking changes will be made without incrementing the version number
- Non-breaking changes include:
  - Adding new endpoints
  - Adding optional request fields
  - Adding response fields (existing clients will ignore them)
  - Bug fixes that don't change the documented behavior

### 6. Documentation
- Each API version will have its own OpenAPI/Swagger documentation
- Documentation will clearly indicate deprecated endpoints and their removal dates
- Migration guides will be provided when new versions are released

## Consequences

### Positive
- Clients can continue using existing API versions while migrating to newer versions
- Clear guidelines for when to create new versions reduce unnecessary proliferation
- URI path versioning provides clear visibility of the version being used
- Package structure reflects API versions, improving code organization
- Enables controlled evolution of the API without breaking existing integrations
- Provides clear expectations to clients about API lifecycle

### Negative
- Multiple versions increase the codebase size and maintenance burden
- Requires additional testing for each supported version
- May lead to code duplication between versions
- URI path versioning makes URLs longer and less clean
- Supporting multiple versions increases complexity in routing and documentation
- May require maintaining compatibility code for longer than ideal

## Alternatives Considered

1. **Header-Based Versioning**
   - Using custom headers: `X-API-Version: 1`
   - Cleaner URLs without version information
   - Less visible and harder to test
   - Not as well supported by browser explorers and documentation tools

2. **Accept Header Versioning**
   - Using content negotiation: `Accept: application/vnd.company.app-v1+json`
   - Standards-based approach using content negotiation
   - More complex to implement and test
   - Less discoverable for API consumers

3. **Query Parameter Versioning**
   - Using query parameters: `/api/customers?version=1`
   - Easy to implement
   - Version becomes optional, which could lead to confusion
   - Less structured than path-based versioning

4. **No Versioning / Continuous Evolution**
   - Making only backward-compatible changes
   - Simpler codebase with only one version
   - Severely limits ability to improve API design over time
   - May lead to maintaining legacy design decisions indefinitely

## Implementation Notes

- We will use Spring's `@RequestMapping` with version prefixes:
  ```java
  @RestController
  @RequestMapping("/api/v1/customers")
  public class CustomerControllerV1 { ... }
  ```

- For documentation, we will use SpringDoc with separate Docket configurations per version:
  ```java
  @Bean
  public GroupedOpenApi v1Api() {
      return GroupedOpenApi.builder()
          .group("v1")
          .pathsToMatch("/api/v1/**")
          .build();
  }
  ```

- We will implement a custom annotation for marking deprecated endpoints:
  ```java
  @Deprecated
  @DeprecatedAPI(removeAfter = "2023-12-31", replacedBy = "/api/v2/customers")
  @GetMapping("/{id}")
  public ResponseEntity<CustomerDTOV1> getCustomer(@PathVariable Long id) { ... }
  ```

- We will use MapStruct for efficient mapping between different DTO versions and domain models

## Compliance Verification
- Code reviews will check that breaking changes are properly versioned
- API tests will verify that existing versions maintain backward compatibility
- Static analysis will be used to enforce proper package structure
- Documentation will be reviewed to ensure it accurately reflects versioning information
- Automated tests will verify that deprecated endpoints include proper warning headers

## References
- RESTful API Versioning Strategies: https://www.mnot.net/blog/2012/12/04/api-evolution
- Spring REST API Versioning: https://www.baeldung.com/rest-versioning
- Microsoft REST API Guidelines on Versioning: https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md#12-versioning
