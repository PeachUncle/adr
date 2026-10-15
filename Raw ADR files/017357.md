# ADR-008: Jest for Testing

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-006 (TypeScript Strict Mode)](./ADR-006-typescript-strict-mode.md)

## Context

We needed a comprehensive testing framework that supports:
- Unit tests for services and repositories
- Integration tests for API endpoints
- TypeScript support with minimal configuration
- Fast execution and watch mode
- Coverage reporting
- Mocking capabilities

## Decision

We will use **Jest** with ts-jest for all backend and frontend testing.

**Configuration**:
```typescript
// jest.config.ts
export default {
  preset: 'ts-jest',
  testEnvironment: 'node',
  coverageThreshold: {
    global: {
      branches: 85,
      functions: 85,
      lines: 85,
      statements: 85
    }
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.test.ts',
    '!src/**/__tests__/**'
  ]
};
```

**Key Features**:
1. **Zero Config TypeScript**: ts-jest handles compilation
2. **Snapshot Testing**: UI component regression testing
3. **Mock Functions**: `jest.fn()` for dependency mocking
4. **Code Coverage**: Built-in Istanbul coverage
5. **Watch Mode**: Fast feedback during development

## Consequences

### Positive

1. **Excellent TypeScript Support**: No transpilation issues
2. **Fast Test Execution**: Parallel test running
3. **Great DX**: Clear error messages, watch mode
4. **Large Ecosystem**: Many plugins and matchers
5. **Industry Standard**: Easy to hire developers familiar with Jest

### Negative

1. **Slower than Vitest**: Slightly slower than newer alternatives
2. **Configuration Complexity**: Multi-project setup requires tuning
3. **Memory Usage**: Can be memory-intensive for large projects

## Alternatives Considered

- **Mocha + Chai**: More setup required - Rejected
- **Vitest**: Faster but less mature - Considered for future
- **Ava**: Minimal features - Rejected

## Testing Standards

```typescript
describe('PaymentService', () => {
  let service: PaymentService;
  let mockRepo: jest.Mocked<IPaymentRepository>;

  beforeEach(() => {
    mockRepo = {
      create: jest.fn(),
      findById: jest.fn(),
    } as any;

    service = new PaymentService(mockRepo);
  });

  it('should create payment invoice', async () => {
    const invoice = await service.createInvoice(100);
    expect(mockRepo.create).toHaveBeenCalledWith(
      expect.objectContaining({ amount: 100 })
    );
  });
});
```

**Coverage Requirements**:
- Services/Repositories: 95% minimum
- Global: 85% minimum
- New code: 95%+ required

## Related Documentation

- [Testing Strategy](/docs/testing-strategy.md)
- [Backend Developer Guide - Testing](/docs/development/backend-developer-guide.md#testing)
- [Elite Testing Standards](/PHASE_8_ELITE_TESTING_IMPLEMENTATION.md)

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
