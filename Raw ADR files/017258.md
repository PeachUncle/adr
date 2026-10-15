---
# === Metadata ===
template_type: "adr"
version: "1.0.0"
created: "2025-10-30"
last_updated: "2025-10-30"
status: "Accepted"
target_audience: ["AI Assistants", "Test Engineers", "Development Team"]
description: "Testing framework and strategy for So Quotable with TDD/BDD approach"

# === ADR Metadata ===
adr_number: "002"
title: "Testing Framework and Strategy"
date: "2025-10-30"
deciders: ["Taylor (Project Owner)"]
tags: ["testing", "TDD", "BDD", "quality", "infrastructure"]
---

# ADR-002: Testing Framework and Strategy

**Date**: 2025-10-30

**Status**: Accepted

**Deciders**: Taylor (Project Owner)

**Tags**: testing, TDD, BDD, quality, infrastructure

---

## Context

So Quotable requires a comprehensive testing strategy that supports Test-Driven Development (TDD) and Behavior-Driven Development (BDD) practices. As a solo developer using AI-assisted development, the testing framework needs to balance production-quality confidence with development velocity.

### Key Requirements

- **Comprehensive BDD/TDD**: Tests serve as executable specifications for AI-assisted development
- **Production Confidence**: High test coverage to ensure reliability
- **Backend-First Approach**: Prioritize testing Convex functions (business logic)
- **Fast Feedback Loop**: Quick test execution for red-green-refactor TDD workflow
- **AI-Friendly**: Patterns that AI can easily generate and maintain
- **Type Safety**: End-to-end TypeScript support

### Technical Context

**Existing Stack** (from ADR-001):

- Frontend: Next.js (App Router) + TypeScript
- Backend: Convex (serverless functions: queries, mutations, actions)
- Database: Convex (document database with TypeScript schema)
- Images: Cloudinary

**Testing Needs**:

- Unit tests for pure functions and utilities
- Integration tests for Convex functions + database
- Component tests for React components
- E2E tests for critical user flows
- Mock external APIs (Cloudinary)

---

## Decision

We will use a **unified Vitest stack** for comprehensive testing with a **backend-first pyramid**.

### Core Testing Stack

```json
{
  "devDependencies": {
    "vitest": "^2.0.0",
    "@vitest/ui": "^2.0.0",
    "convex-test": "^0.0.17",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.1.0",
    "@testing-library/user-event": "^14.5.0",
    "@playwright/test": "^1.45.0"
  }
}
```

### Testing Pyramid (Backend-First)

```
     /\
    /E2E\          10%: Playwright - Critical flows only
   /------\
  /Frontend\       30%: Vitest + Testing Library - Key components
 /----------\
/  Backend   \     60%: Vitest + convex-test - Business logic
--------------
```

**Distribution Rationale**:

- **60% Backend**: Convex functions contain core business logic (quotes, search, verification)
- **30% Frontend**: React components are mostly presentation (thin layer)
- **10% E2E**: Critical paths (search → generate → share)

### Framework Choices

1. **Test Runner**: Vitest
   - Unified runner for all unit/integration tests
   - Fast execution (5-10x faster than Jest)
   - Native TypeScript support
   - ESM-first (matches Next.js + Convex)

2. **Backend Testing**: convex-test
   - Official Convex testing package
   - Real database testing (not mocked)
   - Type-safe test data
   - Transaction rollback per test

3. **Frontend Testing**: Testing Library
   - Component testing focused on user behavior
   - Accessibility-first selectors
   - Works seamlessly with Vitest

4. **E2E Testing**: Playwright
   - Officially recommended by Vercel
   - Best TypeScript support
   - Auto-wait mechanisms (reliable tests)
   - Cross-browser testing built-in

5. **BDD Style**: Native describe/it
   - Given-When-Then in comments
   - No Cucumber.js overhead
   - AI-friendly patterns
   - Can migrate to Cucumber later if needed

### Coverage Goals

- **Backend functions**: 80%+ line coverage
- **Frontend components**: 70%+ line coverage
- **E2E**: Critical user paths only (not measured by coverage)

---

## Consequences

### Positive Consequences

1. **Fast TDD Workflow**
   - Vitest watch mode provides instant feedback (<100ms)
   - Critical for red-green-refactor cycle
   - No build step needed (instant test runs)

2. **Type Safety Throughout**
   - Vitest has native TypeScript support
   - convex-test preserves Convex types
   - Playwright fully typed
   - No type gymnastics required

3. **AI-Friendly Patterns**
   - Single, consistent test syntax (describe/it)
   - Clear, readable test patterns
   - AI can generate tests alongside implementation
   - No complex Gherkin → TypeScript mapping

4. **Unified Mental Model**
   - Same test API (describe/it) across all layers
   - One test runner to learn (Vitest)
   - Consistent assertion library (expect)
   - Simpler onboarding and debugging

5. **Realistic Backend Testing**
   - convex-test uses real database (not mocks)
   - Tests validate actual Convex behavior
   - Catches integration issues early
   - True confidence in backend logic

6. **Production Confidence**
   - Comprehensive coverage (60-30-10 pyramid)
   - E2E tests validate critical flows
   - Backend-first ensures business logic correctness
   - High reliability without excessive test maintenance

7. **Developer Experience**
   - Vitest UI mode for visual debugging
   - Playwright trace viewer for E2E debugging
   - Hot module reload in watch mode
   - Excellent error messages

### Negative Consequences

1. **No Stakeholder-Readable Specs**
   - Tests are TypeScript code, not Gherkin
   - Non-technical stakeholders can't read test files
   - **Mitigation**: Generate documentation from tests if needed
   - **Context**: Solo developer, no stakeholders currently

2. **Newer Ecosystem**
   - Vitest has smaller ecosystem than Jest
   - Fewer StackOverflow answers
   - Some libraries assume Jest
   - **Mitigation**: Vitest API is Jest-compatible, most solutions work

3. **Learning Curve for convex-test**
   - Convex-specific testing patterns
   - Different from traditional database mocking
   - **Mitigation**: Excellent documentation, simpler than mocking

4. **Multiple Tools**
   - Vitest for unit/integration
   - Playwright for E2E
   - Two configurations to maintain
   - **Mitigation**: Both are well-documented, config is straightforward

### Neutral Consequences

1. **Test File Co-location**
   - Tests live next to source files (`.test.ts`)
   - Some developers prefer separate `__tests__` directories
   - Trade-off: Easier discovery vs. cleaner directory structure

2. **BDD Without Cucumber**
   - BDD thinking without formal Gherkin
   - Can always migrate to Cucumber later if needed
   - Decision is reversible

---

## Alternatives Considered

### Alternative 1: Jest + Testing Library + Cypress

**Description**: Traditional testing stack used by many Next.js projects

**Pros**:

- Larger ecosystem and community
- More online resources and tutorials
- Well-established best practices
- Mature tooling and plugins

**Cons**:

- Slower test execution (2-5x slower than Vitest)
- Requires ts-jest for TypeScript
- More configuration needed
- Cypress is slower and less reliable than Playwright
- Not optimized for Convex + Next.js App Router

**Why not chosen**:
Vitest provides significantly faster feedback for TDD, which is critical for productivity. The speed difference (5-10x) compounds over hundreds of test runs per day. Jest's larger ecosystem doesn't offset the velocity loss. Cypress has fallen behind Playwright in reliability and TypeScript support.

### Alternative 2: Full Cucumber.js + Playwright

**Description**: BDD framework with Gherkin feature files and step definitions

**Pros**:

- Business-readable specifications (.feature files)
- Stakeholder collaboration on requirements
- Living documentation
- Clear separation of spec and implementation
- Reusable step definitions

**Cons**:

- Dual-file maintenance (.feature + .steps.ts)
- Slower test execution (Gherkin parsing overhead)
- Harder for AI to generate (two separate syntaxes)
- Lost type safety in step definitions
- More complex debugging (trace through multiple files)
- Overkill for solo developer with no stakeholders

**Why not chosen**:
The overhead of maintaining separate Gherkin files doesn't provide value for a solo developer. All stakeholders (you) can read TypeScript. The complexity slows down AI-assisted test generation and TDD velocity. Native describe/it with Given-When-Then comments provides BDD thinking without the ceremony. Migration to Cucumber remains possible if stakeholders appear later.

### Alternative 3: Vitest + Cypress (Hybrid)

**Description**: Modern test runner with Cypress for E2E

**Pros**:

- Unified modern stack (both are fast)
- Cypress has simpler API than Playwright
- Time-travel debugging in Cypress
- Good developer experience

**Cons**:

- Cypress is slower than Playwright
- Less reliable (more flaky tests)
- Weaker TypeScript support
- Not Vercel's recommendation
- Fewer browser testing options

**Why not chosen**:
Playwright is Vercel's official recommendation for Next.js E2E testing. It's faster, more reliable, and has better TypeScript support. Playwright's auto-wait mechanisms reduce test flakiness. The trace viewer provides better debugging than Cypress's time-travel. For production confidence, reliability trumps API simplicity.

---

## Implementation Notes

### Directory Structure

```
quoteable/
├── src/
│   ├── app/
│   │   └── quotes/
│   │       ├── page.tsx
│   │       └── page.test.tsx       # Co-located
│   ├── components/
│   │   └── QuoteCard/
│   │       ├── QuoteCard.tsx
│   │       └── QuoteCard.test.tsx  # Co-located
│   └── lib/
│       └── utils/
│           ├── formatters.ts
│           └── formatters.test.ts  # Co-located
│
├── convex/
│   ├── quotes.ts
│   ├── quotes.test.ts              # Co-located
│   ├── people.ts
│   └── people.test.ts              # Co-located
│
├── tests/
│   ├── e2e/                        # Playwright E2E
│   │   ├── quoteCreation.spec.ts
│   │   └── search.spec.ts
│   ├── fixtures/                   # Shared test data
│   │   ├── quotes.ts
│   │   └── people.ts
│   └── helpers/                    # Test utilities
│       └── convexTestHelpers.ts
│
├── vitest.config.ts
└── playwright.config.ts
```

### Naming Conventions

- **Unit/Integration**: `*.test.ts` or `*.test.tsx`
- **E2E**: `*.spec.ts` (Playwright convention)
- **Co-location**: Tests live next to source files for fast discovery

### Sample Test Patterns

**Convex Function Test** (convex/quotes.test.ts):

```typescript
import { convexTest } from "convex-test";
import { describe, it, expect } from "vitest";
import { api } from "./_generated/api";
import schema from "./schema";

describe("quotes.list query", () => {
  it("should return all verified quotes", async () => {
    const t = convexTest(schema);

    const personId = await t.run(async (ctx) => {
      return await ctx.db.insert("people", { name: "Albert Einstein" });
    });

    await t.run(async (ctx) => {
      await ctx.db.insert("quotes", {
        personId,
        text: "Imagination is more important than knowledge.",
        verified: true,
        createdAt: Date.now(),
      });
    });

    const quotes = await t.query(api.quotes.list, { verified: true });

    expect(quotes).toHaveLength(1);
    expect(quotes[0].verified).toBe(true);
  });
});
```

**React Component Test** (src/components/QuoteCard/QuoteCard.test.tsx):

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QuoteCard } from './QuoteCard';

describe('QuoteCard component', () => {
  const mockQuote = {
    _id: 'quote-123' as any,
    text: 'The only way to do great work is to love what you do.',
    person: { name: 'Steve Jobs' },
    verified: true,
  };

  it('should render quote text and person name', () => {
    render(<QuoteCard quote={mockQuote} />);

    expect(screen.getByText(/only way to do great work/i)).toBeInTheDocument();
    expect(screen.getByText(/Steve Jobs/i)).toBeInTheDocument();
  });

  it('should show verified badge when quote is verified', () => {
    render(<QuoteCard quote={mockQuote} />);

    expect(screen.getByLabelText(/verified quote/i)).toBeInTheDocument();
  });
});
```

**E2E Test** (tests/e2e/quoteGeneration.spec.ts):

```typescript
import { test, expect } from "@playwright/test";

test.describe("Quote Image Generation Flow", () => {
  test("should generate quote image from search to download", async ({
    page,
  }) => {
    // Given: User is on the homepage
    await page.goto("/");

    // When: User searches for a quote
    await page.getByPlaceholder("Search quotes...").fill("imagination");
    await page.getByRole("button", { name: "Search" }).click();

    // Then: Search results should appear
    await expect(
      page.getByText(/imagination is more important/i)
    ).toBeVisible();

    // When: User selects quote and generates image
    await page.getByText(/imagination is more important/i).click();
    await page
      .getByAltText(/albert einstein/i)
      .first()
      .click();
    await page.getByRole("button", { name: "Generate Image" }).click();

    // Then: Generated image should be downloadable
    await expect(page.getByRole("link", { name: "Download" })).toBeVisible();
  });
});
```

### Configuration

**vitest.config.ts**:

```typescript
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    coverage: {
      provider: "v8",
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
});
```

**playwright.config.ts**:

```typescript
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

### npm Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  }
}
```

### TDD Workflow

```bash
# Terminal 1: Watch mode for instant feedback
npm run test:watch

# Terminal 2: Development server
npm run dev

# Terminal 3: Convex backend
npx convex dev
```

---

## Links

- [Related ADR-001: Initial Tech Stack Selection](./ADR-001-initial-tech-stack.md)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [convex-test Package](https://www.npmjs.com/package/convex-test)
- [Testing Library](https://testing-library.com/)
- [Testing Standards](../../development/conventions/testing-standards.md)

---

## Notes

### Migration Path to Cucumber (If Needed)

If stakeholders appear later and require business-readable specs:

1. Install `@cucumber/cucumber`
2. Convert high-level E2E tests to Gherkin
3. Keep unit/integration tests as Vitest
4. Step definitions reference existing test helpers

Estimated effort: 1-2 weeks for ~50 scenarios

### Known Issues

**convex-test:**

- Each test gets isolated database (automatic cleanup)
- Use `convexTest(schema)` per test for isolation
- Generated types must match import paths

**Next.js App Router:**

- Server Components can't be tested with Testing Library
- Test the underlying Convex queries instead
- Client Components test normally

**Playwright:**

- Use `test.beforeEach` to reset database state
- Store auth state between tests for efficiency
- Run E2E tests sequentially in CI to avoid conflicts

### Future Considerations

**Post-MVP:**

- Visual regression testing (Playwright screenshots)
- Performance testing (Lighthouse CI)
- Contract testing (API schemas)
- Load testing (k6 or Artillery)

---

## Revision History

| Date       | Author | Description                                  |
| ---------- | ------ | -------------------------------------------- |
| 2025-10-30 | Taylor | Initial version - testing framework decision |
