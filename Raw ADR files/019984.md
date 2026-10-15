---
status: 'accepted'
date: 2025-08-28
decision-makers: [GitHub Copilot, development team]
consulted:
  [
    Stack Overflow community,
    Vitest documentation,
    Istanbul.js documentation,
    Node Tap documentation,
  ]
informed: [future developers, LLM agents working on this codebase]
depends-on: [ADR-0009]
---

# Use Dual Testing Strategy for Script Coverage Instead of Subprocess Coverage Collection

## Context and Problem Statement

Build scripts (like `copy-assets.ts` and `generate-markdownlint-config.ts`) need comprehensive test coverage to meet the project's 80% coverage threshold. These scripts are designed to be executed both as CLI tools and as importable functions. The question arose: should we attempt to collect coverage metrics from subprocess execution of these scripts, or use a different approach?

Initial coverage reports showed 0% coverage for scripts when tested only through subprocess execution, despite the scripts running successfully and producing correct outputs.

This decision builds upon ADR-0009 (Adopt Istanbul as Coverage Engine), which provides the coverage exclusion capabilities required for this testing strategy.

## Decision Drivers

- **Coverage Threshold Compliance**: Project requires 80% coverage across all metrics (statements, branches, functions, lines)
- **Script Testability**: Scripts must be tested both as CLI tools (integration) and as functions (unit testing)
- **Maintainability**: Testing approach should be sustainable and not overly complex
- **Tool Limitations**: Coverage tools may have limitations with subprocess execution
- **Development Efficiency**: Testing approach should not significantly slow down test execution
- **Future Maintainer Understanding**: Approach should be clear to future developers

## Considered Options

1. **Subprocess Coverage Collection with NODE_V8_COVERAGE**
2. **Subprocess Coverage Collection with Istanbul/nyc**
3. **Dual Testing Strategy (Unit + Integration)**
4. **Pure Integration Testing Only**
5. **Pure Unit Testing Only**

## Decision Outcome

Chosen option: "**Dual Testing Strategy (Unit + Integration)**", because it provides complete validation while working within the limitations of coverage tools, and offers the best balance of coverage measurement and end-to-end validation.

### Consequences

- **Good**, because the approach achieves comprehensive coverage measurement through unit tests
- **Good**, because the approach maintains end-to-end validation through integration tests
- **Good**, because the approach works reliably with Vitest/Istanbul tooling
- **Good**, because it's maintainable and doesn't depend on complex subprocess coverage collection
- **Good**, because test execution remains fast and predictable
- **Bad**, because it requires maintaining two sets of tests for scripts (unit and integration)
- **Bad**, because CLI-specific code paths may have reduced coverage (acceptable trade-off)
- **Neutral**, because it aligns with established testing patterns for most Node.js projects

### Confirmation

Implementation compliance can be confirmed by:

- **Coverage Reports**: Scripts achieve >80% coverage through unit tests importing script functions
- **Integration Validation**: CLI execution validated through subprocess integration tests
- **Architecture Review**: Script functions are properly exported and unit-testable
- **CLI Minimization**: CLI-only code paths are limited to argument parsing, execution, basic output, and error handling with coverage exclusion comments
- **Test Execution**: Both unit and integration test suites pass consistently

## Pros and Cons of the Options

### Subprocess Coverage Collection with NODE_V8_COVERAGE

**Investigation Results**: Attempted to use `NODE_V8_COVERAGE` environment variable to collect coverage from child processes.

- **Good**, because it would provide coverage from actual CLI execution
- **Good**, because it mirrors real-world usage patterns
- **Bad**, because Vitest doesn't automatically set NODE_V8_COVERAGE environment variable
- **Bad**, because manual coverage directory setup doesn't merge with main coverage report
- **Bad**, because it adds complexity to test setup and teardown
- **Bad**, because coverage data remains isolated and doesn't contribute to overall metrics

**Technical Finding**: While NODE_V8_COVERAGE can collect subprocess coverage data, Vitest doesn't merge this data with the main coverage report, resulting in 0% statement coverage despite successful data collection.

### Subprocess Coverage Collection with Istanbul/nyc

**Investigation Results**: Switched from V8 to Istanbul provider, installed nyc, attempted subprocess instrumentation.

- **Good**, because Istanbul/nyc has better subprocess coverage support than V8 in some contexts
- **Good**, because it's the approach used by Node Tap for subprocess coverage
- **Bad**, because Vitest + Istanbul still doesn't automatically collect subprocess coverage
- **Bad**, because manual nyc instrumentation significantly slows test execution
- **Bad**, because it requires additional configuration and tooling complexity
- **Bad**, because even with proper Istanbul setup, coverage remains at 0% for scripts

**Technical Finding**: Even with Istanbul provider and nyc installation, Vitest doesn't collect or merge subprocess coverage. Manual instrumentation attempts failed to improve coverage metrics.

### Dual Testing Strategy (Unit + Integration)

**Chosen Approach**: Separate unit tests that import script functions directly, plus integration tests that validate CLI execution.

- **Good**, because unit tests provide accurate coverage measurement
- **Good**, because integration tests validate end-to-end CLI functionality
- **Good**, because it works reliably with Vitest tooling
- **Good**, because it follows established Node.js testing patterns
- **Good**, because test execution remains fast and predictable
- **Good**, because it's maintainable and doesn't require complex tooling
- **Good**, because it enforces minimal CLI-only code paths, maximizing testable coverage
- **Neutral**, because it requires maintaining two test files per script
- **Bad**, because CLI-specific code paths may not be covered by unit tests (minimized by design)

**Implementation Pattern**:

```typescript
// Unit tests: src/tests/scripts/copy-assets-unit.test.ts
import {
  copyAssets,
  ensureDir,
  formatCLIOutput,
} from '../../scripts/copy-assets';

// Integration tests: src/tests/scripts/copy-assets.test.ts
execSync(`npx tsx ${scriptPath}`, { cwd: testDir });
```

**Code Architecture Example**:

```typescript
// ✅ GOOD: All business logic exportable and testable
export async function copyAssets() {
  /* business logic */
}
export function formatCLIOutput(result) {
  /* formatting logic */
}

// ✅ GOOD: Minimal CLI section with coverage exclusion
/* istanbul ignore if */
if (process.argv[1] === new URL(import.meta.url).pathname) {
  /* istanbul ignore next */
  (async () => {
    try {
      const result = await copyAssets();
      formatCLIOutput(result);
    } catch (err) {
      stderr.write(`❌ ${String(err)}\n`);
      exit(1);
    }
  })();
}
```

**Code Architecture Requirement**: CLI-only code paths must be minimized to maximize testable coverage. Scripts should follow the "main function" pattern where:

- All business logic is in exportable functions (100% unit testable)
- CLI section only handles: argument parsing, function execution, basic output formatting, and error handling
- Even output formatting should be extracted to testable functions when possible
- The CLI guard `if (process.argv[1] === new URL(import.meta.url).pathname)` isolates minimal untestable code
- Use `/* istanbul ignore if */` and `/* istanbul ignore next */` comments to exclude remaining CLI-only code from coverage requirements

Reference: [Main function pattern in Node.js](https://mathieularose.com/main-function-in-node-js)

### Pure Integration Testing Only

**Not Chosen**: Testing only through subprocess execution without unit testing.

- **Good**, because it tests real-world usage patterns
- **Good**, because it requires minimal test code
- **Bad**, because it provides 0% coverage measurement (confirmed through investigation)
- **Bad**, because it doesn't meet project coverage requirements
- **Bad**, because debugging failures is more difficult
- **Bad**, because it doesn't validate individual function behavior

### Pure Unit Testing Only

**Not Chosen**: Testing only exported functions without subprocess validation.

- **Good**, because it provides excellent coverage measurement
- **Good**, because it enables focused testing of individual functions
- **Bad**, because it doesn't validate CLI interface functionality
- **Bad**, because it doesn't test the actual execution environment
- **Bad**, because CLI-specific code (argument parsing, process.exit, etc.) remains untested

## More Information

### Technical Investigation Summary

**Tools and Approaches Tested**:

1. ✅ **NODE_V8_COVERAGE manual setup**: Successfully collected subprocess coverage data but Vitest didn't merge it
2. ✅ **Istanbul provider switch**: Changed from V8 to Istanbul provider in Vitest configuration
3. ✅ **nyc installation and configuration**: Installed nyc and attempted manual subprocess instrumentation
4. ✅ **Environment variable inheritance**: Tested proper environment variable passing to subprocesses
5. ✅ **Coverage directory verification**: Confirmed subprocess coverage files were created but not merged

**Key Technical Findings**:

- Vitest is designed primarily for in-process testing, not subprocess coverage collection
- Both V8 and Istanbul providers in Vitest have the same subprocess coverage limitations
- Manual coverage collection works but requires complex merging that Vitest doesn't provide
- Node Tap's subprocess coverage capabilities don't translate directly to Vitest
- Istanbul provides `/* istanbul ignore if */` and `/* istanbul ignore next */` comments for excluding CLI-only code from coverage requirements (per ADR-0009)

**Coverage Results Comparison**:

```bash
# Before dual strategy: Scripts at 0% coverage
Scripts |   0.00 |    0.00 |    0.00 |   0.00 |

# After dual strategy: Scripts at 73%+ coverage
Scripts |  73.41 |   82.60 |  100.00 |  73.41 |
```

**References**:

- [ADR-0009: Adopt Istanbul as Coverage Engine for Vitest](./0009-adopt-istanbul-as-coverage-engine-for-vitest.md)
- [Stack Overflow: Vitest coverage reporting issues](https://stackoverflow.com/questions/77971541/coverage-command-with-vitest-wont-return-the-coverage-report-why)
- [Vitest Coverage Guide](https://vitest.dev/guide/coverage.html)
- [Istanbul.js TypeScript Tutorial](https://istanbul.js.org/docs/tutorials/typescript/)
- [Node Tap subprocess coverage documentation](https://istanbul.js.org/docs/tutorials/tap/)

**Decision Confidence**: High - based on extensive technical investigation and clear evidence that subprocess coverage collection is not practical with Vitest tooling.

**Future Reevaluation Triggers**:

- Vitest adds native subprocess coverage collection support
- Project migrates to different testing framework with better subprocess coverage
- Coverage requirements change to allow different measurement approaches
