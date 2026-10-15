# ADR-0003: Use Vitest for Testing

**Date:** 2024-01-01 (Retroactive)  
**Status:** Accepted  
**Deciders:** Project Team  
**Consulted:** N/A  
**Informed:** All Developers

## Context

The Graph Browser application requires a comprehensive testing framework that can test both Vue components (frontend) and Node.js API code (backend). The testing solution needs to:

- Support Vue 3 component testing
- Work with Vite build tool
- Test both frontend and backend code
- Provide fast test execution
- Generate code coverage reports
- Have good developer experience
- Support mocking and test utilities

### Problem Statement
Select a testing framework that provides unified testing for both frontend Vue components and backend Node.js code, with excellent integration with our Vite build system.

### Constraints
- Must work with Vue 3 and Vue Test Utils
- Should integrate seamlessly with Vite
- Must support ES modules (type: "module")
- Should provide code coverage reporting
- Needs to support mocking (especially for database and HTTP calls)
- Fast test execution for developer productivity

### Assumptions
- Developers are familiar with Jest-like testing APIs
- Tests will be co-located with source code in `__tests__` directories
- Both unit and integration tests will be needed
- CI/CD will run tests on every commit

## Decision

We will use **Vitest** as the primary testing framework for both frontend and backend code.

### Proposed Solution
Implement testing using:
- **Vitest** as the test runner and framework
- **@vue/test-utils** for Vue component testing
- **jsdom** for DOM environment in component tests
- **@vitest/coverage-istanbul** for code coverage
- **supertest** for HTTP endpoint testing
- Mock functions using Vitest's built-in `vi.mock()`

### Rationale
1. **Vite Integration**: Vitest is built by the Vite team and shares the same config, no additional build setup needed
2. **Fast Execution**: Uses Vite's transformation pipeline, incredibly fast test runs
3. **Jest-Compatible API**: Familiar API for developers coming from Jest
4. **ES Module Support**: Native ESM support, no transformation needed
5. **Watch Mode**: Smart watch mode that only reruns affected tests
6. **Single Framework**: One testing framework for both frontend and backend
7. **Modern**: Built for modern JavaScript tooling and workflows
8. **Developer Experience**: Excellent error messages and debugging support
9. **Coverage**: Built-in coverage support with Istanbul or V8

## Alternatives Considered

### Alternative 1: Jest
**Description:** Use Jest, the most popular JavaScript testing framework

**Pros:**
- Industry standard with huge ecosystem
- Extensive documentation and community resources
- Rich ecosystem of plugins and tools
- Battle-tested in production
- Excellent snapshot testing
- Parallel test execution

**Cons:**
- Requires additional configuration for Vite projects
- ESM support requires experimental flags and transformation
- Slower than Vitest (especially with Vue SFCs)
- Separate configuration from Vite
- More complex setup for Vue components
- Transform pipeline conflicts with Vite

**Why rejected:** Jest's ESM support is not as mature, and the configuration overhead for working with Vite makes Vitest a better choice. The compatibility issues and slower performance don't justify using Jest when Vitest provides a Jest-like API with better Vite integration.

### Alternative 2: Mocha + Chai
**Description:** Use Mocha as test runner with Chai for assertions

**Pros:**
- Flexible and unopinionated
- Can choose own assertion library
- Long history and stability
- Good for diverse testing needs
- Works well with various tools

**Cons:**
- Requires more setup and configuration
- Need to combine multiple tools (mocha, chai, sinon, nyc)
- More boilerplate per test file
- Less out-of-the-box compared to Vitest
- No built-in mocking (need sinon)
- Slower than Vitest

**Why rejected:** The flexibility is not needed for this project, and the additional setup complexity and performance overhead make Vitest a better choice. Vitest's batteries-included approach is more appropriate.

### Alternative 3: AVA
**Description:** Use AVA, a modern minimalist test runner

**Pros:**
- Very fast (parallel by default)
- Clean, minimal API
- Built-in TypeScript support
- ESM support
- Good error messages

**Cons:**
- Smaller community than Jest or Vitest
- Tests always run in isolation (can be slower for some scenarios)
- Less integration with Vue ecosystem
- Different API from Jest (less familiar)
- Fewer resources and examples

**Why rejected:** While AVA is excellent, Vitest provides better Vue integration and a more familiar Jest-like API. The Vite integration is also not as seamless as Vitest.

### Alternative 4: Cypress Component Testing
**Description:** Use Cypress for component testing instead of unit testing

**Pros:**
- Real browser testing
- Excellent debugging tools
- Visual testing
- Can test in actual browser environment
- Good for integration/E2E tests

**Cons:**
- Much slower than unit testing
- Heavier resource requirements
- Overkill for simple component tests
- Requires browser installation in CI
- Harder to mock dependencies
- Not suitable for backend API testing

**Why rejected:** Cypress is excellent for E2E tests but too heavy for unit testing. Vitest is better suited for fast unit/integration tests. Cypress could be added later for E2E testing.

## Consequences

### Positive
- **Unified Testing**: One framework for frontend and backend reduces cognitive load
- **Fast Feedback**: Test execution is extremely fast due to Vite integration
- **Easy Setup**: Minimal configuration needed, shares Vite config
- **Good DX**: Hot module reload for tests, great error messages
- **Jest Compatibility**: Easy migration of Jest tests if needed
- **Coverage Reports**: Built-in coverage with Istanbul or V8
- **Modern**: Designed for modern JavaScript with first-class ESM support
- **Smart Caching**: Vite's caching makes repeated test runs very fast

### Negative
- **Smaller Ecosystem**: Fewer third-party plugins compared to Jest
- **Newer Tool**: Less battle-tested than Jest (though rapidly maturing)
- **Learning Curve**: Developers familiar with Jest may need to learn subtle differences
- **Documentation**: Some edge cases may have less documentation than Jest

### Neutral
- **API Similarity to Jest**: Mostly compatible but some differences exist
- **Community Size**: Growing rapidly but still smaller than Jest
- **Browser Testing**: For real browser testing, still need Cypress or Playwright

## Implementation

### Action Items
- [x] Install Vitest and related dependencies
- [x] Configure vitest.config.js
- [x] Set up Vue Test Utils for component testing
- [x] Create test files for all components
- [x] Set up backend API tests with supertest
- [x] Configure coverage reporting
- [x] Add test scripts to package.json
- [x] Document testing approach in README

### Timeline
Completed in initial project setup, with tests added iteratively

### Dependencies
- vitest
- @vue/test-utils
- jsdom
- @vitest/coverage-istanbul
- supertest (for API testing)

### Risks
- **Risk**: Vitest API changes (still evolving)
  - **Mitigation**: Pin versions, review changelogs before updates, comprehensive test suite catches breaking changes
- **Risk**: Less Stack Overflow support than Jest
  - **Mitigation**: Official docs are excellent, growing community, Jest knowledge is transferable
- **Risk**: Missing plugins available in Jest ecosystem
  - **Mitigation**: Most needs covered by core Vitest, can create custom plugins if needed

## Validation

### Success Criteria
- ✅ All components have unit tests
- ✅ All API endpoints have tests
- ✅ Tests run in < 5 seconds for fast feedback
- ✅ Code coverage > 80% (currently 26 tests passing)
- ✅ Easy to write new tests
- ✅ Tests catch regressions

### Review Date
2025-01-01 (Annual review, or sooner if significant issues arise)

## References

- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Vite Testing Guide](https://vitejs.dev/guide/features.html#testing)
- [Migration from Jest](https://vitest.dev/guide/migration.html)

## Notes

### Current Test Structure
```
src/components/__tests__/
├── ConnectedList.spec.js (4 tests)
├── GraphBrowser.spec.js (13 tests)
├── NodeDetails.spec.js (2 tests)
├── NodeHistory.spec.js (1 test)
└── graph.fixture.json (test data)

api/__tests__/
└── graph.spec.js (6 tests)
```

### Test Commands
```bash
npm test              # Run all tests
npm run test:unit     # Run unit tests
npm run coverage      # Run with coverage
```

### Vitest Configuration
The project uses a separate `vitest.config.js` that extends the main Vite config, allowing test-specific settings without affecting the build configuration.

### Future Enhancements
- Add mutation testing (Stryker is already configured)
- Add integration tests for full user flows
- Consider adding Playwright for E2E browser testing
- Increase code coverage to >90%

---

**Related ADRs:**
- ADR-0001: Use Vue 3 for Frontend

**Supersedes:**
- None

**Superseded by:**
- None
