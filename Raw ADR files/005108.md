# 5. Testing Framework and Strategy: Vitest with Property-Based Testing

Date: 2025-08-28

## Status

Accepted

## Context

The project needed a comprehensive testing strategy that would:

- Support modern ES Modules and TypeScript out of the box
- Provide fast test execution and watch mode for development
- Enable comprehensive code coverage with configurable thresholds
- Support both unit testing and property-based testing approaches
- Integrate well with the existing toolchain (TypeScript, ESM)
- Offer excellent developer experience with debugging and reporting

Key options considered:

- **Jest**: Most popular, but complex ESM setup required
- **Mocha + Chai**: Flexible but requires more configuration
- **Vitest**: Modern, ESM-first, Vite-powered test runner
- **Node.js Test Runner**: New built-in option but limited features

## Decision

We chose **Vitest** as our primary test framework with **fast-check** for property-based testing:

1. **Primary Framework**: Vitest for unit and integration tests
2. **Property-Based Testing**: fast-check for invariant testing
3. **Coverage**: V8 provider with 80% minimum thresholds
4. **Strategy**: Test-as-contract approach with comprehensive coverage

### Implementation Details

- **Framework**: Vitest with Node.js environment
- **Coverage Provider**: V8 (fastest and most accurate)
- **Coverage Thresholds**: 80% minimum for lines, branches, functions, statements
- **Property Testing**: fast-check for testing invariants and edge cases
- **File Organization**: `tests/*.spec.ts` for unit tests, `tests/*.property.spec.ts` for property tests
- **Watch Mode**: Integrated with development workflow

## Consequences

### Positive

- **Zero Configuration**: Works out-of-the-box with ESM and TypeScript
- **Performance**: Extremely fast test execution and watch mode
- **Modern Features**: Native ESM, TypeScript, and modern JavaScript support
- **Developer Experience**: Excellent debugging, hot module replacement
- **Coverage Enforcement**: Strict thresholds ensure high test quality
- **Property Testing**: Discovers edge cases that unit tests might miss
- **CI/CD Integration**: Fast feedback loops in continuous integration

### Negative

- **Ecosystem**: Smaller ecosystem compared to Jest (though growing rapidly)
- **Learning Curve**: Property-based testing requires understanding of invariants
- **Coverage Requirements**: 80% threshold may slow down rapid prototyping
- **Tool Compatibility**: Some Jest-specific tools may not work directly

### Mitigation

- **Documentation**: Clear examples of both unit and property-based testing patterns
- **Templates**: Test templates and patterns documented in CLAUDE.md
- **Gradual Adoption**: Property-based tests introduced incrementally
- **Flexibility**: Coverage can be adjusted per-file for special cases
- **Training**: Team guidance on effective property-based testing strategies

## References

- [Vitest Documentation](https://vitest.dev/)
- [fast-check Documentation](https://fast-check.dev/)
- [Property-Based Testing Guide](https://increment.com/testing/in-praise-of-property-based-testing/)
- [V8 Coverage Provider](https://vitest.dev/config/#coverage-provider)
