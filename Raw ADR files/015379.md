# ADR 003: Vitest Testing Framework

**Status**: Accepted

**Date**: 2025-10-05

**Context**:
We needed a testing framework that supports:
- TypeScript 5.5.0+ with strict mode (constitutional requirement)
- Native ESM support (aligning with Fastify v5 and modern JavaScript)
- Fast execution for TDD workflow (constitutional requirement: unit tests <10ms, suite <30s)
- Code coverage ≥80% (constitutional requirement)
- AAA pattern (Arrange-Act-Assert) test structure
- Fastify `.inject()` method integration for lightweight HTTP testing
- Testing pyramid: Unit (70%), Integration (20%), E2E (10%)

The constitution explicitly states: "Use Vitest for new TypeScript projects" over Jest, making this a constitutionally-guided decision with technical validation.

**Decision**:
We selected **Vitest 3.2+** as the testing framework for all testing layers (unit, integration, E2E).

**Rationale**:
- **Constitutional Requirement**: Explicit constitutional mandate for Vitest in new TypeScript projects
- **Performance**: 10-20x faster than Jest, supporting TDD rapid feedback loops and <30s suite execution requirement
- **Native ESM**: Built-in ESM support aligns with Fastify v5 and modern TypeScript configuration without transformation overhead
- **TypeScript Excellence**: First-class TypeScript support with no additional configuration, strict mode compatibility
- **Jest Compatibility**: API compatible with Jest, reducing learning curve for developers familiar with Jest patterns
- **Built-in Coverage**: V8 coverage provider integrated, no additional dependencies for ≥80% coverage enforcement
- **Lightweight HTTP Testing**: Compatible with Fastify's `.inject()` method, eliminating need for supertest or actual HTTP server

**Alternatives Considered**:
1. **Jest**:
   - Pros: Mature ecosystem, widespread adoption, extensive documentation
   - Cons: Slower execution (10-20x), ESM support requires transformation, constitutional preference for Vitest
   - Rejected: Performance limitations and constitutional requirements

2. **Ava**:
   - Pros: Fast execution, concurrent test running
   - Cons: Smaller ecosystem, less TypeScript tooling, unfamiliar API patterns
   - Rejected: Smaller community and less TypeScript integration

3. **Tap**:
   - Pros: Fastify's original testing framework, excellent Fastify integration
   - Cons: Less TypeScript-friendly, smaller ecosystem, steeper learning curve
   - Rejected: TypeScript integration challenges

**Consequences**:

**Positive**:
- 10-20x faster test execution enables rapid TDD feedback loops
- Native ESM support eliminates transformation overhead and configuration complexity
- Jest-compatible API allows reuse of testing patterns and knowledge
- Built-in V8 coverage provider meets ≥80% coverage requirement without additional tools
- Excellent TypeScript support with strict mode compatibility
- UI mode (`@vitest/ui`) provides visual test debugging and monitoring
- Fastify `.inject()` integration enables lightweight HTTP testing without server overhead
- Parallel test execution by default improves suite performance

**Negative**:
- Smaller ecosystem compared to Jest (fewer third-party plugins and resources)
- Less Stack Overflow content for troubleshooting edge cases
- Some Jest plugins may not have Vitest equivalents
- Newer framework with potentially undiscovered edge cases

**Neutral**:
- Requires Vitest-specific configuration file (`vitest.config.ts`)
- Different matcher library than Jest (though API compatible)
- Coverage configuration differs slightly from Jest patterns

**Configuration**:
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      lines: 80,
      functions: 80,
      branches: 80,
      statements: 80,
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.test.ts',
        '**/*.config.ts'
      ]
    }
  }
});
```

**Testing Strategy**:
1. **Unit Tests (70%)**:
   - Domain value objects and business logic
   - Application use cases
   - Isolated component testing
   - Fast execution (<10ms per test)

2. **Integration Tests (20%)**:
   - Route and controller integration
   - Fastify `.inject()` for HTTP simulation
   - Infrastructure layer testing
   - No actual HTTP server needed

3. **E2E Tests (10%)**:
   - Full application flow testing
   - Complete request/response cycle
   - Acceptance criteria validation

**Fastify Integration**:
```typescript
// Using Fastify's inject method (lightweight)
const response = await app.inject({
  method: 'GET',
  url: '/status'
});
expect(response.statusCode).toBe(200);
expect(response.json()).toEqual({ status: 'ok' });
```

**AAA Pattern Enforcement**:
```typescript
describe('GET /status', () => {
  it('should return ok status', async () => {
    // Arrange
    const app = await buildApp();

    // Act
    const response = await app.inject({
      method: 'GET',
      url: '/status'
    });

    // Assert
    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({ status: 'ok' });
  });
});
```

**Coverage Enforcement**:
- Minimum 80% coverage across lines, functions, branches, statements
- Coverage reports in text, JSON, HTML, and LCOV formats
- CI/CD pipeline integration for automated enforcement

**Performance Targets**:
- Unit tests: <10ms per test (constitutional requirement)
- Integration tests: <100ms per test
- E2E tests: <500ms per test
- Total suite: <30s execution (constitutional requirement)

**References**:
- [Vitest Documentation](https://vitest.dev/)
- [Vitest with Fastify](https://vitest.dev/guide/environment.html)
- Constitution: `.specify/memory/constitution.md` (Vitest requirement for TypeScript projects)
- Research findings: `/Users/abhishek/Documents/Personal/readme-kit/specs/001-create-basic-server/research.md`
- Feature specification: `/Users/abhishek/Documents/Personal/readme-kit/specs/001-create-basic-server/spec.md`
