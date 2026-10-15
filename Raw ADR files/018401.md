# ADR-004: Comprehensive Testing Strategy

Date: 2025-01-16
Status: Accepted

## Context

The Team Dashboard is a complex system with multiple components:
- Frontend React application
- Multiple backend services
- WebSocket real-time communication
- Database interactions
- External API integrations

We need a testing strategy that ensures:
- High code quality and reliability
- Fast feedback loops
- Confidence in deployments
- Maintainable test suites

## Decision

We will implement a multi-tiered testing pyramid:

### Testing Pyramid
```
         ╱─────╲
        ╱  E2E  ╲      (5%)
       ╱─────────╲
      ╱Integration╲    (20%)
     ╱─────────────╲
    ╱   Component   ╲  (25%)
   ╱─────────────────╲
  ╱      Unit         ╲ (50%)
 ╱─────────────────────╲
```

### 1. Unit Tests (50% of tests)
- **Framework**: Vitest for speed and compatibility
- **Coverage Target**: 80% minimum
- **Focus**: Pure functions, utilities, business logic
- **Execution Time**: < 5 seconds for entire suite

### 2. Component Tests (25% of tests)
- **Framework**: React Testing Library
- **Focus**: React components in isolation
- **Mocking**: Mock external dependencies
- **User Interaction**: Test user events and state changes

### 3. Integration Tests (20% of tests)
- **Framework**: Vitest + Supertest
- **Focus**: API endpoints, database operations
- **Database**: Use test containers
- **Execution Time**: < 30 seconds

### 4. E2E Tests (5% of tests)
- **Framework**: Playwright
- **Focus**: Critical user journeys
- **Environment**: Staging environment
- **Execution Time**: < 5 minutes

## Consequences

### Positive
- **Fast Feedback**: Unit tests run in seconds
- **Comprehensive Coverage**: All layers tested
- **Maintainable**: Clear test boundaries
- **Confidence**: High confidence in deployments
- **Documentation**: Tests serve as documentation

### Negative
- **Initial Investment**: Time to set up infrastructure
- **Maintenance Overhead**: Tests need updates with code
- **Execution Time**: Full suite takes time
- **Flakiness Risk**: E2E tests can be flaky

## Alternatives Considered

### 1. Manual Testing Only
- **Pros**: No automation overhead
- **Cons**: Slow, error-prone, not scalable

### 2. E2E Testing Only
- **Pros**: Tests real user scenarios
- **Cons**: Slow feedback, expensive to maintain

### 3. Unit Testing Only
- **Pros**: Fast, reliable
- **Cons**: Doesn't catch integration issues

## Implementation Details

### Test File Structure
```
src/
├── components/
│   ├── Button.tsx
│   └── Button.test.tsx
├── services/
│   ├── api.ts
│   └── api.test.ts
├── utils/
│   ├── helpers.ts
│   └── helpers.test.ts
tests/
├── integration/
│   ├── api/
│   └── database/
└── e2e/
    ├── auth.spec.ts
    └── dashboard.spec.ts
```

### Unit Test Example
```typescript
// utils/validation.test.ts
import { describe, it, expect } from 'vitest';
import { validateEmail } from './validation';

describe('validateEmail', () => {
  it('should validate correct email', () => {
    expect(validateEmail('user@example.com')).toBe(true);
  });

  it('should reject invalid email', () => {
    expect(validateEmail('invalid')).toBe(false);
  });
});
```

### Component Test Example
```typescript
// components/AgentCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentCard } from './AgentCard';

describe('AgentCard', () => {
  it('should display agent name', () => {
    render(<AgentCard agent={{ name: 'Test Agent' }} />);
    expect(screen.getByText('Test Agent')).toBeInTheDocument();
  });

  it('should handle click events', () => {
    const handleClick = vi.fn();
    render(<AgentCard agent={{}} onClick={handleClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

### Integration Test Example
```typescript
// tests/integration/api/agents.test.ts
import request from 'supertest';
import { app } from '../../../src/app';

describe('POST /api/agents', () => {
  it('should create new agent', async () => {
    const response = await request(app)
      .post('/api/agents')
      .send({ name: 'Test Agent', type: 'frontend' })
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(String),
      name: 'Test Agent',
      type: 'frontend'
    });
  });
});
```

### E2E Test Example
```typescript
// tests/e2e/agent-creation.spec.ts
import { test, expect } from '@playwright/test';

test('create new agent workflow', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('button:has-text("New Agent")');
  await page.fill('input[name="name"]', 'Test Agent');
  await page.selectOption('select[name="type"]', 'frontend');
  await page.click('button:has-text("Create")');
  
  await expect(page.locator('.agent-card')).toContainText('Test Agent');
});
```

### CI/CD Pipeline
```yaml
name: Test Pipeline
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pnpm install
      - run: pnpm test:unit
      - run: pnpm coverage

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v3
      - run: pnpm install
      - run: pnpm test:integration

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pnpm install
      - run: pnpm build
      - run: pnpm test:e2e
```

### Coverage Requirements
- **Overall**: 80% minimum
- **Critical Paths**: 95% minimum
- **New Code**: 90% minimum
- **Exclusions**: Generated files, config files

## Migration Path

1. Phase 1: Set up testing infrastructure
2. Phase 2: Add unit tests (target 80% coverage)
3. Phase 3: Add component tests
4. Phase 4: Add integration tests
5. Phase 5: Add E2E tests for critical paths

## References

- [Testing Trophy](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)