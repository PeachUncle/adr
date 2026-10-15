# E2E Testing Tool Choice

## Context and Problem Statement

End-to-End (E2E) testing is essential to make sure our online application operates as intended from the user's point of view. We require a browser automation tool that is dependable, effective, and scalable. There are options such as Puppeteer, Playwright, Cypress, and Selenium.

## Considered Options

Selenium:
- Popular due to its strong cross-browser support
- However, it is slower, more resource-intensive, and requires additional configuration for JavaScript-based programs

Cypress:
- Ideal for current JavaScript frameworks, however it is only compatible with Chrome browsers
- It is limited in flexibility for scenarios such as mobile emulation and requires its own test runner.

Playwright:
- Offers sophisticated functionality and supports multiple browsers
- However, it has a larger setup and maintenance overhead than Puppeteer

Puppeteer:
- JavaScript/Node.js Ecosystem: Interacts naturally with our JavaScript stack without the need for further settings.
- Browser Control and Headless Operation: Optimizes resource usage and expedites test execution by giving users complete control over Chromium/Chrome browsers in headless mode.
- Rich API for Modern Web:  Facilitates contemporary web features such as SPAs, dynamic content, and JavaScript interactions (such as form submissions and navigation).
- Reliability and Maintenance: Maintained by the Chrome team. It minimizes compatibility problems by staying current with the newest browser versions and web standards.

## Decision Outcome

Puppeteer is the best option and the tool we chose to use for E2E testing because of its easy interaction with our JavaScript stack, performance benefits, and powerful automation features. It's dependability, and continued support from the Chrome team guarantee that it will suit our E2E testing requirements as our project grows.

Consequences of choice:
- Writing, updating, and incorporating E2E tests into CI/CD workflows takes time.
- Prioritize testing for Chrome and Chromium at first, with the option to expand to additional browsers if necessary.
- Developers must become acquainted with Puppeteer's API and best practices.
