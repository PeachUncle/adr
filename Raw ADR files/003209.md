# ADR 016: Choice of E2E Testing Architecture - Page Object Model (POM)

## Status
Accepted

## Context
The PlumbingPOC project required a robust, maintainable E2E testing strategy using Playwright. Initial test implementations used utility functions in separate files (like `auth.ts` and `quoteHelpers.ts`), but this approach led to:

- **Tight coupling** between tests and implementation details
- **Maintenance burden** when UI changes occurred
- **Code duplication** across test files
- **Poor readability** with DOM selectors scattered throughout tests
- **Brittle tests** that broke with minor UI changes

## Decision
We will adopt the **Page Object Model (POM)** architecture exclusively for all E2E testing. All test interactions with the application will go through dedicated page objects rather than direct DOM manipulation or utility functions.

### Page Object Structure
```
tests/e2e/page-objects/
├── base/
│   └── BasePage.ts          # Common functionality for all pages
├── pages/
│   ├── AuthPage.ts          # Authentication (signInAsUserType, signOut)
│   ├── QuoteRequestPage.ts  # Quote creation (createQuoteRequest)
│   ├── DashboardPage.ts     # Dashboard navigation
│   └── RequestDetailPage.ts # Request management
└── components/
    ├── CommandMenu.ts       # Admin command center navigation
    ├── QuoteList.ts         # Quote display/management components
    ├── RequestModal.ts      # Request detail modal components
    └── UserMenu.ts          # User menu dropdown components
```

### Building Blocks Pattern
Page objects expose **building block methods** that compose multiple low-level interactions:

```typescript
// AuthPage building blocks
await authPage.signInAsUserType('user');     // Smart login with user type detection
await authPage.signOut();                    // Robust logout

// QuoteRequestPage building blocks
const requestId = await quoteRequestPage.createQuoteRequest('perimeter_drains');

// DashboardPage building blocks
await dashboardPage.findAndOpenRequest(requestId, 'admin');
await dashboardPage.createQuote(description, price);
```

## Consequences

### Positive
- **🔧 Maintainability**: UI changes only require updates in one place per page
- **♻️ Reusability**: Page methods can be used across multiple tests
- **📖 Readability**: Tests read like high-level user actions
- **🛡️ Encapsulation**: Implementation details are hidden from tests
- **🧪 Testability**: Easy to mock or stub page interactions
- **📚 Documentation**: Page objects serve as living documentation of the UI

### Negative
- **⏱️ Initial Investment**: Higher upfront cost to create page objects
- **🏗️ Architecture Overhead**: Additional abstraction layer to maintain
- **🔄 Learning Curve**: Team needs to understand POM patterns

### Implementation Details

#### BasePage.ts
All page objects extend `BasePage` which provides:
- Common utilities (`waitForElement`, `fillInput`, `clickElement`)
- API response waiting (`waitForApiResponse`)
- Error handling patterns

#### Page Object Responsibilities
- **AuthPage**: Authentication flows, session management
- **QuoteRequestPage**: Quote creation with AI conversation handling
- **DashboardPage**: Navigation, filtering, request management
- **RequestDetailPage**: Quote creation, status updates

#### Test Structure
All test files follow standardized documentation:

```typescript
/**
 * [Test Suite Name] Test Suite
 *
 * This spec tests [specific functionality being tested].
 *
 * ASSUMPTIONS:
 * - [Any prerequisite tests or conditions that must be met]
 *
 * Tests Performed:
 * 1. [test name] - [brief description]
 * 2. [test name] - [brief description]
 */
```

## Alternatives Considered

### Utility Functions Approach (Rejected)
- **Pros**: Quick to implement, familiar pattern
- **Cons**: Tight coupling, maintenance burden, poor reusability
- **Decision**: Rejected due to maintenance and scalability concerns

### Direct DOM Manipulation (Rejected)
- **Pros**: Most direct approach, no abstraction overhead
- **Cons**: Brittle, unmaintainable, poor readability
- **Decision**: Rejected as it violates testing best practices

### Component-Level Testing (Deferred)
- **Pros**: Faster execution, more focused testing
- **Cons**: Doesn't cover full user journeys, misses integration issues
- **Decision**: Deferred - POM covers E2E needs, component testing can be added later

## References
- [Page Object Model - Martin Fowler](https://martinfowler.com/bliki/PageObject.html)
- [Playwright POM Best Practices](https://playwright.dev/docs/pom)
- [Test Automation Patterns](https://testautomationpatterns.org/)

## Date
2025-01-22

## Authors
PlumbingPOC Development Team
