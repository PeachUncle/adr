# 7. Browser Testing Framework

Date: 2019-05-28

## Attendees

- Apoorv Kansal
- Adrian Yong
- Briana Coppard
- Lucas Hills
- Adrian Evans
- David Allen
- Wayne See
- Levi Serebryanski
- Timothy Patullock
- Nick Dawbarn
- Daniel Bradford
- Stefan Vizzari

## Status

In Progress

## Context

In light of the recent [API infinite loop bug](https://zendesk.atlassian.net/wiki/spaces/ops/pages/694063407/2019-04-11+Integrated+chat+widget+causing+customer+sites+to+become+unresponsive+Non-SI), the team realised the need and importance of extensive API test coverage. It is not enough to have one simple unit test for each API. In order to gain more confidence in deploys (especially deploys related to APIs), we need to test complex API configurations. Some customers have more than 200 lines of our API code triggering off an exponential number of different workflows within the widget.

After much deliberation, the team decided it's necessary to write proper browser tests to test the full sequence of the widget initialization under a number of different API use cases. Although Jest integrations test would be easy to write and provide a decent amount of coverage, it is still difficult to completely test the full widget initialization process that includes queuing APIs on page load.

Furthermore, rather than writing more Zendesk browser tests, we have decided to move to a testing framework that can be embeded into our repository. The team prefers to write browser tests in one unified repository and our existing staging tests are very flaky due to Help Center account creation failing regularly. For that reason, we have also decided that our new browser tests will have limited dependency on external Zendesk services. The tests will depend on a shared Zendesk account but not interact with it to a large extent. In addition, putting these tests into our codebase mean that they run before merging which is beneficial as the master branch should no longer have commits merged that cause tests to fail.

As such, Apoorv Kansal and Adrian Yong investigated two popular browser testing frameworks. The libraries have been critically evaluated below.

## Potential Solutions

### Cypress

Cypress is a complete all-in-one end to end Javascript testing tool that includes a proper testing framework, assertion library, mocking capabilities and more.
It allows developers to easily write and run tests locally and on our CI providers. Some key differences Cypress has:

- Does not use Selenium.
- Developer first framework.
- Works with many tools and frameworks (eg. React, Angular, Applitools, Percy.io etc.).
- Large and evergrowing community support.
- All in one tool.
- Lightning fast tests.

Cypress code a chain of commands where each command returns a Promise-like instance. It manages a Promise chain on your behalf, with each command yielding a ‘subject’ to the next command, until the chain ends or an error is encountered. The commands are asynchronous and that commands don't do anything the moment they are invoked but rather enqueue themselves to be run later which Cypress manages.

#### Considerations for the Web Widget

##### HTTP Requests

Given that we do not want to constantly change account settings to produce different web widget configurations, we should mock the `embeddable/config` endpoint to return different enabled products, widget colours or anything else. Cypress comes with [http mocking](https://docs.cypress.io/guides/guides/network-requests.html#Testing-Strategies) out of the box.

##### API queuing

We need to test complex API use cases and this includes using the `zE(() => {})` and `$zopim(() => {})` embedded onto a html page. Since having a separate html page for each test is unmaintable and not scalable, we should inject Javascript code onto the rendered html before the page loads. Cypress has a `onBeforeLoad` [handler](https://docs.cypress.io/api/commands/visit.html#Arguments) and here, we can inject the callbacks.

##### Running APIs during runtime

Cypress provides [access](https://docs.cypress.io/api/commands/window.html#No-Args) to the window object during test execution, allowing us to call APIs during runtime.

#### General Considerations

##### Advantages

- Cypress supports making [http requests](https://docs.cypress.io/api/commands/request.html#Syntax) to backend services and mocking http requests.
- All tests run in the browser. This means there is no need for object serialization or JSON wire protocols. We will have full access to the Chrome Developer tools and have access to powerful debugging.
- Cypress supports [plugins](https://docs.cypress.io/guides/tooling/plugins-guide.html#Use-Cases) that allow us to tap in node based processes if needed.
- Chai-like testing syntax.
- Powerful development environment that makes writing and testing so easy and quick.
- Environment variable support via json files, bash statements and plugins.
- Large community support and actively developed.
- Easy to understand documentation.
- Able to integrate with Kent C Dodd's react testing library for querying and interacting with elements (see: https://github.com/testing-library/cypress-testing-library).
  Easy integration on Travis, Jenkins and local environment (requires slightly more configuration given that we do not have an asset composer iframe locally).
- Cypress has support for custom commands that can easily work with the chain of commands. For example, we can easily abstract opening the widget into a simple command to dry up the tests.
- Cypress is like jQuery. Queried elements always return a jQuery object allowing us to easily select items with a common and popular interface.
- Cypress is super simple and easy to read. Even a non-programmer can understand what is happening in the code below:

```js
it('send an API chat message', () => {
  cy.visit(`${Cypress.env('hostPage')}/live.html`);

  cy.findByText('Live chat')
    .click()
    .findByText('Start chat')
    .click();

  cy.window().then(win => {
    win.zE('webWidget', 'chat:send', "I'd like the Jambalaya, please");
  });

  cy.findByText("I'd like the Jambalaya, please").should('exist');
});
```

##### Disadvantages

- Cypress support iframes to a limited extent (https://docs.cypress.io/guides/references/known-issues.html#Iframes). Although not all features work at the moment, it is on demand feature request with (see cypress-io/cypress#136). I can see this support being added in the [future too](https://github.com/cypress-io/cypress/issues/685). We have built a [workaround solution](https://github.com/zendesk/embeddable_framework/pull/2950) that is feasible for the team.
- Given that it does not have support for iframes, certain features do not work such as snapshot traversals. This isn't a big deal as it's mainly used for local development work and it's really a nice to have feature more than a critical feature. I do not believe any browsing testing framework provides this feature.
- Only supports all Chrome flavoured browsers.
- Supports only one tab in one browser.

### Puppeteer

#### Description:

Puppeteer is a node library developed by Goolge that use the Chrome Developer tools
protocol to communicate with Chromium or Chrome to run automated browser tests in
headless mode (default). Puppeteer can be used with any javascript test runner like
Jest, Mocha and Jasmine

#### Considerations:

The same considerations as noted above for Cypress where used when choosing Puppeteer,
we looked for:

- HTTP requests mocking
- API queuing (for testing zE Settings API on page load)
- Running API commands during runtime (for testing ze Settings API commands)
- Web Sockets communication mocking/intercepting (for testing Chat, HC and Talk)
- Run end-to-end tests on Travis as part of CI build

All considerations were met during the POC exercise except for Web Sockets mocking which
is still under investigation.

#### HTTP requests mocking

Puppeteer intercepts HTTP requests and responses via a set of APIs https://pptr.dev/#?product=Puppeteer&version=v1.17.0&show=api-pagesetrequestinterceptionvalue

```
page.setRequestInterception(true);
page.on('request', request => {
  // create custom response for testing e.g. customised widget config payload
  });

or

page.on('response', response => {
  // verify response payload
});

```

We can then mock widget config response from the server which will allow us
to write tests for different widget configurations e.g. with HC only, Chat only,
HC And Chat only, etc

#### API queuing

In order to test API settings, the simplest solution is to use webpack to serve up
a set of static HTML pages with the specific API Settings and tests these static pages
via Puppeteer.

Or we could dynamically generate the html pages with Puppeteer and then run webpack
to serve up the html pages and run the tests.

#### Running API commands during runtime

Puppeteer runs commands using the evaluate method https://pptr.dev/#?product=Puppeteer&version=v1.17.0&show=api-pageevaluatepagefunction-args

e.g. `page.evaluate('ze.Hide()')`

#### Run end-to-end tests on Travis as part of CI build

We managed to use Puppeteer to run the dev server in Travis and run the end-to-end
tests on the dev server during a Travis CI build. We set up Puppeteer to start the
webpack dev server once before test execution starts and shut down the dev server when
the tests end.

Adjustments made:

- Create a new, streamlined webpack server config, just for testing
- Check in a test html file into the repo for the dev server to serve up
- Set a different port number for the dev server

Example code to start up dev server:

```
const { setup: setupDevServer } = require('jest-dev-server');

await setupDevServer({
  command: 'npm run test-e2e:server',
  launchTimeout: 50000,
  host: '0.0.0.0', // waits for the domain to be available before running tests
  port: 5000
});
```

#### Advantages:

- Supports **iFrames**.
- Tests are written in **Jest** as it uses the Jest test runner
- It uses the **Chrome Developer Tools protocol** - tests run faster than when using Selenium webdriver
- **Reliable tests** using built-in APIs that handles asynchronous "waits":
  - `page.waitForNavigation // resovles after a page navigates to another url`
  - `page.waitForSelector // resolves after a selector appears on the page`
  - `page.waitForResponse // waits for a specific URL in the response`
- **Device emulation** testing with touch support for testing different viewport sizes
- **Debugging** tests view the dev tools as you would any javascript application
- **Console log** application errors during test execution
  e.g. `page.on('console', msg => {console.log(msg)});`
- Maintained by Google with over 200 contributors

#### Disadvantages:

- Puppeteer is just an API to drive Chrome and the initial setup was a bit difficult because there is more than one way to set it up but we got there eventually.
- Need to plan and setup our own DSL to wrap around the API calls to make the commands more user friendly.

#### Puppeteer References:

- Demo of the latest features of Puppeteer (Google IO May 2019)
  https://www.youtube.com/watch?v=MbnATLCuKI4
- Puppeteer Github repo https://github.com/GoogleChrome/puppeteer/
- Puppeteer API docs https://pptr.dev

## Further Investigation

### Say no to Mocking

We have exhaustively considered all parts of the widget that could be mocked (redux store, chat web sdk, chat web socket payloads etc.) and have come to the same conclusion: it will not scale. Mocking itself introduces more maintainability issues and outweighs the benefits of reducing our dependency on external services.

If we do not mock parts of the widget, we will need to build up state by logging into Zendesk accounts and change the agent status through the UI. This is far from ideal but given the simplicity of changing agent statuses and far less boilerplate code in Puppeteer or Cypress compared to our existing browser tests, we think this is the simplest and most maintainable solution. We will create and maintain multiple shared Zendesk accounts that have different configurations enabled for different tests (eg. one account has chat badge enabled or another account has multiple talk routes). Our biggest pain point was account creation and this solution avoids account service creation completely. We want to stress that we should technically test the communication between the widget and various immediate service interfaces (eg. chat backend websocket endpoint, help center search endpoint, talk backend websocket endpoint, contact form submission endpoint) because if they fail, we fail and should not deploy at all. Hence, it makes sense to not mock out services like Talk and Chat. In the case of account service creation, the widget does not depend on account creation and hence, we do not need to test that dependency.

### Recommendation

After much investigation with Cypress, it's best to choose Puppeteer and use shared Zendesk accounts rather than mocking any software elements of the widget.

Cypress is very restrictive for our complex use case. For example, Cypress does not allow multiple tabs or disabling same origin policy to open iframes. Furthermore, we cannot access two different domains under the same test. These constraints mean that Cypress cannot accomodate the proposed solution as we cannot login into a Zendesk account and modify the agent status for either Talk or Chat. On the other hand, Puppeteer supports multiple tabs.

## Decision

The final decision is to use Puppeteer.

## Consequences of Decision

- Developers must learn how to use the Puppeteer framework.
- Developers will need to install the necessary frameworks.
- Developers will need to embed browser tests into their Pull Requests.
- Developers should be able to easily run browser tests locally.
