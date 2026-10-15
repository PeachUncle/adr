---
status: 'accepted'
date: 2024-06-27
decision-makers: voder.ai webteam
consulted: voder.ai website team
informed: voder.ai stakeholders
packages:
  - dev-config
---

# ADR 0002: Use Playwright for End-to-End Testing

## Context and Problem Statement

A CI-friendly, cross-browser end-to-end testing framework should validate critical user flows in our web application. Test coverage is limited, and manual testing slows down our delivery pipeline. We require reliable network mocking, parallel execution, and consistent behavior across Chromium, Firefox, and WebKit.

## Decision Drivers

- Integration with GitHub Actions / CI pipeline
- First-class support for multiple browsers (Chromium, Firefox, WebKit)
- Built-in network request interception and mocking API
- Parallel test execution for speed
- Active community and strong TypeScript support

## Considered Options

- **Playwright**
- **Cypress**
- **Puppeteer**

## Decision Outcome

Chosen option: "Playwright", because it provides official multi-browser support, built-in network interception and mocking, parallel execution, and an integrated test runner that satisfies all decision drivers.

### Consequences

- Good, because the solution provides reliable, cross-browser testing out of the box.
- Good, because network mocking and fixtures are first-class features.
- Bad, because there is a small learning curve for team members unfamiliar with Playwright.
- Bad, because the installation footprint is larger than some alternatives.

### Confirmation

- Add `@playwright/test` to devDependencies (`npm install -D @playwright/test`).
- Create `playwright.config.js` in the project root with appropriate projects and webServer settings.
- Verify a basic “hello world” test executes successfully against Chromium, Firefox, and WebKit locally.
- Integrate `npx playwright test --reporter=html` into the CI pipeline and confirm tests pass in GitHub Actions.

## Pros and Cons of the Options

### Playwright

- Good, because it offers official multi-browser support (Chromium, Firefox, WebKit).
- Good, because it has built-in test runner, network mocking, and parallel execution.
- Neutral, because the API is newer and may evolve.
- Bad, because the install footprint is larger and requires initial team ramp-up.

### Cypress

- Good, because it has a mature ecosystem and developer-friendly GUI.
- Bad, because it is limited to Chromium-based browsers and requires plugins for Firefox/WebKit.
- Bad, because network mocking APIs are less powerful out of the box.

### Puppeteer

- Good, because it provides strong control over Chromium and is Google-backed.
- Bad, because it lacks official Firefox/WebKit support and doesn’t include a built-in test runner.
- Bad, because parallelization and network mocking require additional libraries.

## More Information

- Playwright documentation: <https://playwright.dev/>
- Example “hello world” test in `tests/basic.spec.js`.
- CI integration snippet in `.github/workflows/ci.yml`.
