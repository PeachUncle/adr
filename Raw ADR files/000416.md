# ADR 002: Use FTA for TypeScript Code Quality Metrics

**Status:** Accepted  
**Date:** 2025-11-20  
**Decision Makers:** Development Team  
**Related:** [ADR 001: Use Vitest for TypeScript](./001-use-vitest-for-typescript.md)

## Context

The repository had no automated way to measure or enforce TypeScript code quality beyond basic linting and type checking. While ESLint and TypeScript compiler provide valuable checks, they don't give quantifiable metrics about code complexity and maintainability.

We needed a solution that would:

1. Provide objective, quantifiable code quality metrics
2. Integrate easily with our CI/CD pipeline
3. Run fast enough for frequent use
4. Support TypeScript natively
5. Offer clear, actionable feedback
6. Allow us to establish and track quality baselines

## Decision

We will use **FTA (Fast TypeScript Analyzer)** for measuring and enforcing TypeScript code quality metrics.

### Key Decisions

1. **Tool Selection**: FTA (Fast TypeScript Analyzer) v3.0.0
2. **Score Threshold**: 50 (files exceeding this fail CI) - updated from initial 60
3. **Analysis Scope**: All TypeScript and JavaScript files in `src/`
4. **CI Integration**: Run FTA in the `test-typescript` workflow job
5. **Configuration**: Score cap via CLI argument in npm scripts

## Rationale

### Why FTA?

**Alternatives Considered:**

| Tool | Pros | Cons | Decision |
|------|------|------|----------|
| **FTA** | ✅ TypeScript-native<br>✅ Very fast (Rust-based)<br>✅ Comprehensive metrics<br>✅ Simple CLI<br>✅ Clear thresholds | ⚠️ Newer tool<br>⚠️ Smaller ecosystem | **✅ Selected** |
| **Code Climate** | ✅ Mature<br>✅ GitHub integration | ❌ Requires external service<br>❌ Commercial for private repos<br>❌ Slower | ❌ Rejected |
| **SonarQube** | ✅ Comprehensive<br>✅ Mature | ❌ Heavy setup<br>❌ Requires server<br>❌ Overkill for our needs | ❌ Rejected |
| **ESLint complexity rules** | ✅ Already using ESLint | ❌ Limited metrics<br>❌ Not file-level scoring<br>❌ No composite score | ❌ Insufficient |
| **TypeScript compiler** | ✅ Already using | ❌ No complexity metrics<br>❌ Only type safety | ❌ Insufficient |

**FTA was selected because:**

1. **Speed**: Analyzes entire codebase in milliseconds (Rust-based)
2. **TypeScript Focus**: Built specifically for TypeScript/JavaScript analysis
3. **Comprehensive Metrics**: Cyclomatic complexity, Halstead metrics, and composite FTA score
4. **Simple Integration**: Single npm package, no external services required
5. **Clear Thresholds**: Score-based system with obvious pass/fail criteria
6. **Zero Configuration**: Works out of the box with sensible defaults
7. **Active Development**: Modern tool with regular updates

### Why Score Cap of 50?

**Initial Baseline Analysis:**

```
├─ solution.ts (32 lines): FTA Score 41.34 - OK
├─ solution.test.ts (91 lines): FTA Score 12.77 - OK
├─ folderManager.js (121 lines): FTA Score 51.51 - Could be better
└─ setup.js (70 lines): FTA Score 44.21 - OK
```

**After Refactoring:**

```
├─ solution.ts (32 lines): FTA Score 41.34 - OK
├─ solution.test.ts (91 lines): FTA Score 12.77 - OK
├─ folderManager.js (103 lines): FTA Score 49.37 - OK (refactored from 51.51 with security fixes)
├─ setup.js (84 lines): FTA Score 45.94 - OK (enhanced error messages)
├─ languageTemplates.js (58 lines): FTA Score 10.99 - OK (extracted)
├─ Year.js (27 lines): FTA Score 41.08 - OK (security value object)
├─ Day.js (23 lines): FTA Score 10.29 - OK (security value object)
├─ Language.js (39 lines): FTA Score 39.57 - OK (security value object)
├─ SafePath.js (37 lines): FTA Score 42.09 - OK (security value object)
└─ validators.js (23 lines): FTA Score 34.04 - OK (shared validation utilities)
```

**Rationale for 50 threshold:**

1. **All current files pass** - After refactoring folderManager.js, all code meets the standard
2. **Aligns with FTA "OK" assessment** - Score of 50 is the boundary of the "OK" range
3. **Proactive quality enforcement** - Stricter than industry standard to encourage better code
4. **Proven achievable** - Demonstrated through successful refactoring of folderManager.js
5. **Encourages modularization** - Lower threshold motivates extracting complex logic into separate modules

### Configuration Decisions

**npm scripts with CLI arguments:**

```json
"fta": "npx fta-cli src --score-cap 50",
"fta:typescript": "npx fta-cli src --score-cap 50"
```

**`.ftarc.json` settings:**

```json
{
  "scoreCap": 50,
  "includeComments": false,
  "excludeUnder": 6,
  "outputLimit": 5000
}
```

**Rationale:**

- **scoreCap: 50** - Explained above; enforced via CLI argument for reliability
- **includeComments: false** - Comments don't affect code complexity
- **excludeUnder: 6** - Skip trivial files (e.g., barrel exports, constants)
- **outputLimit: 5000** - High enough to show all files in foreseeable future

## Consequences

### Positive

✅ **Objective Quality Baseline**: We now have quantifiable metrics for TypeScript code quality  
✅ **Early Detection**: Quality issues caught in CI before code review  
✅ **Trend Tracking**: Can monitor code quality over time  
✅ **Educational**: Developers learn about complexity metrics  
✅ **Fast Feedback**: Analysis completes in < 1 second  
✅ **Clear Standards**: Unambiguous pass/fail criteria  
✅ **Documentation**: Comprehensive guide for understanding metrics  

### Negative

⚠️ **Learning Curve**: Team needs to understand FTA metrics  
⚠️ **Potential Friction**: Failing CI may slow down some PRs initially  
⚠️ **Score Gaming**: Developers might optimize for score instead of readability  
⚠️ **Tool Dependency**: Relying on relatively new tool  

### Mitigations

1. **Documentation**: Comprehensive guide in `docs/TYPESCRIPT_CODE_QUALITY_METRICS.md`
2. **Achievable Threshold**: Score cap of 50 proven achievable through refactoring demonstration
3. **Context in Decisions**: FTA score is one signal, not the only measure of quality
4. **Refactoring Guidance**: Guide includes practical strategies and real examples (folderManager.js)
5. **Education**: Guide includes metrics explanation, refactoring patterns, and best practices

### Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| FTA becomes unmaintained | Medium | Low | Tool is actively developed; can switch if needed |
| False positives block PRs | Medium | Low | Threshold is reasonable; can adjust if problematic |
| Developers game the score | Low | Medium | Emphasize code review and readability over scores |
| Performance degrades with scale | Low | Low | FTA is extremely fast; analyzes 1600 files/sec |

## Implementation

### Changes Made

1. **Dependencies**: Added `fta-cli` as dev dependency
2. **Configuration**: Created `.ftarc.json` with score cap of 50
3. **Scripts**: Added `fta` and `fta:typescript` npm scripts with `--score-cap 50` CLI argument
4. **CI Workflow**: Added FTA analysis step to `test-typescript` job
5. **Code Refactoring**: Refactored `folderManager.js` to meet the 50 threshold
   - Extracted language templates into `languageTemplates.js` module
   - Reduced cyclomatic complexity through better separation of concerns
   - Improved from FTA score 51.51 to 49.37
6. **Documentation**: Created comprehensive guide in `docs/TYPESCRIPT_CODE_QUALITY_METRICS.md`
7. **ADR**: This document

### Integration Points

**CI Pipeline (`test-typescript` job):**

```yaml
- name: TypeScript type checking
  run: npm run typecheck:typescript

- name: ESLint checking
  run: npm run lint:typescript

- name: FTA code quality analysis   # ← NEW
  run: npm run fta:typescript        # ← NEW

- name: Run TypeScript tests
  run: npm run test:typescript
```

**npm Scripts:**

```json
{
  "fta": "npx fta-cli src --score-cap 50",
  "fta:typescript": "npx fta-cli src --score-cap 50"
}
```

### Rollback Plan

If FTA proves problematic:

1. Remove FTA step from `.github/workflows/ci.yml`
2. Remove `fta` and `fta:typescript` scripts from `package.json`
3. Remove `fta-cli` from `devDependencies`
4. Remove `.ftarc.json`
5. Mark this ADR as **Superseded**

## Validation

### Hypothesis

> **We believe that** adding TypeScript code metrics  
> **Will result in** higher code quality  
> **We will know we have succeeded when:**
> - ✅ We have a baseline measure of TypeScript code quality (Score cap: 50, lowered from 60)
> - ✅ We have a collection of TypeScript code quality metrics (Cyclomatic, Halstead, FTA Score)
> - ✅ We have foundation documentation (TYPESCRIPT_CODE_QUALITY_METRICS.md)
> - ✅ We have demonstrated refactoring capability (folderManager.js: 51.51 → 49.37)

### Success Criteria

- [x] FTA configured with baseline threshold (50, refined from initial 60)
- [x] FTA runs automatically in CI for all JavaScript/TypeScript
- [x] CI fails if FTA thresholds exceeded
- [x] All current code passes FTA checks (after refactoring)
- [x] Documentation created and comprehensive
- [x] All existing tests still pass
- [x] Demonstrated successful refactoring to meet stricter threshold

### Metrics to Track

Going forward, we should track:

1. **Average FTA Score** across all TypeScript files
2. **Number of files** exceeding score thresholds
3. **Trend over time** (improving vs. degrading)
4. **Time to fix** quality issues caught by FTA
5. **False positive rate** (if any)

## Related Documents

- [Hypothesis-Driven Design Guide](../HYPOTHESIS_DRIVEN_DESIGN.md)
- [TypeScript Code Quality Metrics Guide](../TYPESCRIPT_CODE_QUALITY_METRICS.md)
- [GitHub Copilot Development Guide](../github-copilot-development-guide.md)
- [ADR 001: Use Vitest for TypeScript](./001-use-vitest-for-typescript.md)

## References

- [FTA Project Website](https://ftaproject.dev/)
- [FTA GitHub Repository](https://github.com/sgb-io/fta)
- [FTA npm Package](https://www.npmjs.com/package/fta-cli)
- [Cyclomatic Complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity)
- [Halstead Complexity Measures](https://en.wikipedia.org/wiki/Halstead_complexity_measures)

---

**Approved by:** Development Team  
**Implementation Date:** 2025-11-20  
**Review Date:** 2026-02-20 (3 months)
