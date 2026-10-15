# ADR 0005: Testing Strategy for Next.js App Router

## Status
Accepted

## Context
We need a comprehensive testing strategy for our Next.js application that covers:
- Server Components (async components that fetch data)
- Client Components (interactive components with state)
- Server Actions (server-side mutations)
- Mixed architectures (components that use both patterns)

The goal is to achieve 85%+ code coverage while maintaining test clarity and speed.

## Decision

### Testing Framework
- **Jest** as the test runner
- **React Testing Library** for component testing
- **@testing-library/jest-dom** for DOM matchers

### Testing Approach

#### 1. Server Components Testing
- Await the component before rendering: `const component = await ServerComponent()`
- Mock data fetching modules with `jest.mock()`
- Test async data flow and error handling
- Example: `dashboard/page.test.tsx`

#### 2. Client Components Testing
- Use `fireEvent` for user interactions
- Mock Server Actions with `jest.mock()`
- Use `waitFor()` for async state updates
- Test `useTransition` and loading states
- Example: `InteractiveWidget.test.tsx`

#### 3. Presentational Components Testing
- Focus on rendering with different props
- Test conditional rendering based on data
- Verify CSS classes and variants
- Use `data-testid` for complex selectors
- Example: `ServerStats.test.tsx`

#### 4. Server Actions Testing
- Mock Next.js cache functions (`revalidatePath`, `revalidateTag`)
- Mock database operations
- Test return values and error handling
- Current coverage: 25% (acceptable for Server Actions)

### Mocking Strategy

#### Global Mocks (jest.setup.ts)
```typescript
// Polyfills
global.TextEncoder = TextEncoder
global.TextDecoder = TextDecoder

// Next.js navigation
jest.mock('next/navigation')

// Next.js cache
jest.mock('next/cache')
```

#### Local Mocks
- Database modules: Mock per test file
- Server Actions: Mock in Client Component tests
- External APIs: Mock with `jest.fn()`

### Test Structure
```typescript
describe('ComponentName', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('describes expected behavior', () => {
    // Arrange
    // Act
    // Assert
  });
});
```

### Coverage Targets
- **Overall**: 85%+ (achieved: 96.33%)
- **Statements**: 90%+
- **Branches**: 80%+
- **Functions**: 85%+
- **Lines**: 90%+

### Testing Best Practices
1. **Test behavior, not implementation**: Focus on what users see and do
2. **Use semantic queries**: Prefer `getByRole`, `getByLabelText` over `getByTestId`
3. **Mock at module boundaries**: Mock external dependencies, not internal logic
4. **Keep tests simple**: One concept per test
5. **Test edge cases**: Empty states, errors, loading states
6. **Avoid snapshot tests**: They're fragile and don't test behavior

## Consequences

### Positive
- High code coverage (96.33%) provides confidence in refactoring
- Clear testing patterns for Server/Client Components
- Fast test execution (< 3 seconds for full suite)
- Easy to add new tests following established patterns
- Mocks are centralized and reusable

### Negative
- Server Actions are harder to test in isolation (25% coverage)
- Need to maintain polyfills for Node.js environment
- Global mocks can hide integration issues
- `data-testid` attributes add noise to production code

### Neutral
- Server Components require `await` before rendering (not intuitive at first)
- Need to understand Jest mocking patterns
- Coverage tools don't understand Server Components well

## Alternatives Considered

### 1. Playwright/Cypress E2E Testing
- **Pros**: Tests real browser, catches integration issues
- **Cons**: Slower, more complex setup, harder to mock Server Actions
- **Decision**: Use unit tests first, add E2E later for critical flows

### 2. Testing Server Actions with MSW (Mock Service Worker)
- **Pros**: More realistic API mocking
- **Cons**: Overkill for simple Server Actions, harder setup
- **Decision**: Keep simple jest.mock() for now

### 3. 100% Code Coverage Target
- **Pros**: Complete test coverage
- **Cons**: Diminishing returns, too much time on edge cases
- **Decision**: 85%+ is sufficient, focus on critical paths

## Notes
- Server Actions testing could be improved with integration tests
- Consider adding E2E tests when the app grows
- Coverage report available: `npm test -- --coverage --watchAll=false`
- All test files follow naming convention: `*.test.tsx` or `*.test.ts`

## Related
- ADR 0002: Server Components vs Client Components
- ADR 0003: Tailwind CSS with CVA for Design System
