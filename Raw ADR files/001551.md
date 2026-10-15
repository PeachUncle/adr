# ADR-012: Test Framework Standardization (Vitest Only)

**Status:** Accepted  
**Date:** November 2, 2025  
**Decision Makers:** Engineering Team  
**Related:** ADR-009 (Mock Data Removal), Pre-commit Hooks

---

## Context

### The Problem

We discovered mixed test framework syntax across the codebase:

- Some tests use **Jest** (`jest.mock()`, `jest.fn()`, `jest.clearAllMocks()`)
- Other tests use **Vitest** (`vi.mock()`, `vi.fn()`, `vi.clearAllMocks()`)
- This creates:
  - **Unprofessional appearance** - Inconsistent patterns suggest lack of standards
  - **Maintenance overhead** - Developers must remember which syntax to use
  - **Flaky tests** - Tests fail when Jest globals aren't available in Vitest environment
  - **Wasted time** - Repeatedly converting between frameworks

### Current State

**Test Configuration:**

- `vitest.config.ts` with `globals: true`
- `src/test/setup.ts` with comprehensive mocks
- Package.json: `"test": "vitest"`

**Discovered Issues (Nov 2, 2025):**

1. `src/app/api/favorites/__tests__/route.test.ts` - Used Jest syntax, failed to run
2. `src/__tests__/api/affiliate-links.test.ts` - Uses Jest syntax (not verified)
3. No pre-commit checks to prevent Jest syntax in new tests

**Impact:**

- Tests written in Jest syntax don't run until converted
- Pre-commit hooks pass but tests fail in CI
- Inconsistent developer experience

---

## Decision

**We will standardize on Vitest as our only test framework.**

### Rules

1. **All tests must use Vitest syntax:**
   - ✅ `vi.mock()` not `jest.mock()`
   - ✅ `vi.fn()` not `jest.fn()`
   - ✅ `vi.clearAllMocks()` not `jest.clearAllMocks()`
   - ✅ `vi.spyOn()` not `jest.spyOn()`
   - ✅ Import from `'vitest'`: `import { describe, it, expect, beforeEach, vi } from 'vitest'`

2. **No Jest dependencies or types:**
   - ❌ Remove `@types/jest` from `package.json`
   - ❌ Remove `jest.config.js` if it exists
   - ✅ Use `vitest.config.ts` exclusively

3. **Pre-commit enforcement:**
   - Scan all test files for Jest syntax
   - Block commits with Jest patterns
   - Provide helpful error messages with Vitest equivalents

4. **Documentation requirements:**
   - Update `CONTRIBUTING.md` with test framework standards
   - Add Vitest examples to developer guides
   - Document common patterns in `src/test/README.md`

---

## Implementation

### Phase 1: Pre-commit Hook (IMMEDIATE)

**File:** `scripts/maintenance/check-test-framework.js`

```javascript
#!/usr/bin/env node
/**
 * Enforces Vitest-only test framework syntax
 * Blocks Jest syntax to maintain consistency
 */

const fs = require('fs');
const path = require('path');

const JEST_PATTERNS = [
  { pattern: /jest\.mock\(/g, replacement: 'vi.mock(', severity: 'ERROR' },
  { pattern: /jest\.fn\(/g, replacement: 'vi.fn(', severity: 'ERROR' },
  {
    pattern: /jest\.clearAllMocks\(/g,
    replacement: 'vi.clearAllMocks(',
    severity: 'ERROR',
  },
  { pattern: /jest\.spyOn\(/g, replacement: 'vi.spyOn(', severity: 'ERROR' },
  {
    pattern: /jest\.resetAllMocks\(/g,
    replacement: 'vi.resetAllMocks(',
    severity: 'ERROR',
  },
  {
    pattern: /jest\.restoreAllMocks\(/g,
    replacement: 'vi.restoreAllMocks(',
    severity: 'ERROR',
  },
  {
    pattern: /: jest\.Mock/g,
    replacement: ': ReturnType<typeof vi.fn>',
    severity: 'ERROR',
  },
  {
    pattern: /: jest\.Mocked/g,
    replacement: ': ReturnType<typeof vi.fn>',
    severity: 'ERROR',
  },
  {
    pattern: /jest\.MockedFunction/g,
    replacement: 'ReturnType<typeof vi.fn>',
    severity: 'ERROR',
  },
];

const TEST_FILE_PATTERNS = [
  '**/*.test.ts',
  '**/*.test.tsx',
  '**/*.spec.ts',
  '**/*.spec.tsx',
  '**/__tests__/**/*.ts',
  '**/__tests__/**/*.tsx',
];

function checkFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const violations = [];

  for (const { pattern, replacement, severity } of JEST_PATTERNS) {
    const matches = content.match(pattern);
    if (matches) {
      violations.push({
        file: filePath,
        pattern: pattern.source,
        replacement,
        severity,
        count: matches.length,
      });
    }
  }

  return violations;
}

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error('Usage: node check-test-framework.js <file1> <file2> ...');
    process.exit(1);
  }

  const allViolations = [];

  for (const file of args) {
    // Only check test files
    if (
      !file.includes('.test.') &&
      !file.includes('.spec.') &&
      !file.includes('__tests__')
    ) {
      continue;
    }

    const violations = checkFile(file);
    allViolations.push(...violations);
  }

  if (allViolations.length > 0) {
    console.error('\n❌ Jest syntax detected in test files\n');
    console.error(
      'We use Vitest exclusively. Please convert to Vitest syntax:\n'
    );

    const grouped = {};
    for (const v of allViolations) {
      if (!grouped[v.file]) grouped[v.file] = [];
      grouped[v.file].push(v);
    }

    for (const [file, violations] of Object.entries(grouped)) {
      console.error(`\n📄 ${file}:`);
      for (const v of violations) {
        console.error(`  - ${v.pattern} (${v.count}x)`);
        console.error(`    Replace with: ${v.replacement}`);
      }
    }

    console.error('\n📚 Quick fix commands:\n');
    for (const [file] of Object.entries(grouped)) {
      console.error(`  sed -i '' 's/jest\\.mock(/vi.mock(/g' ${file}`);
      console.error(`  sed -i '' 's/jest\\.fn(/vi.fn(/g' ${file}`);
      console.error(
        `  sed -i '' 's/jest\\.clearAllMocks(/vi.clearAllMocks(/g' ${file}`
      );
    }

    console.error(
      '\n📖 See: docs/development/ADR/012-test-framework-standardization.md\n'
    );
    process.exit(1);
  }

  console.log('✅ All test files use Vitest syntax');
  process.exit(0);
}

main();
```

### Phase 2: Update Pre-commit Hook

**File:** `.husky/pre-commit`

Add before linting:

```bash
# Check test framework consistency
echo "🧪 Checking test framework syntax..."
node scripts/maintenance/check-test-framework.js $(git diff --cached --name-only --diff-filter=ACM | grep -E '\.test\.(ts|tsx)$|\.spec\.(ts|tsx)$|__tests__/')
```

### Phase 3: Convert Existing Tests

**Files to convert:**

1. ✅ `src/app/api/favorites/__tests__/route.test.ts` - DONE
2. ⚠️ `src/__tests__/api/affiliate-links.test.ts` - TODO

**Conversion pattern:**

```bash
# Automated conversion
sed -i '' 's/jest\.mock(/vi.mock(/g' FILE
sed -i '' 's/jest\.fn(/vi.fn(/g' FILE
sed -i '' 's/jest\.clearAllMocks(/vi.clearAllMocks(/g' FILE
sed -i '' 's/jest\.spyOn(/vi.spyOn(/g' FILE

# Add imports if missing
# import { describe, it, expect, beforeEach, vi } from 'vitest';
```

### Phase 4: Documentation Updates

**CONTRIBUTING.md:**

````markdown
## Testing Standards

### Test Framework: Vitest

We use **Vitest exclusively** for all tests. Do not use Jest syntax.

**Why Vitest?**

- Faster than Jest (native ESM, no transpilation)
- Better TypeScript support out of the box
- Vite-native (matches our Next.js + Vite setup)
- Compatible API with Jest, but more modern

**Required Syntax:**

```typescript
// ✅ CORRECT - Vitest
import { describe, it, expect, beforeEach, vi } from 'vitest';

vi.mock('@/lib/mongodb');
const mockFn = vi.fn();
vi.clearAllMocks();
```
````

```typescript
// ❌ WRONG - Jest (will fail pre-commit)
jest.mock('@/lib/mongodb');
const mockFn = jest.fn();
jest.clearAllMocks();
```

**Pre-commit Checks:**

- All test files are scanned for Jest syntax
- Commits are blocked if Jest patterns are found
- See `docs/development/ADR/012-test-framework-standardization.md` for details

````

---

## Consequences

### Positive

✅ **Consistency:** All tests use the same syntax
✅ **Fewer failures:** Tests don't fail due to framework mismatch
✅ **Faster reviews:** No need to check for framework inconsistencies
✅ **Professional appearance:** Shows attention to detail and standards
✅ **Easier onboarding:** New developers learn one framework
✅ **Better CI/CD:** No surprise test failures in pipeline

### Negative

⚠️ **Initial conversion time:** Must convert existing Jest tests
⚠️ **Developer habit:** Devs familiar with Jest must adjust
⚠️ **Documentation debt:** Must update all testing guides

### Neutral

- Vitest and Jest APIs are ~95% compatible, so learning curve is minimal
- Most developers already know Jest, so Vitest is easy to pick up

---

## Alternatives Considered

### Alternative 1: Support Both Jest and Vitest

**Rejected because:**
- Doubles maintenance burden (two configs, two setups)
- Confuses developers (which framework for which test?)
- Pre-commit hooks become complex
- Unprofessional appearance

### Alternative 2: Use Jest Exclusively

**Rejected because:**
- Vitest is faster and more modern
- We're already using Vite/Next.js, Vitest integrates better
- Our `vitest.config.ts` is already set up and working
- Jest requires additional configuration for ESM support

### Alternative 3: No Enforcement (Let Developers Choose)

**Rejected because:**
- Leads to the current problem (mixed frameworks)
- No consistency = unprofessional
- Wastes time debugging framework issues

---

## Validation

**Success Criteria:**

1. ✅ All test files use Vitest syntax only
2. ✅ Pre-commit hook blocks Jest syntax
3. ✅ `pnpm test` runs without framework errors
4. ✅ Documentation updated (CONTRIBUTING.md, ADRs)
5. ✅ CI/CD pipeline passes with 100% Vitest

**Testing:**

```bash
# 1. Check for any Jest syntax in codebase
grep -r "jest\\.mock\|jest\\.fn\|jest\\.clearAllMocks" src/ --include="*.test.ts" --include="*.spec.ts"

# 2. Run all tests
pnpm test --run

# 3. Test pre-commit hook
echo "jest.mock('@/lib/test')" > test-file.test.ts
git add test-file.test.ts
git commit -m "test" # Should fail

# 4. Verify enforcement
pnpm test:unit # Should pass
````

---

## Migration Plan

### Immediate (Today - Nov 2, 2025)

- [x] Create ADR-012
- [ ] Create `check-test-framework.js` script
- [ ] Add to pre-commit hook
- [ ] Convert `affiliate-links.test.ts` to Vitest
- [ ] Test pre-commit enforcement

### Short Term (This Week)

- [ ] Update CONTRIBUTING.md
- [ ] Update developer guides
- [ ] Create `src/test/README.md` with examples
- [ ] Audit all test files for Jest syntax

### Long Term (Ongoing)

- [ ] All new tests use Vitest by default
- [ ] CI/CD reports test framework violations
- [ ] Regular audits to ensure compliance

---

## Related Documentation

- [ADR-009: Mock Data Removal Strategy](./009-mock-data-removal-strategy.md)
- [ADR-011: Frontend Component Architecture](./011-frontend-component-architecture.md)
- [Pre-commit Hook Documentation](../ENTERPRISE_QUALITY_CHECKS.md)
- [Testing Guide](../../testing/TEST_STRATEGY.md)

---

## References

- [Vitest Documentation](https://vitest.dev/)
- [Vitest vs Jest](https://vitest.dev/guide/comparisons.html#jest)
- [Migration Guide: Jest → Vitest](https://vitest.dev/guide/migration.html)

---

**Decision:** Standardize on Vitest exclusively, enforce via pre-commit hooks  
**Rationale:** Consistency, speed, professionalism  
**Impact:** Low (APIs are similar), High ROI (prevents future issues)

---

_Last Updated: November 2, 2025_  
_Status: Accepted and In Implementation_
