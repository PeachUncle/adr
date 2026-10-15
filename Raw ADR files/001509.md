# ADR-002: Test-Driven Development Standards

## Status
Accepted

## Date
2025-01-14

## Context
The EdgeRush LootMan project lacked consistent testing practices and had insufficient test coverage. Tests were written after implementation (if at all), leading to:
- Low code coverage (below 40% in many areas)
- Difficult-to-test code with tight coupling
- Bugs discovered late in development or production
- Fear of refactoring due to lack of safety net
- Inconsistent test quality and organization

We needed a systematic approach to ensure all code is thoroughly tested and testable from the start.

## Decision
We will adopt Test-Driven Development (TDD) as the standard development methodology for all new code and refactored code.

### TDD Workflow
All code must follow the Red-Green-Refactor cycle:
1. **Red** - Write a failing test first
2. **Green** - Write minimal code to make the test pass
3. **Refactor** - Improve code while keeping tests green
4. **Repeat** - Continue for each new feature or behavior

### Test Organization
Tests are organized by type following the test pyramid:
- **Unit Tests (70%)**: Test single units in isolation
  - Domain logic tests
  - Use case tests
  - Value object tests
- **Integration Tests (25%)**: Test component interactions
  - API endpoint tests
  - Database repository tests
  - External API client tests
- **End-to-End Tests (5%)**: Test complete user scenarios
  - Critical business workflows
  - User journey tests

### Test Standards
- **Naming Convention**: `should_ExpectedBehavior_When_StateUnderTest`
- **Organization**: Arrange-Act-Assert (AAA) pattern
- **Coverage Threshold**: Minimum 85% code coverage enforced by build
- **Test Isolation**: Each test must be independent and repeatable
- **Fast Execution**: Unit tests must run in milliseconds

### Testing Tools
- **JUnit 5**: Test framework
- **MockK**: Kotlin-friendly mocking library
- **Testcontainers**: Integration testing with real databases
- **JaCoCo**: Code coverage reporting and enforcement
- **Kotest**: Assertions and matchers

### Base Test Classes
```kotlin
// Unit tests
abstract class UnitTest {
    @BeforeEach
    fun setup() {
        MockKAnnotations.init(this)
    }
}

// Integration tests
@SpringBootTest
@Testcontainers
abstract class IntegrationTest {
    // Testcontainers setup
}
```

## Consequences

### Positive
- **Higher Code Quality**: Tests catch bugs before they reach production
- **Better Design**: TDD forces thinking about interfaces and dependencies upfront
- **Living Documentation**: Tests document expected behavior
- **Confident Refactoring**: Comprehensive tests enable safe code changes
- **Faster Debugging**: Failing tests pinpoint exact issues
- **Reduced Technical Debt**: Code is testable from the start
- **Regression Prevention**: Tests prevent reintroduction of bugs

### Negative
- **Initial Slowdown**: Writing tests first feels slower initially
- **Learning Curve**: Team needs to learn TDD practices and tools
- **Discipline Required**: Easy to skip tests under pressure
- **Test Maintenance**: Tests need to be maintained alongside code
- **Mocking Complexity**: Some scenarios require complex test setup

### Neutral
- **Build Time**: More tests increase build time, but catch issues earlier
- **Coverage Enforcement**: Build fails if coverage drops below 85%
- **Test-First Mindset**: Requires cultural shift in development approach

## Implementation Notes
- JaCoCo configured to fail builds below 85% coverage threshold
- Base test classes provide common setup for unit and integration tests
- Test data builders created for common entities (Raider, LootAward, Raid)
- Integration tests use Testcontainers for real PostgreSQL database
- MockK used for mocking in unit tests
- Test organization mirrors production code structure

## Exceptions
- **Legacy Code**: Existing code without tests can be refactored incrementally
- **Configuration Classes**: Simple Spring configuration may not need tests
- **DTOs**: Simple data classes may not need dedicated tests
- **Generated Code**: Code generators output doesn't require tests

## Verification
- Coverage reports generated with each build
- CI/CD pipeline enforces coverage threshold
- Code review checklist includes test verification
- Regular team reviews of test quality

## References
- [Test Driven Development by Kent Beck](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)
- [Growing Object-Oriented Software, Guided by Tests](http://www.growing-object-oriented-software.com/)
- [Testing Standards Documentation](../testing-standards.md)
