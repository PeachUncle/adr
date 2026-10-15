# Frontend Testing Strategy

* Status: proposed
* Deciders: Platform Team, Frontend Team
* Date: 2025-12-05

## Context and Problem Statement

With our frontend stack selected (React + Vite + TanStack Router/Query per ADR-007) and component library chosen (shadcn/ui + Tailwind per ADR-008), we need a comprehensive testing strategy that covers unit tests, integration/component tests, and end-to-end tests across all frontend applications (e-commerce, POS, admin, merchandising) and the shared `libs/ui` component library.

Key questions:
1. What testing philosophy should guide our approach (traditional pyramid vs testing trophy)?
2. What tools for each testing layer?
3. How do E2E tests interact with backend services (mocked vs live)?
4. How does component development tooling integrate with testing?
5. What is the right testing approach for design system / presentation components?

## Decision Drivers

1. **Nx integration** - Tools must work with Nx affected analysis and caching
2. **Vite ecosystem alignment** - Testing tools should integrate natively with Vite
3. **Component library needs** - `libs/ui` (shadcn/ui) requires visual development and documentation
4. **Cross-browser requirements** - E-commerce needs true cross-browser testing (including Safari)
5. **CI/CD efficiency** - Tests must be fast and parallelizable
6. **Developer experience** - Fast feedback loops, good debugging tools
7. **Performance** - Minimize tool overhead; prefer lightweight solutions

## Testing Philosophy: Testing Trophy

We adopt Kent C. Dodds' **Testing Trophy** model over the traditional testing pyramid:

```
      ┌─────────┐
      │   E2E   │  ← Critical user flows only (10%)
      ├─────────┤
      │         │
      │ Integr- │  ← Component tests with RTL (60%)
      │  ation  │     Most confidence per dollar
      │         │
      ├─────────┤
      │  Unit   │  ← Pure logic, utilities (20%)
      ├─────────┤
      │ Static  │  ← TypeScript, ESLint (10%)
      └─────────┘
```

**Rationale**: For modern frontend applications, integration tests (testing components as users interact with them) provide the best balance of confidence, speed, and maintenance cost. Pure unit tests are reserved for complex business logic; E2E tests cover only critical user journeys.

## Component Testing Philosophy

### Design System & Presentation Components

For **dumb/presentation components** in `libs/ui` (buttons, inputs, cards, modals, etc.):

| Testing Approach | Recommendation |
|------------------|----------------|
| **Ladle stories** | Primary - visual verification, variant documentation |
| **Unit tests** | Generally NOT needed - props in, render out is self-evident |
| **Accessibility tests** | Required - axe-core validation in Vitest |
| **E2E tests** | Never - test at feature/page level instead |

**Why unit tests are typically unnecessary for presentation components:**

1. **Props → Render is trivial**: Testing that `<Button variant="primary">` renders a primary button adds no confidence
2. **Ladle provides visual verification**: Developers see all variants; visual regression catches styling issues
3. **TypeScript catches prop errors**: Type checking eliminates most bugs these tests would catch
4. **Maintenance burden**: Unit tests for presentation components break on every refactor with little value

**When to add unit tests for UI components:**

- Complex conditional rendering logic
- Computed accessibility attributes (ARIA)
- Event handler logic (form validation, state transitions)
- Animation or transition timing logic

### Smart/Container Components & Features

For **feature components** in apps (ProductDetail, Checkout, CartSummary):

| Testing Approach | Recommendation |
|------------------|----------------|
| **Vitest + RTL** | Primary - test user interactions and data display |
| **Ladle stories** | Optional - useful for complex states |
| **E2E tests** | Critical paths only - full user journeys |

### E2E Test Scope

E2E tests should focus on **high-level user journeys**, not component behavior:

**Good E2E test scope:**
- Complete checkout flow (cart → shipping → payment → confirmation)
- User authentication (login → access protected route)
- Search and filter products → add to cart
- POS transaction completion

**Bad E2E test scope:**
- Button click handlers
- Form field validation messages
- Modal open/close behavior
- Component variant rendering

## Considered Options

### Component Development & Visual Testing

1. **Storybook 10** - Industry standard, extensive features, official Nx plugin
2. **Ladle** - Lightweight, Vite-native, faster (chosen)

### Unit/Integration Testing

3. **Vitest + React Testing Library** - Vite-native, Jest-compatible (chosen)
4. **Jest + React Testing Library** - Legacy, slower with Vite

### E2E Testing

5. **Playwright** - Cross-browser, native parallel, official Nx plugin (chosen)
6. **Cypress** - Excellent debugging, mature component testing, limited browser support

## Decision Outcome

### Chosen Stack

| Layer | Tool | Nx Integration | Rationale |
|-------|------|----------------|-----------|
| Static Analysis | TypeScript + ESLint | `@nx/eslint` | Foundation layer, catches issues at compile time |
| Unit/Integration | Vitest + React Testing Library | `@nx/vitest` | Vite-native, browser mode, fast |
| Component Dev | **Ladle** | Manual (`nx:run-commands`) | 6x faster startup, 28x smaller bundle |
| Accessibility | axe-core + Vitest | `@nx/vitest` | CI-enforced a11y validation |
| E2E (mocked) | Playwright | `@nx/playwright` | Cross-browser, fast, API mocking |
| E2E (live) | Playwright | `@nx/playwright` | Same tool, different config |

### Testing Layers Defined

```
┌─────────────────────────────────────────────────────────────────────┐
│                         E2E (Live Backend)                          │
│  Playwright against staging/QA environment                          │
│  Pre-deployment gate, critical user journeys only, nightly runs     │
├─────────────────────────────────────────────────────────────────────┤
│                         E2E (Mocked Backend)                        │
│  Playwright with route mocking                                      │
│  PR builds, fast feedback, user flow validation                     │
├─────────────────────────────────────────────────────────────────────┤
│                      Component/Integration Tests                     │
│  Vitest + React Testing Library                                     │
│  Feature components, data display, user interactions                │
├─────────────────────────────────────────────────────────────────────┤
│                    Ladle Stories (libs/ui)                          │
│  Visual development, variant documentation, design review           │
│  Primary testing for presentation components                        │
├─────────────────────────────────────────────────────────────────────┤
│                      Accessibility Tests                             │
│  axe-core in Vitest - validates WCAG compliance                     │
│  Required for all libs/ui components                                │
├─────────────────────────────────────────────────────────────────────┤
│                           Unit Tests                                 │
│  Vitest for pure functions, utilities, hooks, complex logic         │
│  NOT for simple presentation components                             │
├─────────────────────────────────────────────────────────────────────┤
│                         Static Analysis                              │
│  TypeScript strict mode, ESLint, pre-commit hooks                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Deep Dive: Tool Choices

### Ladle vs Storybook

| Factor | Storybook 10 | Ladle |
|--------|--------------|-------|
| **Cold start** | 8s | **1.2s** |
| **Hot reload** | 2s | **<500ms** |
| **Bundle size** | ~7MB | **~250KB** (28x smaller) |
| **Nx plugin** | `@nx/storybook` (official) | Manual (5 min setup) |
| **Addons** | Extensive ecosystem | Minimal |
| **A11y testing** | Storybook addon | **axe-core in Vitest** (better) |

**Decision: Ladle**

Rationale:
- **Performance**: 6x faster startup, instant hot reload - critical for component development flow
- **Simplicity**: Single dependency, zero config, Vite-native
- **A11y testing is better in Vitest**: Storybook's a11y addon only runs when viewing stories; axe-core in Vitest runs in CI and catches regressions automatically
- **Nx integration works**: Manual setup with `nx:run-commands` provides caching and affected analysis
- **Uber validated**: 335 projects, 15,896 stories - 99% of Storybook stories migrated without changes

### Ladle Nx Integration

```json
// libs/ui/project.json
{
  "targets": {
    "ladle": {
      "executor": "nx:run-commands",
      "options": {
        "command": "ladle serve --port 61000",
        "cwd": "{projectRoot}"
      }
    },
    "ladle-build": {
      "executor": "nx:run-commands",
      "cache": true,
      "inputs": [
        "default",
        "^production",
        "{projectRoot}/src/**/*.stories.{js,jsx,ts,tsx}",
        "{projectRoot}/.ladle/**/*"
      ],
      "outputs": ["{projectRoot}/build"],
      "options": {
        "command": "ladle build",
        "cwd": "{projectRoot}"
      }
    }
  }
}
```

### Playwright vs Cypress

| Factor | Playwright | Cypress |
|--------|-----------|---------|
| **Browser support** | Chromium, WebKit, Firefox | Chrome, Edge, Firefox (no Safari) |
| **Parallel execution** | Native, free | Requires Dashboard (paid) |
| **Component testing** | Experimental | Mature |
| **Nx plugin** | `@nx/playwright` (official) | `@nx/cypress` (official) |
| **CI/CD scaling** | Excellent | Requires additional services |

**Decision: Playwright**

Rationale:
- **Cross-browser essential**: E-commerce requires Safari testing; Playwright is the only option with true WebKit support
- **CI/CD efficiency**: Native parallel execution without paid services
- **API mocking**: Built-in `route.fulfill()` for mocking backend responses
- **Single tool**: Same framework for mocked and live E2E tests

## Testing Examples

### Ladle Story (Presentation Component)

```typescript
// libs/ui/src/button/button.stories.tsx
import type { Story } from "@ladle/react";
import { Button } from "./button";

// No unit tests needed - Ladle stories document and verify all variants

export const Primary: Story = () => (
  <Button variant="primary">Primary Button</Button>
);

export const Secondary: Story = () => (
  <Button variant="secondary">Secondary Button</Button>
);

export const Loading: Story = () => (
  <Button loading>Submitting...</Button>
);

export const Disabled: Story = () => (
  <Button disabled>Disabled</Button>
);

// All variants visible, manually verified, visually documented
```

### Accessibility Test (Required for libs/ui)

```typescript
// libs/ui/src/button/button.a11y.test.tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from './button';

expect.extend(toHaveNoViolations);

describe('Button accessibility', () => {
  it('has no violations in default state', async () => {
    const { container } = render(<Button>Click me</Button>);
    expect(await axe(container)).toHaveNoViolations();
  });

  it('has no violations when disabled', async () => {
    const { container } = render(<Button disabled>Disabled</Button>);
    expect(await axe(container)).toHaveNoViolations();
  });

  it('has no violations when loading', async () => {
    const { container } = render(<Button loading>Loading</Button>);
    expect(await axe(container)).toHaveNoViolations();
  });
});
```

### Feature Component Test (Smart Component)

```typescript
// apps/ecommerce/src/features/product/product-detail.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProductDetail } from './product-detail';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

describe('ProductDetail', () => {
  it('displays product information from API', async () => {
    const queryClient = createTestQueryClient();
    queryClient.setQueryData(['product', 'ABC123'], {
      id: 'ABC123',
      name: 'Test Product',
      price: 29.99,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <ProductDetail productId="ABC123" />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Test Product' })).toBeInTheDocument();
      expect(screen.getByText('$29.99')).toBeInTheDocument();
    });
  });

  it('adds product to cart on button click', async () => {
    const user = userEvent.setup();
    const queryClient = createTestQueryClient();
    queryClient.setQueryData(['product', 'ABC123'], {
      id: 'ABC123',
      name: 'Test Product',
      price: 29.99,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <ProductDetail productId="ABC123" />
      </QueryClientProvider>
    );

    await user.click(screen.getByRole('button', { name: /add to cart/i }));

    // Assert cart mutation was triggered
    expect(screen.getByText(/added to cart/i)).toBeInTheDocument();
  });
});
```

### E2E Test (High-Level User Journey)

```typescript
// apps/ecommerce-e2e/src/checkout.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Checkout Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses for consistent test data
    await page.route('**/api/cart/**', route => route.fulfill({
      status: 200,
      json: { items: [{ sku: 'ABC123', qty: 2, price: 29.99 }] }
    }));

    await page.route('**/api/inventory/**', route => route.fulfill({
      status: 200,
      json: { available: true, quantity: 50 }
    }));
  });

  test('completes purchase with valid payment', async ({ page }) => {
    // High-level user journey - NOT testing individual components
    await page.goto('/cart');

    await page.getByRole('button', { name: 'Proceed to Checkout' }).click();
    await expect(page).toHaveURL('/checkout/shipping');

    await page.getByLabel('Address').fill('123 Main St');
    await page.getByLabel('City').fill('New York');
    await page.getByRole('button', { name: 'Continue to Payment' }).click();

    await page.getByLabel('Card Number').fill('4111111111111111');
    await page.getByRole('button', { name: 'Place Order' }).click();

    await expect(page).toHaveURL(/\/confirmation/);
    await expect(page.getByText('Order Confirmed')).toBeVisible();
  });
});
```

## E2E Testing Strategy

### Mocked Backend (PR Builds)

```typescript
// e2e/tests/checkout.spec.ts
test.beforeEach(async ({ page }) => {
  await page.route('**/api/cart/**', route => route.fulfill({
    status: 200,
    json: { items: [{ sku: 'ABC123', qty: 2, price: 29.99 }] }
  }));
});
```

**When to use:**
- PR builds (fast feedback)
- Testing UI logic in isolation
- Parallel CI runs

### Live Backend (Pre-deployment)

```typescript
// e2e/tests/checkout-live.spec.ts
test.use({ baseURL: process.env.STAGING_URL });

test('completes real transaction in staging', async ({ page }) => {
  await page.goto('/cart');
  // Uses actual staging APIs
});
```

**When to use:**
- Pre-deployment gate
- Nightly regression runs
- API contract validation

### Playwright Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'chromium-mocked',
      use: { ...devices['Desktop Chrome'] },
      testMatch: /.*\.spec\.ts$/,
      testIgnore: /.*-live\.spec\.ts$/,
    },
    {
      name: 'chromium-live',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env.STAGING_URL,
      },
      testMatch: /.*-live\.spec\.ts$/,
    },
    {
      name: 'webkit-mocked',
      use: { ...devices['Desktop Safari'] },
      testMatch: /.*\.spec\.ts$/,
      testIgnore: /.*-live\.spec\.ts$/,
    },
  ],
});
```

## CI/CD Pipeline Integration

```yaml
# .github/workflows/frontend.yml
name: Frontend CI

on:
  pull_request:
    paths:
      - 'apps/**'
      - 'libs/ui/**'

jobs:
  static-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install
      - run: nx affected -t lint,typecheck

  unit-integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install
      - run: nx affected -t test --parallel=3

  e2e-mocked:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install
      - run: npx playwright install --with-deps
      - run: nx affected -t e2e --parallel=2

  ladle-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install
      - run: nx affected -t ladle-build

  # Nightly or pre-deployment
  e2e-live:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install
      - run: npx playwright install --with-deps
      - run: nx run-many -t e2e --projects=*-e2e --configuration=live
        env:
          STAGING_URL: ${{ secrets.STAGING_URL }}
```

## Coverage Targets

| Layer | Target | Enforcement |
|-------|--------|-------------|
| Static (TypeScript) | 100% strict | CI blocks on errors |
| Accessibility (libs/ui) | 100% components | axe-core in Vitest |
| Unit Tests | 80% for utilities/hooks | Vitest coverage report |
| Feature Component Tests | 80% for app features | Vitest coverage report |
| Ladle Stories | 100% of libs/ui components | Manual review |
| E2E (mocked) | Critical paths covered | Manual review |
| E2E (live) | Smoke tests only | Pre-deployment gate |

## Consequences

### Positive

- **Fast component development**: Ladle's 1.2s startup vs Storybook's 8s
- **Better a11y enforcement**: axe-core in CI catches regressions automatically
- **Unified tooling**: Vitest + Playwright across all apps reduces cognitive load
- **True cross-browser**: Safari testing catches iOS/macOS-specific issues
- **Minimal test maintenance**: No brittle unit tests for presentation components
- **Nx optimization**: Affected analysis and caching work with all tools

### Negative

- **No Ladle plugin**: Manual `nx:run-commands` setup (one-time 5 min effort)
- **Fewer Ladle addons**: No controls panel like Storybook (acceptable tradeoff)
- **Two E2E configs**: Mocked and live require separate maintenance
- **Learning curve**: Team must learn Vitest + Playwright

### Neutral

- **Storybook migration**: If team has Storybook experience, stories are compatible
- **Tailwind 4.x warning**: Known Ladle issue; use 4.0.6 or earlier

## Implementation Plan

1. [ ] Add `@nx/vitest` to workspace
2. [ ] Add `@nx/playwright` to workspace with mocked/live configurations
3. [ ] Configure Ladle for `libs/ui` with `nx:run-commands` targets
4. [ ] Add axe-core and configure accessibility test patterns
5. [ ] Create testing utilities library (`libs/test-utils`) with RTL + Query wrappers
6. [ ] Define E2E test patterns for each app (checkout, search, POS transaction)
7. [ ] Configure CI pipeline with parallelization and caching
8. [ ] Document testing conventions in `CONTRIBUTING.md`

## References

- ADR-007: Frontend UI Framework (React + Vite + TanStack)
- ADR-008: Component Library (shadcn/ui + Tailwind)
- [Ladle Documentation](https://ladle.dev/docs/)
- [Ladle vs Storybook Performance](https://blog.logrocket.com/ladle-storybook-performance-project-sizes/)
- [Vitest Browser Mode](https://vitest.dev/guide/browser/)
- [Playwright Test](https://playwright.dev/docs/intro)
- [Testing Trophy](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications)
- [jest-axe for Accessibility Testing](https://github.com/nickcolley/jest-axe)
- [Nx Vitest Plugin](https://nx.dev/nx-api/vitest)
- [Nx Playwright Plugin](https://nx.dev/nx-api/playwright)
