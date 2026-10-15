# ADR-003: Test Infrastructure with Vitest and Playwright

**Status**: Accepted

**Date**: 2024-2025 (retroactive documentation)

## Context

The Animation Catalog requires comprehensive testing to ensure:

1. **Component Correctness**: Animations render and behave as expected
2. **Performance**: No regressions in animation performance
3. **Determinism**: Tests produce consistent results across runs
4. **Visual Quality**: Animations look correct in browsers
5. **Accessibility**: Interactive animations are keyboard/screen-reader accessible
6. **Fast Feedback**: Tests run quickly during development

Testing needs:
- **Unit Tests**: Component logic, hooks, services
- **Integration Tests**: Component interactions, state management
- **E2E Tests**: Full user flows, visual validation
- **Performance Tests**: Animation FPS, bundle size

Test frameworks considered:
1. **Jest + React Testing Library**: Industry standard
2. **Vitest + Testing Library**: Modern, faster, Vite-native
3. **Cypress**: Popular E2E framework
4. **Playwright**: Modern E2E with better features

## Decision

We chose a **two-tier testing strategy**:

### Tier 1: Unit & Integration Tests with Vitest

- **Vitest** as the test runner (instead of Jest)
- **React Testing Library** for component testing
- **Deterministic test environment** with controlled randomness

**Why Vitest over Jest:**
- Native Vite integration (faster, no config duplication)
- ES modules support out of the box
- Faster test execution (parallel by default)
- Compatible Jest API (easy migration)
- Better TypeScript support

### Tier 2: E2E Tests with Playwright

- **Playwright** for end-to-end browser testing
- Visual validation for animations
- Cross-browser testing (Chromium, Firefox, WebKit)
- Accessibility audits

**Why Playwright over Cypress:**
- Multi-browser support (Cypress only Chrome-based)
- Better API for async operations
- Built-in test artifacts (screenshots, videos, traces)
- Faster execution
- Better debugging with Playwright Inspector

## Implementation

### Directory Structure

```
src/
  __tests__/               # Unit & integration tests
    *.test.tsx
  components/
    **/*.test.tsx          # Co-located component tests

tests/
  e2e/                     # Playwright E2E tests
    *.spec.ts

scripts/
  run-vitest.mjs           # Vitest wrapper with deterministic env
  run-playwright.mjs       # Playwright wrapper
  cleanup-vitest.mjs       # Kill stray Vitest workers
```

### Test Commands

```bash
npm test              # Run all Vitest tests (deterministic wrapper)
npm run test:e2e      # Run Playwright tests (headless)
npm run test:headed   # Run Playwright with UI
npm run typecheck     # TypeScript validation
```

### Deterministic Testing

To prevent flaky tests, we enforce determinism:

```javascript
// scripts/run-vitest.mjs
process.env.DETERMINISTIC_TEST_ENV = '1'
process.env.TZ = 'UTC'
// Seeds for random number generators if needed
```

**Benefits:**
- Tests produce same results every run
- No timing-dependent failures
- Easier to reproduce issues
- CI/CD reliability

### Key Configurations

**`vitest.config.ts`:**
```typescript
export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['**/*.test.{ts,tsx}', '**/node_modules/**'],
    },
  },
})
```

**`playwright.config.ts`:**
```typescript
export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  retries: 2,
  use: {
    baseURL: 'http://localhost:5173',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: devices['Desktop Chrome'] },
    { name: 'firefox', use: devices['Desktop Firefox'] },
    { name: 'webkit', use: devices['Desktop Safari'] },
  ],
})
```

## Consequences

### Positive

- **Fast Feedback**: Vitest is 2-3x faster than Jest for our test suite
- **Vite Native**: No config duplication, same build pipeline
- **Better DX**: Hot reload for tests, watch mode with UI
- **Deterministic**: Controlled environment prevents flakiness
- **Multi-Browser**: Playwright ensures cross-browser compatibility
- **Visual Validation**: Screenshot comparison catches visual regressions
- **CI Integration**: Both tools have excellent GitHub Actions support

### Negative

- **Learning Curve**: Team needs to learn Playwright (different from Cypress)
- **Test Maintenance**: E2E tests can be brittle with DOM changes
- **Performance Overhead**: Full browser tests are slower than unit tests
- **Vitest Memory Leaks**: Historical issue requiring cleanup script

### Mitigation Strategies

1. **Cleanup Script**: `cleanup-vitest.mjs` kills stray workers
2. **Test Wrappers**: `run-vitest.mjs` and `run-playwright.mjs` set deterministic env
3. **Retry Logic**: Playwright configured with 2 retries for flaky tests
4. **Selective E2E**: Only critical user flows in E2E, rest in integration tests
5. **CI Optimization**: Run unit tests first, E2E in parallel jobs

## Testing Strategy

### What to Unit Test

- ✅ Component rendering with Testing Library
- ✅ Hook logic (`useAnimations`, etc.)
- ✅ Service functions (`animationData`, `preload`)
- ✅ Utility functions
- ✅ State machine transitions (if implemented)

### What to E2E Test

- ✅ Full navigation flows (group switching, URL sync)
- ✅ Visual animations (screenshot comparison)
- ✅ Drawer interactions
- ✅ Error boundary fallback
- ✅ Responsive layouts

### What NOT to Test

- ❌ Third-party library internals (Framer Motion)
- ❌ Styling details (use visual regression instead)
- ❌ Browser-specific quirks (leave to Playwright)

## Alternatives Not Chosen

### Jest

**Pros**: Industry standard, huge ecosystem
**Cons**: Slower, requires Babel config, worse Vite integration

### Cypress

**Pros**: Great DX, popular, good docs
**Cons**: Chrome-only, slower, limited multi-window support

### Storybook + Chromatic

**Pros**: Visual testing, component library
**Cons**: Overhead for simple catalog, costly for commercial use

## Future Enhancements

1. **Performance Testing**: Add Lighthouse CI for performance budgets
2. **Visual Regression**: Integrate Percy or Chromatic for screenshot diffing
3. **Coverage Goals**: Target 80%+ unit test coverage
4. **Mutation Testing**: Use Stryker for test quality validation
5. **Fake Timers**: Use `vi.useFakeTimers()` for timer-based animations

## References

- `vitest.config.ts` - Vitest configuration
- `playwright.config.ts` - Playwright configuration
- `scripts/run-vitest.mjs` - Test wrapper
- `scripts/run-playwright.mjs` - E2E wrapper
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
