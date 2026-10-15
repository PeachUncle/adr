# 5. Testing Strategy and Types

## Status

Accepted

Date: 2025-07-01

## Context

Our domain services require a comprehensive testing strategy to ensure reliability, maintainability, and confidence 
in our codebase. We need to:

1. Define the different types of tests and their scope
2. Establish when each type of test should be used
3. Set clear guidelines for test coverage requirements
4. Define the testing pyramid structure for our domain services
5. Ensure consistent testing practices across the project

## Decision

At this stage we will not define any coverage requirement, as first we want to focus on quality rather than quantity.
In the future we will review this decision again, using the current coverage metrics across all services, to decide 
if we need to define a minimum and realistic coverage or not.

We will implement a multi-layered testing strategy following the testing pyramid principle, with the following test 
types:

### 1. Unit Tests
- **Purpose**: Test individual components in isolation
- **Scope**: Functions, methods, and small component **behaviors**
- **Location**: Alongside the code being tested (`*_test.go` files)
- **Characteristics**:
  - Fast execution
  - No external dependencies
  - Focus on business logic
  - Use of mocks for external dependencies (detailed in future ADRs)

### 2. Integration Tests
- **Purpose**: Test component interactions and external dependencies
- **Scope**: Database operations, service interactions, external API calls
- **Coverage**: Key integration paths must be covered
- **Location**: Alongside the code being tested (`*_integration_test.go` files)
- **Characteristics**:
  - Test against real dependencies when possible
  - May require test containers or local dependencies

### 3. End-to-End Tests
- **Purpose**: Test complete user scenarios
- **Scope**: Full system functionality through different API endpoints and services
- **Coverage**: All critical user paths and happy paths
- **Location**: `e2e` folder
- **Characteristics**:
  - Run against a fully deployed system
  - Test real user scenarios
  - Slower execution, run in the CI/CD pipeline

### Test Execution Strategy

#### Current Strategy

All tests are run on every commit

#### Desired Strategy

- Unit tests: Run on every commit
- Integration tests: Run on every commit
- E2E tests: Run before deployment to staging/production

## Consequences

### Positive

- Clear separation of test types and responsibilities
- Consistent testing approach across the project
- Early detection of issues through different test layers
- Improved confidence in code changes
- Better maintainability through an organized test structure

### Negative

- Initial setup time for different test types
- Additional CI/CD pipeline complexity
- More time needed for test maintenance

### Neutral

- Need for additional infrastructure for integration and E2E tests
- Regular review and updates of the testing strategy are needed

## Implementation Notes

### Example Test Structure
```
services/authentication-service/
└── internal/
    └── auth/
        ├── service.go
        ├── service_test.go           # Unit tests
        └── service_integration_test.go # Integration tests
e2e/
└── auth_test.go                  # E2E tests
```

## Related Documents

## Contributors

- Àlex Grau Roca