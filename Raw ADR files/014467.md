# 3. Build Tags for Test Categorization

## Status

Accepted

Date: 2025-07-01

## Context

As we have multiple test types (unit, integration, end-to-end), we need a consistent way to categorize and execute 
specific types of tests, as running all tests together regardless of their type can lead to several issues:

- Slow CI/CD pipelines when running all tests, including integration tests that require external dependencies
- Difficulty in isolating failures to specific test categories
- Integration tests requiring infrastructure setup that may not be available in all environments
- Mixing of unit and integration tests in test runs, even when only one type is needed
- Lack of clarity about which tests are purely unit tests versus those with external dependencies

We need a standardized approach to categorize our tests so they can be run selectively based on the context and 
stage of development.

## Decision

We will use Go build tags to categorize different types of tests, allowing selective execution of test suites. 
Specifically:

1. **Build Tag Convention**:
   - Unit tests: `//go:build unit`
   - Integration tests: `//go:build integration`
   - End-to-end tests: `//go:build e2e`

2. **File Naming Convention**:
   - Unit tests: `*_test.go`
   - Integration tests: `*_integration_test.go`
   - End-to-end tests: Stored in a separate `e2e` directory

3. **Default Test Behavior**:
   - Without specifying tags, no tests will run
   - Explicit tag must be provided to run tests of a specific category

4. **Test Command Structure**:
   - Unit tests: `go test -tags=unit ./...`
   - Integration tests: `go test -tags=integration ./...`
   - All tests: `go test -tags="unit integration" ./...`

5. **CI/CD Pipeline Integration**:
   - Different stages will run different categories of tests
   - Unit tests: Run on every commit
   - Integration tests: Run on every commit but in a separate job with the appropriate infrastructure
   - E2E tests: Run before deployment to staging/production, and optionally on every commit in a separate job

## Consequences

### Positive

- Clear separation between test types allows selective test execution
- Faster CI/CD pipelines by running only the necessary tests at each stage
- Improved test isolation and clarity about test dependencies
- Better organization of test files based on their category
- Ability to run unit tests without setting up external dependencies
- Clearer error attribution when tests fail
- Simpler debugging process for specific test categories

### Negative

- Additional setup is required for each test file to include appropriate build tags
- Risk of tests being skipped if build tags are forgotten or misconfigured
- Learning curve for developers unfamiliar with Go build tags
- Potential for confusion if tags and file naming conventions do not align

### Neutral

- Regular review is required to ensure tests are categorized correctly
- Build tag conventions must be clearly documented and enforced through code reviews
- May require adjustments to IDE configurations to properly recognize and run tagged tests

## Implementation Notes

### Build Tag Syntax

Go build tags must be placed at the top of the file before the package declaration:

```go
//go:build unit

package mypackage_test
```

For more complex tag expressions, use logical operators:

```go
//go:build integration && !race
```

### Makefile Integration

To simplify test execution, we will add these targets to our Makefile:

```makefile
.PHONY: test-unit test-integration test-e2e test-all

test-unit:
	go test -tags=unit ./... -v

test-integration:
	go test -tags=integration ./... -v

test-all: test-unit test-integration
```

### CI/CD Configuration

GitHub Actions workflow example:

```yaml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v3
        with:
          go-version: '1.24'
      - run: make test-unit

  integration-tests:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:6.0
        ports:
          - 27017:27017
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v3
        with:
          go-version: '1.24'
      - run: make test-integration
```

### IDE Configuration

For GoLand/IntelliJ IDEA, configure run configurations to include the appropriate build tags:

1. Edit Run Configuration
2. Add `-tags=unit` or `-tags=integration` to the "Go tool arguments" field

For VS Code, add to settings.json:

```json
{
  "go.testTags": "unit"
}
```

### Common Test Utilities

For utilities needed by multiple test types, create a separate package with appropriate build constraints:

```go
//go:build unit || integration

package testutils
```

## Related Documents

- [ADR-0005: Testing Strategy and Types](../../global/0005-testing-strategy-and-types.md)
- [Go Build Constraints Documentation](https://pkg.go.dev/cmd/go#hdr-Build_constraints)
- [Go Testing Package Documentation](https://pkg.go.dev/testing)

## Contributors

- Àlex Grau Roca
