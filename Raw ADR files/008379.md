---
# These are optional metadata elements. Feel free to remove any of them.
status: accepted
date: 06/06/2025
decision-makers: Katy, Pranay, Zhenyu
consulted: course documents, [Playwright documentation](https://playwright.dev/docs/intro) 
informed: the team as a whole was informed and asked about different browsers (Chromium, Firefox, webkit)
---

# Using Playwright for Cross-Browser Testing

## Context and Problem Statement

Though we designed our end-to-end tests with `Puppeteer` based on one of the labs we did with the course, `Puppeteer` really only does its tests on the Chromium browser. For this reason, decided to use `Playwright` to make sure that our site loads correctly across multiple browsers, mainly Chromium, Firefox, and webkit. 

## Considered Options

* Playwright
* BrowserStack
* Browserling
* LambdaTest

## Decision Outcome

Chosen option: "Playwright", because of its simplicity of use, connection to course materials, auto-wait, and quick setup. It was very simple to integrate into our workflow using `npx`. 

### Consequences

* Good, because it's cross-browser supporting Chromium, Firefox, and webkit and one API.
* Good, because it's headless by default, which is less infrastructure load. For debugging, it can be set to not be headless.
* Good, because it offers simple checks and functions: `isVisible`, `click`, etc.
* Good, because it supports built-in tracing, screenshots, and video recordings. When a test fails, you can look at the results and see an actual video of the test, which is very helpful.
* Good, because of the ability to view results in a clean, informative format on localhost.
* Bad, because it's relatively new so there's less of an established ecosystem.
* Bad, because there are known issues with webkit.
* Bad, because test writing requires code.

## Reasons we did not go with the other options:
- BrowserStack, LambdaTest, and Browsering are commercial services with usage-based pricing, which isn't sustainable for our project.
- BrowserStack and LambdaTest are mostly built for manual testing/visual inspection. We wanted scripted, automated test suites to run our tests.
- Playwright integrates smoothly with our CICD pipeline because it runs locally, and it would be more complicated to set up with these other services. 
