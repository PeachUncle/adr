# ADR 0009: Backend Testing Strategy

## Status

Accepted

## Context

A robust testing strategy is crucial for ensuring the reliability, maintainability, and correctness of the backend application. Without clear guidelines, testing efforts can become inconsistent, leading to:

* Uneven test coverage across different parts of the application.
* Difficulty in refactoring or adding new features with confidence.
* Increased risk of regressions slipping into production.
* Slow feedback loops during development.

Defining a consistent testing strategy helps mitigate these risks and ensures a high standard of quality.

## Decision

We will adopt a multi-layered testing approach for the backend, focusing on unit tests and integration tests.

1. **Testing Levels:**
   * **Unit Tests:** Focus on testing individual components (functions, methods, small structs) in isolation. Dependencies should be mocked or stubbed. These tests should be fast and numerous.
   * **Integration Tests:** Verify the interaction between multiple components or layers, including interactions with external systems like databases or external APIs (using test doubles or real instances in controlled environments). These tests are slower than unit tests but provide confidence in component collaboration.
   * **(Optional) End-to-End (E2E) Tests:** Test the entire application flow from the API endpoint down to the database (or other external systems). These are the slowest and most brittle tests, used sparingly for critical user flows.

2. **Tools and Libraries:**
   * **Core Testing:** Go's standard `testing` package.
   * **Assertions:** `stretchr/testify/assert` and `stretchr/testify/require` for expressive assertions.
   * **Mocking:** `stretchr/testify/mock` for creating mocks based on interfaces. Alternatively, manual test doubles (stubs, fakes) can be used where appropriate.
   * **HTTP Testing:** `net/http/httptest` for testing HTTP handlers.
   * **Database Testing:** Use test containers (e.g., via `ory/dockertest` or similar libraries) or an in-memory database (like SQLite, if compatible) for integration tests involving the database. Test data should be managed carefully (setup/teardown).

3. **Testing Scope by Layer (Onion Architecture):**
   * **Domain Layer:** Primarily unit tests. Test entities, value objects, domain services, and factory/reconstructor functions for correctness and invariant enforcement. No external dependencies allowed.
   * **Application Layer:** Unit tests for use cases. Mock repository interfaces and other external dependencies (e.g., external service clients defined by interfaces). Verify orchestration logic, input validation (DTO level), and interaction with mocks.
   * **Infrastructure Layer:** Integration tests. Test repository implementations against a real (test) database. Test external API clients against mock servers or potentially real test endpoints (if available and stable).
   * **Interfaces Layer (HTTP Handlers):** Integration tests using `net/http/httptest`. Mock the application layer (use cases) called by the handlers. Verify request parsing, response formatting, status codes, and error handling.

4. **Conventions:**
   * **File Naming:** Test files must be named `*_test.go` and reside in the same package as the code being tested.
   * **Test Function Naming:** Use descriptive names, e.g., `TestUser_NewUser_ValidInput`, `TestUserUsecase_CreateUser_RepositoryError`.
   * **Table-Driven Tests:** Prefer table-driven tests for testing multiple input/output scenarios for the same function.
   * **Test Coverage:** Aim for high unit test coverage in the Domain and Application layers. Integration tests cover critical paths in Infrastructure and Interfaces layers. Coverage metrics will be monitored but not used as a strict gate initially.

5. **Test Data Management:**
   * For unit tests, use simple, hardcoded data.
   * For integration tests (especially database), use setup and teardown functions (e.g., `TestMain`, subtest setup/teardown) to manage test data creation and cleanup, ensuring test isolation.

6. **Continuous Integration (CI):**
   * All tests (unit and integration) must pass in the CI pipeline before code can be merged.
   * Run tests automatically on every commit/pull request.

## Consequences

* **Pros:**
  * **Increased Confidence:** Higher confidence in code correctness and stability when refactoring or adding features.
  * **Improved Quality:** Early detection of bugs and regressions.
  * **Faster Feedback:** Unit tests provide rapid feedback during development.
  * **Living Documentation:** Well-written tests serve as documentation for how components are intended to be used.
  * **Maintainability:** Clear separation of concerns in tests mirrors the application architecture.
* **Cons:**
  * **Development Time:** Writing and maintaining tests requires additional development effort.
  * **Test Maintenance:** Tests need to be updated alongside code changes, which can sometimes be time-consuming.
  * **Integration Test Complexity:** Setting up and managing environments for integration tests (e.g., databases in containers) can be complex.
  * **Potential for Brittle Tests:** Poorly written tests (especially integration/E2E) can be brittle and fail due to unrelated changes.
