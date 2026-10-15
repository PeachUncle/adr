---
status: accepted
date: 2025-06-08
decision-makers: [Whole team]
consulted: [Course materials (labs), Whole team]
informed: [Whole team]
---

# Use of Puppeteer for End-to-End (E2E) Testing

## Context and Problem Statement

As part of our quality assurance workflow, we needed to validate critical user flows in our web app—such as toggling cards in and out of the deck, updating UI states, and simulating user interactions. These interactions couldn’t be sufficiently covered by unit tests alone, so we needed a framework capable of automated browser-level testing.

The question was: what tool can reliably simulate user behavior and DOM interactions in a headless or visible browser environment, while staying relatively lightweight and easy to integrate into CI?

## Decision Drivers

* Need for automated testing of real browser behavior (e2e)
* Compatibility with GitHub Actions / CI pipeline
* Minimal configuration overhead
* Good documentation and learning resources

## Considered Options

* Puppeteer
* Playwright
* Manual testing only

## Decision Outcome

Chosen option: **Puppeteer**, because it gave us full programmatic control over Chrome, was fast and easy to configure, and allowed our tests to run reliably in GitHub Actions. The APIs are simple and expressive, and the setup works well with our existing Node.js ecosystem.

### Consequences

* Good, because Puppeteer is fast, stable, and widely used in automated testing.
* Good, because it's easy to simulate complex DOM interactions programmatically.
* Good, because tests can be debugged locally with a non-headless browser if needed.
* Bad, because Puppeteer is Chrome-only (although that was acceptable for our scope).
* Neutral, because Playwright supports more browsers but comes with a slightly heavier config burden.

### Confirmation

Confirmation is achieved through automated GitHub Action workflows that run all Puppeteer tests in headless mode after each push to relevant branches. Failures in Puppeteer E2E tests fail the pipeline, ensuring stability of critical user-facing functionality.

## Pros and Cons of the Options

### Puppeteer

* Good, because it integrates well with Node.js and Jest-style assertions.
* Good, because it's well-documented and fast for CI pipelines.
* Good, because we can control the browser at a fine-grained level (e.g., clicks, waits, navigation)
* Bad, because it's limited to Chromium-based testing.

### Playwright

* Good, because it supports Chromium, Firefox, and WebKit out of the box.
* Good, because of rich tooling and debugging features.
* Bad, because it’s slightly more complex to set up and heavier on CI.
* Bad, because it was unfamiliar to most of our team.

### Manual Testing Only

* Good, because it’s fast to execute during development.
* Good, because it's flexible.
* Bad, because it’s not scalable, consistent, or automatable for regression testing.
* Bad, because it can be subjective for developers.

## More Information

* Puppeteer documentation: [https://pptr.dev](https://pptr.dev)
* Our E2E tests live in `__tests__/e2e/` and are executed via `npm run test:e2e`.
* Example test includes toggling a card’s deck status and confirming count updates.
* Headless mode is used by default in CI, with `--headed` available for debugging locally.
