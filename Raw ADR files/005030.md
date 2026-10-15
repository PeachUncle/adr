# ADR-006: Playwright for End-to-End Testing

**Status:** Accepted
**Date:** 2025-11-15
**Deciders:** Alice (Architect), Tess (Test Architect), Charlie (Developer)
**Technical Story:** Epic 6 - Story 6-10 (Dashboard E2E Tests)

## Context and Problem Statement

The Agent Orchestrator dashboard requires comprehensive end-to-end testing to ensure critical user flows work correctly across different browsers and devices. We need a testing framework that supports cross-browser testing, provides good developer experience, integrates with CI/CD, and can test modern web features including WebSocket connections.

## Decision Drivers

* Cross-browser testing (Chromium, Firefox, WebKit/Safari)
* Cross-device testing (Desktop, Tablet, Mobile viewports)
* Accessibility testing (WCAG 2.1 Level AA compliance)
* Modern web API support (WebSocket, localStorage, etc.)
* Parallel test execution for fast CI/CD
* Good debugging experience
* Active maintenance and community
* CI/CD integration

## Considered Options

* **Option 1:** Playwright
* **Option 2:** Cypress
* **Option 3:** Selenium WebDriver
* **Option 4:** Puppeteer

## Decision Outcome

**Chosen option:** "Playwright", because it provides true cross-browser testing (Chromium, Firefox, WebKit), excellent performance with parallel execution, built-in accessibility tools, modern API design, and superior debugging experience compared to alternatives.

### Positive Consequences

* True cross-browser testing (Chromium, Firefox, WebKit)
* Fast parallel execution (4-shard CI setup, ~5-10 min total)
* Built-in auto-waiting eliminates flaky tests
* Excellent debugging (screenshots, videos, traces)
* Native TypeScript support
* Page Object Model pattern support
* Accessibility testing with built-in tools
* Modern async/await API (no cy.then chains)
* Network interception for WebSocket testing
* Mobile viewport testing built-in

### Negative Consequences

* Larger test binary size (~300MB browsers)
* Newer than Cypress (smaller ecosystem, but growing fast)
* Some edge cases require more configuration than Cypress

## Pros and Cons of the Options

### Option 1: Playwright

Modern, cross-browser testing framework from Microsoft.

**Pros:**
* **True cross-browser** (Chromium, Firefox, WebKit)
* Excellent performance (parallel execution)
* Auto-waiting (no explicit waits needed)
* Built-in test artifacts (screenshots, videos, traces)
* Modern async/await API
* Native TypeScript support
* Active development (Microsoft-backed)
* Page Object Model support
* Mobile viewport testing
* Network interception

**Cons:**
* Large browser binaries (~300MB)
* Newer than Cypress (2020 vs 2015)
* Smaller ecosystem

### Option 2: Cypress

Popular JavaScript testing framework with time-travel debugging.

**Pros:**
* Large community and ecosystem
* Time-travel debugger
* Automatic screenshot/video
* Good documentation
* Established patterns

**Cons:**
* **Chromium-only** (Firefox/WebKit support experimental)
* Chained API (cy.then, less modern)
* Can't test multiple tabs/windows
* **Flaky auto-waiting** (race conditions common)
* **Slower than Playwright** (~2x in benchmarks)
* No native TypeScript (requires extra config)
* Difficult WebSocket testing

### Option 3: Selenium WebDriver

Industry-standard, mature testing framework.

**Pros:**
* Most mature option (since 2004)
* Huge ecosystem
* Multi-language support
* Cross-browser support

**Cons:**
* **Very slow** (no auto-waiting, explicit waits needed)
* **Flaky tests common** (timing issues)
* Complex setup
* Outdated API design
* Poor developer experience
* Debugging difficult
* Not designed for modern web

### Option 4: Puppeteer

Headless Chrome automation from Google.

**Pros:**
* Fast (Chrome DevTools Protocol)
* Good for scraping/automation
* Lightweight
* Good documentation

**Cons:**
* **Chrome/Chromium only**
* Not designed for cross-browser testing
* Manual wait management
* Less suitable for E2E testing
* Primarily an automation tool, not test framework

## Links

* [Playwright Documentation](https://playwright.dev/)
* [Playwright Best Practices](https://playwright.dev/docs/best-practices)
* [Playwright vs Cypress Comparison](https://playwright.dev/docs/why-playwright)
* [Epic 6 Retrospective](../epics/epic-6-retrospective.md)
* Implementation: `tests/e2e/`, `tests/support/pages/`

## Implementation Notes

### Test Suites (7 suites, 155 tests total)
1. **project-management.spec.ts** (20 tests) - List/detail views, CRUD
2. **escalation-interface.spec.ts** (25 tests) - Filters, modals, responses
3. **kanban-board.spec.ts** (30 tests) - Drag-and-drop, 6 columns, filters
4. **dependency-graph.spec.ts** (25 tests) - D3.js graph, zoom/pan, export
5. **realtime-updates.spec.ts** (15 tests) - WebSocket, multi-tab sync
6. **responsive-design.spec.ts** (20 tests) - Desktop/tablet/mobile
7. **accessibility.spec.ts** (30 tests) - WCAG 2.1 AA compliance

### Page Object Model Pattern
```typescript
class ProjectsListPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/projects');
  }

  async searchProjects(query: string) {
    await this.page.getByPlaceholder('Search projects').fill(query);
  }

  async getProjectCards() {
    return this.page.getByTestId('project-card').all();
  }
}
```

### CI/CD Integration
```yaml
# .github/workflows/test.yml
- name: Run E2E Tests
  run: npm run test:e2e -- --shard=${{ matrix.shard }}/4
  strategy:
    matrix:
      shard: [1, 2, 3, 4]
```

### Browser Configuration
- **Chromium:** Latest stable
- **Firefox:** Latest stable
- **WebKit:** Latest stable
- Browsers cached for faster CI

### Test Results from Story 6-10
- **Total Tests:** 155 E2E tests
- **Pass Rate:** 100% (155/155 passing)
- **Browsers:** All 3 browsers (Chromium, Firefox, WebKit)
- **Devices:** Desktop (1920x1080), Tablet (768x1024), Mobile (375x667)
- **Accessibility:** WCAG 2.1 Level AA compliant
- **CI Time:** ~5-10 minutes (4-shard parallel)

### Flaky Test Prevention
- Auto-waiting (no manual timeouts)
- Test isolation (beforeEach cleanup)
- Burn-in script for detecting flakes (10 iterations)
- No hardcoded waits (use locators)

### Debugging Features
- Screenshots on failure
- Video recording on failure
- Trace viewer for step-by-step replay
- Codegen for recording tests

### Accessibility Testing
```typescript
// Built-in accessibility checks
await expect(page).toBeAccessible(); // Coming soon
// Current: Manual ARIA checks + axe-core planned
```

## Review and Update History

| Date | Reviewer | Change |
|------|----------|--------|
| 2025-11-15 | Alice, Tess, Charlie | Initial decision (Story 6-10) |
| 2025-11-16 | Bob | Documented in ADR with test metrics |
