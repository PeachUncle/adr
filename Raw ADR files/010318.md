# ADR-018: React/TypeScript Testing Standards

## Metadata

Version: 1.0.0
Status: Proposed
Last Updated: 2025-06-23

## Context

The frontend codebase requires consistent, maintainable testing practices for React components and TypeScript code. While general testing guidelines exist in Core Governance and component-specific practices have emerged (as documented in StudentCourseDetailsPage.test-dos-and-donts.md), we need to formalize these patterns into standardized, system-wide testing requirements.

### Current Situation

- Testing practices vary across components
- Some test patterns have proven more effective than others
- Component-specific guidelines exist but aren't formally adopted
- Test setup and provider mocking needs standardization

### Impact Scope

- All React components and TypeScript code
- Frontend test infrastructure
- CI/CD pipeline
- Developer workflow

### Stakeholders

- Frontend developers
- QA team
- DevOps team
- Code reviewers

## Decision

We will adopt a comprehensive testing standard for React/TypeScript code that builds upon existing practices and formalizes proven patterns.

### 1. Test Environment Setup

- Use `renderWithProviders` for consistent context and providers
- Maintain centralized test utils in `src/test-utils/`
- Configure global mocks in `setupTests.ts`
- Standardize provider mocking patterns

### 2. Mock Implementation Requirements

```typescript
// Standard auth context mock pattern
vi.mock('@context/auth/AuthContext', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual, // Preserve all exports
    useAuth: () => ({
      user: mockUser,
      isAuthenticated: true,
      // ... other required properties
    }),
  };
});
```

- Always spread original module exports
- Mock only necessary functionality
- Provide type-safe mock data
- Use factories for consistent test data

### 3. Component Testing Standards

1. Routing and Navigation
   - Set route params via `initialEntries`
   - Test route-dependent rendering
   - Verify navigation behavior

2. Provider Integration
   - Use real providers via `renderWithProviders`
   - Avoid redundant provider wrapping
   - Mock provider hooks consistently

3. State and Event Testing
   - Test both positive and negative states
   - Verify error states and loading states
   - Use `waitFor` for async operations

4. Service Integration
   - Mock and verify service calls
   - Test error handling
   - Validate loading states

### 4. Code Quality Requirements

- Maintain clean test files
- Remove unused imports/variables
- Use typed assertions
- Avoid test code duplication

## Consequences

### Benefits

- Consistent test implementation across codebase
- Reduced test maintenance overhead
- Improved test reliability
- Clear testing patterns for new components

### Drawbacks

- Initial effort to update existing tests
- Learning curve for new patterns
- Migration period with mixed standards

### Technical Impacts

- Changes to test utilities
- Updates to CI/CD validation
- Test coverage requirements

### Required Changes

- Update test setup files
- Refactor existing tests
- Document new patterns

## Implementation

### Required Steps

1. Update `setupTests.ts` with standard mocks
2. Create/update test utilities
3. Document patterns and examples
4. Review and update existing tests
5. Configure linting rules

### Dependencies

- Testing libraries (@testing-library/react)
- Mocking tools (vitest)
- Type definitions
- Linting configuration

### Migration Plan

1. Apply to new components immediately
2. Update key existing components
3. Gradually migrate remaining tests
4. Validate coverage requirements

### Validation Criteria

- All tests follow new patterns
- No provider-related test failures
- Improved test maintainability
- Complete pattern documentation

## Related Documents

- [Core Governance - Quality Assurance](../rules/core/governance.md)
- [StudentCourseDetailsPage.test-dos-and-donts.md](../../frontend/src/pages/courses/StudentCourseDetailsPage.test-dos-and-donts.md)
- [ADR-013: TypeScript Service Layer Standardization](./ADR-013-typescript-service-standard.md)
- [setupTests.ts](../../frontend/src/test-utils/setupTests.ts)
