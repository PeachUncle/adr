# 4. Integration Testing Framework

## Status

Accepted

Date: 2025-07-01

## Context

Our application relies on various external dependencies such as MongoDB, message brokers, and third-party APIs. 
While unit tests with mocks are essential, they do not verify that our code correctly interacts with actual external 
systems. Integration tests are needed to ensure our services work correctly with real dependencies.

However, integration testing introduces several challenges:

- Setting up and tearing down external dependencies consistently for tests
- Managing test data and database state between test runs
- Avoiding interference between parallel test executions
- Ensuring tests are repeatable and isolated
- Maintaining consistent testing patterns across different external systems
- Keeping integration tests efficient and fast enough for CI/CD pipelines

We need a standardized approach to integration testing that addresses these challenges while supporting our 
existing testing practices and build tag categorization.

## Decision

We will implement a comprehensive integration testing framework with the following components:

1. **Container-Based Dependencies**
   - Use Docker Compose for managing test dependencies
   - Single instance of each dependency shared across test suites
   - Clean container management through Makefile targets
   - Consistent environment between development and CI

2. **Database Test Helpers**
   - Utility functions for database setup and teardown
   - Unique database per test for isolation
   - Data seeding utilities for common test scenarios
   - Automatic cleanup after test completion

3. **Test Organization**
   - Integration tests in `*_integration_test.go` files
   - Build tags as defined in [ADR-0003](0003-build-tags-for-test-categorization.md)
   - Table-driven test patterns consistent with unit tests, as defined in [ADR-0002](0002-table-driven-tests-implementation.md)

4. **Fixed Time Handling**
   - Clock interface for deterministic time-based testing
   - Fixed time values for predictable test results

5. **Environment Configuration**
   - Environment variables for configuration
   - Support for local development with real dependencies
   - Consistent configuration between local and CI environments

6. **Test Fixtures and Factories**
   - Standard patterns for creating test data
   - Domain-specific test object factories
   - Utilities for comparing expected vs. actual data
   - Create fixtures within the test cases

## Consequences

### Positive

- Efficient test execution with minimal container overhead
- Simple and maintainable container management through Docker Compose
- Database-level isolation prevents test interference
- Consistent test environment across local and CI environments
- Fast test execution suitable for continuous integration
- Reduced complexity in test infrastructure
- Better resource utilization with shared containers
- Test helpers reduce boilerplate code in integration tests
- Fixtures within test cases reduce the risk of unexpected breaking tests by adding new fixtures and provides the 
  full context within the case definition

### Negative

- Need to manage container lifecycle through Docker Compose
- Initial setup required for development environment
- Resource requirements for running dependencies
- Potential for port conflicts if not properly configured
- Need to ensure proper cleanup of test databases

### Neutral

- Need for CI/CD systems with container support
- Regular updates required for container images and dependencies
- Balance needed between test coverage and execution time

## Implementation Notes

### MongoDB Test Framework

For MongoDB integration testing, we will implement a reusable test helper:

```go
// TestDB represents a test database instance with utilities for test setup/teardown
type TestDB struct {
  Client   *mongo.Client
  DB       *mongo.Database
  cleanup  func() error
}

// NewTestDB creates a new test database connection
func NewTestDB(t *testing.T) *TestDB {
  t.Helper()

  ctx := context.Background()
  logger, _ := log.NewTest()
  client, err := NewClient(ctx, logger)
  if err != nil {
      t.Fatalf("Failed to create MongoDB client: %v", err)
  }

  // Setting up a unique database name for each test to avoid conflicts
  dbName := fmt.Sprintf("test_%s_%d", t.Name(), time.Now().UnixNano())
  db := client.Database(dbName)

  return &TestDB{
      Client: client,
      DB:     db,
      cleanup: func() error {
          ctx := context.Background()
          if err := db.Drop(ctx); err != nil {
              return fmt.Errorf("failed to drop test database: %w", err)
          }
          if err := client.Disconnect(ctx); err != nil {
              return fmt.Errorf("failed to disconnect test client: %w", err)
          }
          return nil
      },
  }
}

// Close cleans up test database and disconnects
func (tdb *TestDB) Close(t *testing.T) {
  t.Helper()
  if err := tdb.cleanup(); err != nil {
      t.Fatalf("Failed to cleanup test database: %v", err)
  }
}
```

### Clock Interface for Deterministic Testing

To ensure deterministic time-based tests:

```go
// Clock is an interface that provides time functionality
type Clock interface {
  Now() time.Time
}

// RealClock uses the actual system time
type RealClock struct{}

func (RealClock) Now() time.Time {
  return time.Now()
}

// FixedClock returns a fixed time for testing
type FixedClock struct {
  FixedTime time.Time
}

func (c FixedClock) Now() time.Time {
  return c.FixedTime
}
```

### Makefile Integration

```makefile
run-integration-tests: start-mongodb
  @echo "Running integration tests..."
  @go test -v -tags=integration ./...

start-mongodb:
  @echo "Starting MongoDB container..."
  @docker compose up -d mongodb
```

### CI/CD Integration

To integrate with CI/CD pipelines:

```yaml
# GitHub Actions example
integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v3
      - name: Set up Go
        uses: actions/setup-go@v3
        with:
          go-version: '1.24'
      - name: Run integration tests
        run: make run-integration-tests
```

## Related Documents

- [ADR-0003: Build Tags for Test Categorization](0003-build-tags-for-test-categorization.md)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MongoDB Go Driver Documentation](https://pkg.go.dev/go.mongodb.org/mongo-driver/mongo)

## Contributors

- Àlex Grau Roca
