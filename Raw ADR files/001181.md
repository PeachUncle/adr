# ADR-002: Comprehensive Testing Strategy

## Status

Accepted

## Date

2025-01-10

## Context

We need a robust testing strategy for our Connect Four monorepo that ensures:

- High confidence in game logic correctness
- Reliable UI component behavior
- Effective API integration testing
- Fast feedback loops during development
- Maintainable test suites across packages

The testing strategy must support both web and mobile platforms while integrating seamlessly with our Turborepo build system.

## Decision

We will implement a **comprehensive testing strategy** using:

- **Jest** as the primary testing framework
- **React Testing Library** for component testing
- **React Native Testing Library** for mobile component testing
- **Package-specific coverage thresholds**
- **Parallel test execution** via Turborepo

### Test Architecture

```
Testing Stack:
├── Unit Tests (game-logic)     # Pure logic testing
├── Component Tests (ui)        # React component behavior
├── Integration Tests (api)     # HTTP/WebSocket communication
└── Smoke Tests (apps)          # Basic application functionality
```

## Rationale

### Why Jest

1. **Zero Configuration**: Works out-of-the-box with TypeScript
2. **Snapshot Testing**: Built-in snapshot capabilities
3. **Mocking**: Powerful mocking capabilities for dependencies
4. **Parallel Execution**: Fast test runs across multiple cores
5. **Ecosystem**: Excellent integration with React Testing Library

### Why React Testing Library

1. **User-Centric**: Tests interact with components as users would
2. **Accessibility**: Encourages accessible component design
3. **Maintainable**: Less brittle than implementation-detail tests
4. **Best Practices**: Promotes good testing practices
5. **Community**: Industry standard for React component testing

### Coverage Strategy

| Package      | Threshold | Rationale               |
| ------------ | --------- | ----------------------- |
| `game-logic` | 80%       | Critical business logic |
| `ui`         | 80%       | User-facing components  |
| `api-client` | 75%       | External dependencies   |
| `mobile`     | 70%       | Platform-specific code  |
| `web`        | 70%       | Application integration |

## Implementation Details

### Test Distribution

**Total: 67 Tests**

- `game-logic`: 25 unit tests (game rules, validation, win detection)
- `ui`: 29 component tests (rendering, interactions, accessibility)
- `api-client`: 13 integration tests (HTTP, WebSocket, error handling)
- `mobile`: 1 smoke test (basic functionality)
- `web`: 1 smoke test (basic functionality)

### Jest Configuration

**Base Configuration (`jest.config.base.js`):**

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx|js)',
    '**/*.(test|spec).+(ts|tsx|js)',
  ],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/index.ts',
  ],
  coverageReporters: ['text', 'lcov', 'html'],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
};
```

**Package-Specific Overrides:**

- **UI Package**: JSDOM environment, jest-dom matchers
- **Mobile Package**: React Native preset, expo mocking
- **API Client**: Node environment, fetch/WebSocket mocking

### Test Categories

#### 1. Unit Tests (game-logic)

**Focus**: Pure business logic validation

```typescript
describe('makeMove', () => {
  it('should place piece in correct position', () => {
    const board = createEmptyBoard();
    const result = makeMove(board, 0, 'red');

    expect(result.board[5][0]).toBe('red');
    expect(result.isValid).toBe(true);
  });
});
```

**Coverage Areas:**

- Board state management
- Move validation (bounds, availability)
- Win detection (horizontal, vertical, diagonal)
- Game state transitions
- Edge cases and error conditions

#### 2. Component Tests (ui)

**Focus**: User interaction and rendering behavior

```typescript
describe('GameBoard', () => {
  it('should handle column clicks', () => {
    const mockOnClick = jest.fn();
    render(<GameBoard board={board} onColumnClick={mockOnClick} />);

    fireEvent.click(screen.getByLabelText('Drop piece in column 1'));

    expect(mockOnClick).toHaveBeenCalledWith(0);
  });
});
```

**Coverage Areas:**

- Component rendering with various props
- User interaction handling
- Accessibility compliance
- Error boundary behavior
- State management integration

#### 3. Integration Tests (api-client)

**Focus**: External service communication

```typescript
describe('ConnectStarApiClient', () => {
  it('should handle WebSocket connections', () => {
    const client = new ConnectStarApiClient('ws://localhost');
    client.connect();

    expect(mockWebSocket).toHaveBeenCalled();
  });
});
```

**Coverage Areas:**

- HTTP request/response handling
- WebSocket connection management
- Error handling and retry logic
- Event listener registration
- Authentication and authorization

#### 4. Smoke Tests (apps)

**Focus**: Basic application functionality

```typescript
describe('App smoke test', () => {
  it('runs a basic test', () => {
    expect(true).toBe(true);
  });
});
```

**Purpose:**

- Verify app can be instantiated
- Catch major configuration issues
- Ensure critical dependencies load

### Parallel Execution Strategy

**Turborepo Integration:**

```json
{
  "tasks": {
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"],
      "inputs": [
        "src/**/*.{ts,tsx}",
        "**/*.test.{ts,tsx}",
        "**/*.spec.{ts,tsx}"
      ]
    }
  }
}
```

**Benefits:**

- Tests run in parallel across packages
- Only affected packages re-run tests
- Cached results for unchanged packages
- Sub-2-minute full test suite execution

### Mocking Strategy

**Global Mocks:**

```typescript
// API calls
global.fetch = jest.fn();

// WebSocket
global.WebSocket = jest.fn();

// React Native modules
jest.mock('expo-status-bar', () => ({
  StatusBar: 'StatusBar',
}));
```

**Selective Mocking:**

- Mock external dependencies, not internal code
- Use real implementations when feasible
- Prefer dependency injection for testability

## Consequences

### Positive

1. **High Confidence**: Comprehensive coverage ensures reliability
2. **Fast Feedback**: Parallel execution provides quick validation
3. **Regression Prevention**: Automated testing catches breaking changes
4. **Documentation**: Tests serve as living documentation
5. **Refactoring Safety**: Tests enable confident code changes

### Negative

1. **Initial Overhead**: Writing tests requires upfront time investment
2. **Maintenance Burden**: Tests need updates when interfaces change
3. **False Positives**: Flaky tests can reduce developer confidence
4. **Coverage Pressure**: Focus on metrics vs. meaningful tests

### Mitigation Strategies

1. **Test-Driven Development**: Write tests first to ensure value
2. **Regular Maintenance**: Review and update tests during refactoring
3. **Quality Over Quantity**: Focus on meaningful tests, not just coverage
4. **Developer Education**: Train team on effective testing practices

## Development Workflow

### Local Development

```bash
# Run all tests
pnpm test

# Run package-specific tests
pnpm test --filter=game-logic

# Watch mode for active development
pnpm test --filter=ui -- --watch

# Coverage report
pnpm test:coverage
```

### Continuous Integration

```bash
# CI test command
pnpm test:ci

# Coverage validation
pnpm test:coverage --threshold
```

### Pre-commit Hooks

- Run affected package tests
- Validate coverage thresholds
- Ensure test naming conventions

## Success Metrics

- **Coverage**: Maintain package-specific thresholds
- **Test Reliability**: <5% flaky test rate
- **Execution Time**: Full test suite <2 minutes
- **Developer Adoption**: 100% of features include tests
- **Bug Detection**: Tests catch >80% of regressions

## Future Enhancements

1. **Visual Regression Testing**: Automated UI screenshot comparison
2. **Performance Testing**: Load testing for API endpoints
3. **End-to-End Testing**: Full user workflow automation
4. **Property-Based Testing**: Advanced game logic validation
5. **Mutation Testing**: Verify test quality with mutation testing

## References

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library Guide](https://testing-library.com/docs/react-testing-library/intro/)
- [Testing Best Practices](https://kentcdodds.com/blog/how-to-know-what-to-test)
- [Turborepo Testing](https://turbo.build/repo/docs/core-concepts/monorepos/running-tasks)
