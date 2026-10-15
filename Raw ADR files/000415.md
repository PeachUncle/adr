# ADR 001: Use Vitest for TypeScript Testing

## Status

**Accepted** - November 17, 2025

## Context

The Advent of Code repository supports multiple programming languages (JavaScript, Python, Go, Rust, Java, C++, TypeScript). Each language needs a robust testing framework to validate puzzle solutions.

For TypeScript solutions, we needed to choose a testing framework that would:
- Provide fast test execution
- Support modern TypeScript/ESM features natively
- Integrate well with our CI/CD pipeline
- Offer good developer experience
- Be actively maintained

### Options Considered

1. **Jest** - The most popular JavaScript/TypeScript testing framework
   - ✅ Mature ecosystem
   - ✅ Extensive community support
   - ✅ Rich plugin ecosystem
   - ❌ Slower test execution
   - ❌ Complex ESM support (requires configuration)
   - ❌ Heavy dependency footprint

2. **Vitest** - Modern testing framework built on Vite
   - ✅ Very fast test execution (powered by Vite)
   - ✅ Native ESM support
   - ✅ Jest-compatible API (easy migration)
   - ✅ Built-in TypeScript support
   - ✅ Lightweight
   - ❌ Smaller ecosystem than Jest
   - ❌ Newer, less established

3. **Node Test Runner** - Node.js built-in test runner
   - ✅ No external dependencies
   - ✅ Built into Node.js
   - ❌ Limited assertion library
   - ❌ Less mature feature set
   - ❌ Limited ecosystem

## Decision

We will use **Vitest** as the testing framework for TypeScript solutions.

### Rationale

1. **Performance**: Vitest's speed significantly improves developer feedback loops, especially important as the number of puzzle solutions grows
2. **Modern Stack**: Native ESM and TypeScript support aligns with our use of modern JavaScript features
3. **Jest Compatibility**: Vitest's Jest-compatible API makes it easy for developers familiar with Jest to contribute
4. **Future-Proof**: Built on Vite, which is becoming a standard in the JavaScript ecosystem
5. **Developer Experience**: Hot module replacement and watch mode provide excellent DX

### Implementation Details

- **Configuration**: `vitest.config.ts` with globals enabled for Jest-like syntax
- **Test File Pattern**: `**/*.test.ts`
- **Coverage**: v8 provider for coverage reporting
- **TypeScript**: Configured in `tsconfig.json` with `vitest/globals` types

## Consequences

### Positive

- ✅ Faster test execution (typically 2-5x faster than Jest)
- ✅ Better TypeScript developer experience
- ✅ Simpler configuration for ESM modules
- ✅ Consistent with modern JavaScript best practices
- ✅ Easy to add coverage reporting
- ✅ Watch mode works seamlessly

### Negative

- ⚠️ Smaller plugin ecosystem compared to Jest
- ⚠️ Some advanced Jest features may not be available
- ⚠️ Team members need to learn Vitest-specific features (though API is mostly compatible)

### Migration Strategy

If we need to migrate back to Jest in the future:
1. Vitest uses a Jest-compatible API, so most tests won't need changes
2. Update `package.json` scripts
3. Replace `vitest.config.ts` with `jest.config.js`
4. Update `tsconfig.json` to use Jest types instead of Vitest

## Alternatives Considered but Rejected

- **Mixing frameworks** - Rejected to maintain consistency across TypeScript solutions
- **No testing framework** - Rejected as automated testing is critical for maintaining solution correctness

## Related

- **Testing Principles**: See [Hypothesis-Driven Design Guide](../HYPOTHESIS_DRIVEN_DESIGN.md)
- **BDD Testing**: Repository also uses Cucumber.js for BDD tests (separate concern)
- **Future ADRs**: May need ADR for integration testing strategy if puzzle complexity increases

## References

- [Vitest Documentation](https://vitest.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Jest to Vitest Migration Guide](https://vitest.dev/guide/migration.html)

## Notes

- This decision applies specifically to TypeScript solutions
- Other languages (JavaScript, Python, Go, etc.) continue using their language-specific testing frameworks
- BDD tests (Cucumber) remain unchanged and serve a different purpose (structural validation)

---

**Author**: GitHub Copilot Agent  
**Reviewers**: Application Architecture Expert, Test Quality Reviewer  
**Last Updated**: November 17, 2025
