## ADR 021: Playwright for frontend Testing

## Context
As our application grows, we need a robust testing strategy on the frontend to ensure reliability, prevent regressions, and improve developer confidence. Automated testing allows us to verify UI functionality across different browsers, devices, and environments. We require a testing framework that supports end-to-end (E2E) testing to simulate real user interactions, works well with our Next.js frontend, is easy to maintain and scale as the project evolves, has cross-browser support for compatibility testing, and provides a good developer experience with fast execution and debugging tools.  

### Options
Playwright is a modern E2E testing framework developed by Microsoft. It supports multiple browsers, including Chromium, WebKit, and Firefox, using a single API. Playwright provides automatic waiting for elements, parallel test execution, and robust debugging tools. Its ability to handle multiple browser contexts makes it a strong choice for cross-browser testing. However, since it is newer compared to other frameworks, it has a smaller community and ecosystem than alternatives like Selenium.  

Cypress is a JavaScript-based testing framework designed for modern web applications. It runs directly in the browser, offering real-time reloading and time-travel debugging. Cypress simplifies test writing and execution, making it an excellent choice for developers looking for a streamlined experience. However, it has limited cross-browser support, particularly lacking full support for Safari and Internet Explorer. Additionally, it does not support multiple tabs or browser instances natively, which can be a limitation for certain test cases.  

Selenium is one of the oldest and most widely used browser automation tools. It supports multiple programming languages, including Java, Python, and JavaScript, and works with all major browsers. Selenium has a large community and integrates well with various testing tools, making it a highly flexible solution. However, its test execution speed is slower than modern alternatives, and it requires more setup and maintenance. Selenium tests can also be flaky due to their heavy reliance on WebDriver.  

TestCafe is a Node.js-based testing framework that does not require WebDriver or browser plugins. It supports multiple browsers out of the box and provides built-in parallel execution. TestCafe is easy to set up and supports both JavaScript and TypeScript. It also directly competes with Selenium, and appears to have a much better developer experience. However, it has a much smaller community than Playwright or Selenium, and its ecosystem lacks many advanced integrations available in other frameworks.

## Decision

We will use Playwright as our primary frontend testing framework. It offers the best combination of speed, reliability, and cross-browser support while being easy to set up in a modern JavaScript environment like Next.js. Playwright provides robust debugging tools, parallel execution, and auto-waiting features, which make tests less flaky. Unlike Cypress, it fully supports Safari, Firefox, and WebKit, making it better for cross-browser testing. Compared to Selenium, it is faster and more developer-friendly, with modern APIs designed for UI testing.  

## Status

Accepted

## Consequences

Using Playwright as our frontend testing framework will improve test reliability due to its auto-waiting and parallel execution capabilities. This will help reduce flaky tests and speed up our test suite, making development more efficient. Playwright's cross-browser support ensures that our application functions correctly across different environments. The modern API and debugging tools provided by Playwright, such as Playwright Inspector, will enhance the developer experience and make diagnosing issues easier. However, since Playwright is a relatively new framework compared to Selenium, some team members may require time to familiarize themselves with its API. The learning curve should not be a major issue, as Playwright has extensive documentation and an intuitive API design.  
