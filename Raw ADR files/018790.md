# 10. Browser Testing Chat in the Widget

Date: 2019-11-14

## Attendees

- Lucas Hills
- Briana Coppard
- David Allen
- Wayne See
- Daniel Bradford
- Alex Robinson
- Levi Serebryanski
- Adrian Yong
- Kari Matthews
- Tim Patullock

## Status

Accepted

## Context

Chat is the most complicated feature in the widget, with many moving parts and edge cases that need to be accounted for.
Since chat uses websockets to send and receive information from the chat backend, the browser tests need to be able to simulate or perform
actions that would send the expected data down to the Chat Web SDK to be able to run the tests.

This ADR aims to select an appropriate method of writing browser tests that can test chat functionality in the widget.

## Possible Approaches

### 1. Exposing the Redux store globally

We can expose the redux store the widget uses when the widget detects that it's running in an E2E context, and use that
to drive the widget.

```jsx
// create the store here
if (__E2E__) {
  window.store = store
}

// inside the test
await page.evaluate(el => {
  window.store.dispatch(chatAccountSettings)
})
expect(await launcher.getLabel()).toEqual('Chat'))
```

#### Pros

##### Easy to setup

This would be trivial to setup, and we can write tests for a wide variety of scenarios.

##### Reproducible and consistent

Tests are localized and won't leak into other tests, since we don't rely on external systems.
Tests can be run consistently and should have reproducible results.

#### Cons

##### Tied to the internals of the widget

The resulting tests would be tied to the implementation details of the widget, and would need to be updated everytime we
change the internals of the widget.

##### Bypasses the Chat Web SDK entirely

This method would bypass testing Chat Web SDK, and therefore isn't representative of an end-to-end test. If the web sdk changed something that
affected the web widget, the tests wouldn't be able to catch it.

### 2. Use a custom SDK

When running browser tests, we can configure webpack to replace the node module chat-web-sdk with our own custom implementation.

#### Pros

##### Easy to setup

This would be trivial to setup, and we can write tests for a wide variety of scenarios.

##### Reproducible and consistent

Tests are localized and won't leak into other tests, since we don't rely on external systems.
Tests can be run consistently and should have reproducible results.

#### Cons

##### Web SDK would need to be reimplemented

We'd need to provide a mock implementation of the web sdk, with our own custom implementation of the firehose, setting visitor department, etc.

##### Bypasses the Chat Web SDK entirely

This method would bypass testing Chat Web SDK, and therefore isn't representative of an end-to-end test. If the web sdk changed something that
affected the web widget, the tests wouldn't be able to catch it. Any behaviours or side-effects that
the Chat Web SDK provides would either need to be reimplemented by our custom implementation, or have
other work arounds.

### 3. Setup a mock websockets server

We could setup a [websocket server](https://github.com/websockets/ws) and point the web widget to use that as the chat backend.

```jsx
import WebSocket from 'ws';

const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', ws => {
  ws.on('message', message => {
    expect(message).toEqual(expected());
    ws.send(reply());
  });

  ws.send(chatOnlinePayload());
});
```

#### Pros

##### Tests are completely isolated

Tests are completely isolated from external factors like system outages, etc. Re-running the same test multiple times should return
the same results. Tests are also isolated from each other, since "account" changes can be simulated using mocked payloads and aren't persistent across tests.

##### Tests can be run offline

No internet connection is needed to run the E2E tests, since all external communications can be mocked out.

##### Flexible enough to run multiple scenarios

We can test scenarios such as chat triggers, proactive chats, disconnection, etc. since we can simulate sending the appropriate websocket payloads.

#### Cons

##### Feasibility

As of now, we are not sure if this is possible. The Chat Web SDK would need some modifications
in order to be able to connect to a different server, and most likely other changes are needed
to make this work.

##### Hard to setup

In order to run tests, we would need to capture the expected messages by recording sessions
so that they can be replayed in the tests. We can create tooling to automate this process, but
would need to invest time to build the necessary infrastructure for this.

##### Tied to the Web SDK

We might potentially need to modify tests when things such as ODVR and Answer Bot come into
play.

### 4. Use the chat dashboard

We could use the actual chat dashboard to drive interaction with the web widget. This is similar
to how Zendesk Browser Tests currently run tests against chat in the widget, using
Selenium to simulate a user on the dashboard toggling settings on and off.

There are several advantages to writing these tests in Embeddable Framework vs keeping them in
a separate repository as it's currently done now in Zendesk Browser Tests, namely:

- Builds can be verified to pass browser tests, without the need to run a separate asynchronous
  pipeline.
- It's much easier to keep browser tests in sync with the actual code, since a pull request
  for a feature can now include both the actual implementation and the browser test for it.
- The tests would be easier to debug and maintain, since the whole engineering team
  will be responsible for the writing and maintaining the browser tests instead of it being
  the responsibility of specific individuals.

An example of how a test that uses the chat dashboard would look like when written in Puppeteer:

```jsx
// load the widget
await widgetPage.loadWithConfig('contactForm', 'zopimChat');
await wait(async () => {
  expect(await launcher.getLabelText()).toEqual('Help');
});
const chatPage = await browser.newPage();

// load the chat dashboard
await chatPage.goto('https://account.zendesk.com/chat/agent');
const frame = await chatPage.mainFrame().childFrames()[0];
const documentHandle = await frame.evaluateHandle('document');
const doc = documentHandle.asElement();

// sign into chat dashboard
const email = await queries.getByLabelText(doc, 'Email');
await email.type('email@zendesk.com');
const password = await queries.getByLabelText(doc, 'Password');
await password.type('hunter2');
const button = await queries.getByText(doc, 'Sign in');
await button.click();

// wait for interstitial to load
await wait(async () => {
  expect(await chatPage.title()).toEqual('z3n - Chat');
}, 15000);

// wait for dashboard to finish loading
await wait(async () => {
  expect(await chatPage.title()).toEqual('Dashboard - Home');
}, 15000);

// set the status to online
const chatDoc = await getDocument(chatPage);
const status = await queries.getAllByText(chatDoc, 'Invisible');
await status[0].click();
const online = await queries.getAllByText(chatDoc, 'Online');
await online[0].click();

// verify that the widget label changes to Chat
await wait(async () => {
  expect(await launcher.getLabelText()).toEqual('Chat');
});
```

#### Differences to Zendesk Browser Tests

Other than the tests existing inside the Embeddable Framework, there are several things we can change to the way
we did tests in Zendesk Browser Tests to help improve the overall experience of writing and running
browser tests:

- Do not create new accounts for the tests. One of the pain points in Zendesk Browser Tests is the account service
  going down and causing the tests to break. We should maintain a set of accounts that we use for testing and make
  sure they're not modified after creation.
- Only test against production accounts. This ensures that our tests won't break when staging goes down.
- Investigate using internal APIs for chat dashboard. Zopim automation tests use
  [some](https://github.com/zendesk/zopim-automation/blob/master/automations/clients/scribe/account.py)
  [internal APIs](https://github.com/zendesk/zopim-automation/blob/master/automations/clients/scribe/widgets.py) for updating
  account settings. We should investigate whether we can use the same APIs so that our tests will stay resilient
  against markup changes in the chat dashboard.

#### Pros

##### Comprehensive

Tests written with this approach would be the closest out of all the options to simulating
real world usage, and therefore the most comprehensive and provides the most confidence.

##### Can be extended to work with other services

We could use the same pattern for other services like Talk, and potentially Answer Bot.

#### Cons

##### Susceptible to external factors

Tests can break due to external factors such as outages or changes in the dashboard. These
tests would rely on account setup that has been done outside of the tests as well. For example,
some tests might rely on certain departments existing, but a user (or another test) could
accidentally rename the department name, thus breaking the tests that relied on those
departments existing.

##### Chat account leakages

Tests can leak into other tests. For example, if two tests are using the same account, and one
test sets prechat form on toggled on while the other one doesn't, the tests would break
depending on how they were ordered. Tests would need to be structured and ordered in a specific
way in order to lessen the risk of cross contamination.

##### Reliance on internet connection

Tests will now need an internet connection to be able to run.

## Prior Art

Zopim uses the dashboard approach as well to test regressions in the widget. A sample test
looks like this:

```python
@spec(phases=[0, 1])
@drivers('Agent', 'Visitor')
def test_offline_message(self):
  """Offline messsages are received and present in history
  """
  self.widget = self.load_widget(self.Visitor)

  self.dashboard.nav.set_status_invisible()

  name = self.generate_name()
  email = self.generate_email()
  msg = self.generate_msg()

  self.widget.initiate_chat(online=False)
  self.widget.send_offline_message(name, email, msg)

  self.dashboard.nav.select_history()
  self.dashboard.history.chat_listed(name=name, msg=msg)
```

## Decision

We will replace Chat Web SDK with our own module when running end-to-end tests. This custom SDK can be programmed to return certain responses
which can enable our tests to exercise chat in the widget without requiring a connection to the chat backend.

## Consequences

Since the Chat Web SDK will be mocked/replaced, there will be a trade-off in that certain things involving the SDK won't be properly tested.
For example, if we upgrade the SDK and it is throwing an exception on a certain command, this won't be caught in browser tests.
