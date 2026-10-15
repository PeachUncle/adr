# Testing Utilities for Generated Command Interfaces

## Status

Accepted

## Context

Testing generated command handlers involves repetitive boilerplate:
- Creating mock cobra commands
- Building complex request objects with nested flag and argument structures
- Writing assertion helpers for common test patterns

Users of adder-generated commands need easier ways to test their handlers without writing verbose test setup code.

## Decision

Implement testing utilities in the adder package that provide:

1. **Assertion helpers** - `AssertNoError()` and `AssertError()` with better error messages
2. **Mock command creation** - `NewMockCobraCommand()` for test scenarios
3. **Generic request builders** - Fluent interface for building test requests
4. **Documentation and examples** - Clear patterns for testing generated handlers

## Consequences

### Positive
- Reduced test boilerplate for adder users
- Consistent testing patterns across projects
- Better test readability with fluent builders
- Lower barrier to entry for testing CLI handlers

### Negative
- Additional API surface to maintain
- Dependency on testing package in main codebase
- Need to keep utilities in sync with generated structures

### Implementation

```go
// Basic utilities
tu := adder.NewTestingUtils()
tu.AssertNoError(t, err)
tu.AssertError(t, err, "expected message")
cmd := tu.NewMockCobraCommand("test")

// Generic request builder
builder := adder.NewRequestBuilder().
    WithFlag("input", "testdata/commands").
    WithFlag("validate", true).
    WithArg("name", "test")

// Type-safe builders (user-created)
req := NewMyRequestBuilder().
    WithInput("testdata").
    WithValidate(true).
    Build()
```

### Guidelines

- **Use testdata directories** - Follow Go conventions for test data organization
- **Create type-safe builders** - For complex request structures
- **Test error cases** - Use AssertError for comprehensive coverage
- **Mock dependencies** - Use dependency injection for external services