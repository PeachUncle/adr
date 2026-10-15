---
status: 'accepted'
date: 2025-08-06
decision-makers: voder.ai website team
consulted: LLM-assisted development stakeholders
informed: development team
packages:
  - dev-config
---

# ADR 0009: Use Vitest for Package Testing and Playwright for E2E Testing

## Context and Problem Statement

Following ADR-0008's monorepo package architecture, we need to establish comprehensive testing strategies that support:

- **Package-level isolation**: Each package needs independent testing
- **LLM agent validation**: Tests prove agents implemented specs correctly
- **Cross-browser compatibility**: Application works across all target browsers
- **Integration confidence**: Packages work together in the complete application
- **Performance validation**: Application meets Core Web Vitals requirements

ADR-0002 established Playwright for E2E testing, but we need to clarify the complete testing strategy across the monorepo.

## Decision Drivers

- **Package Isolation**: Each package needs fast, isolated unit testing
- **LLM Validation**: Tests serve as executable specifications for AI agents
- **Browser Coverage**: Cross-browser compatibility validation required
- **Development Speed**: Fast feedback loops during package development
- **CI Efficiency**: Parallel testing across packages and browsers
- **Existing Decision**: ADR-0002 mandates Playwright for E2E testing

## Considered Options

- **Vitest Only**: Use Vitest for all testing (unit, integration, E2E)
- **Playwright Only**: Use Playwright for all testing levels
- **Jest + Playwright**: Traditional Jest for unit tests, Playwright for E2E
- **Vitest + Playwright**: Vitest for packages, Playwright for application E2E

## Decision Outcome

Chosen option: **"Vitest + Playwright"**, because it provides optimal developer experience for package development (Vitest's speed and modern features) while maintaining the proven E2E capabilities established in ADR-0002.

### Testing Strategy by Layer

#### **Package Testing (Vitest)**

- **Unit Tests**: Component lifecycle, business logic, error handling
- **Integration Tests**: Service container interactions, dependency injection
- **Contract Tests**: Interface compliance and API validation
- **Accessibility Tests**: WCAG compliance, ARIA implementation
- **Performance Tests**: Memory usage, initialization times

#### **Application Testing (Playwright)**

- **E2E Tests**: Complete user workflows and interactions
- **Cross-browser Tests**: Chromium, Firefox, WebKit validation
- **Mobile Tests**: Responsive behavior on mobile devices
- **Performance E2E**: Core Web Vitals, loading performance
- **Accessibility E2E**: Full-page accessibility validation

### Migration note

Migration note: MVP loader tests have migrated to use shared mocks utilities located at src/vite.config.mock-utils.ts and deterministic first-function extraction via getFirstFunctionExport in src/vite.config.test-helpers.ts. Per-test ad-hoc mocks have been removed; loader assertions now rely on the known first function export from the mocks.

### Consequences

**Positive:**

- **Fast Package Development**: Vitest's instant feedback during development
- **Comprehensive Coverage**: Unit tests + E2E tests cover all scenarios
- **Browser Confidence**: Playwright ensures cross-browser compatibility
- **LLM-Friendly**: Clear test specifications guide AI implementation
- **CI Efficiency**: Parallel package testing + browser testing

**Negative:**

- **Tool Complexity**: Developers need familiarity with both tools
- **Configuration Overhead**: Separate config files for different test types
- **Dependency Management**: Different test utilities for different layers

### Confirmation

- ✅ Each package has Vitest configuration with 90%+ coverage
- ✅ Application has Playwright configuration for all target browsers
- ✅ CI pipeline runs package tests in parallel before E2E tests
- ✅ LLM agents can validate implementation using package tests
- ✅ E2E tests validate complete user workflows across browsers

## Implementation Details

### Package Test Configuration

Each package includes:

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    environment: 'jsdom',
    coverage: {
      thresholds: {
        global: { functions: 90, lines: 90, branches: 80 },
      },
    },
  },
});
```

### Application Test Configuration

Main application includes:

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'chromium', use: devices['Desktop Chrome'] },
    { name: 'firefox', use: devices['Desktop Firefox'] },
    { name: 'webkit', use: devices['Desktop Safari'] },
  ],
});
```

### Test Workflow

1. **Package Development**: Vitest provides instant feedback
2. **Package Validation**: Vitest confirms interface compliance
3. **Integration Testing**: Vitest validates service interactions
4. **E2E Validation**: Playwright confirms user workflows
5. **Cross-browser Testing**: Playwright validates browser compatibility

## Alignment with Existing ADRs

- **ADR-0002**: Maintains Playwright for E2E testing as established
- **ADR-0006**: Supports Vanilla TypeScript with appropriate test utilities
- **ADR-0008**: Enables package isolation with independent test suites

## More Information

This testing strategy ensures that LLM agents have clear success criteria at the package level (Vitest tests) while maintaining confidence in the complete application experience (Playwright E2E tests). The dual-tool approach optimizes for both development speed and deployment confidence.
