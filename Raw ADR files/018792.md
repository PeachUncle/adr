# 12. Cross Browser Testing in the Widget

Date: 2020-04-02

## Attendees

- Lucas Hills
- Apoorv Kansal
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

Approved

## Context

We're currently relying on [ZBT](https://github.com/zendesk/zendesk_browser_tests)
to do cross browser testing.
One of the downsides to relying on ZBT is that it can't be included in PR builds,
which means we have to wait for the PR to be merged to master before
we can do cross browser testing.

The purpose of this ADR is to see what approaches we can take to include
cross browser tests that run as part of the pull requests.

## Possible Approaches

### 1. Run ZBT cross-browser tests on the PRs

One of the reasons ZBT tests have to run on merge is that it relies
on the Web Widget being deployed, as the tests run against staging.
As a workaround, we can piggy-back on our current Samson Review flow (which
kicks off the build process) and run tests against specific versions using
the AC version parameter.

The flow would look something like:

1. PR created
2. User comments with [Samson Review]
3. Comment triggers a build
4. Once build is done, Samson triggers Jenkins with SHA of commit
5. Jenkins runs cross-browser tests using sha sent
6. If test fails, leave a comment on the PR

#### Pros

##### Easy to implement

We've already written the ZBT tests, we just need to hook things up in Samson
and Jenkins.

##### Test is close to actual production conditions

The widget tested in ZBT uses EKR and Asset Composer, so we're indirectly
testing that the widget works with those dependencies.

#### Cons

##### Requires manual action and can be bypassed

The whole flow can only be kicked off by someone leaving a comment. Unfortunately
Samson doesn't allow stages to be kicked off by other events other than
a comment with the words Samson Review in it.

This also means that if no one leaves the magic comment, the whole flow
can be bypassed.

##### Lock-in to ZBT, Samson and Jenkins

Going with this approach means that Web Widget will be tied to ZBT, Samson and
Jenkins. If we were to migrate away from even one of these tools, this flow will
need to be modified as well.

##### Reliability issues

Tests running in Jenkins can fail to issues unrelated to the test itself.
Jenkins can fail to spin-up a node, or Sauce Labs could have connectivity issues,
for example.

### 2. Include cross browser testing inside Embeddable Framework

We could write our own cross browser tests and include them as part of CI.

As part of this ADR, a POC was made of how this approach would work.
The POC uses Selenium and Sauce Labs. Selenium is a
browser automation tool (similar to Puppeteer), and Sauce Labs is a platform
where you can run browser tests across various devices. They were chosen
because Sauce Labs is one of the approved tools in Zendesk test engineering,
and Selenium is the recommended way to integrate with it.

#### Pros

##### Part of the PR

This workflow can be integrated with CI, so we can run cross browser tests
on our PRs before it gets merged.

##### Code ownership

Similar to the ZBT tests we have migrated over to Puppeteer, having the tests
live alongside with the actual widget code gives the team greater
flexibility in adding and modifying tests.

##### Less dependencies

The tests will work even if we migrate away from Samson, or if Jenkins is down.
This also gives us the option of ditching ZBT, as cross browser testing is
one of the reasons why we haven't completely dropped it.

#### Cons

##### Another test framework to know

Unfortunately, our current browser testing framework, Puppeteer, does not (and will not)
support IE11, one of the hard-to-test devices we want to support. We will
have to use another test framework for doing cross-browser testing.

##### Complicated to setup

To be able to run the tests without deploying a build of the widget,
we'll have to run a web server and have it serve the widget assets. This server
would have to be accessible remotely, as the tests won't be run locally.

The POC does prove that it is possible with Sauce, using Sauce Connect.

##### Does not test EKR or Asset Composer

Similar to our current E2E tests, we only simulate Asset Composer and
EKR in the tests. While this works, any change we make in those dependencies
will have to be ported over to Embeddable Framework as well in order to be sure
we're testing the widget the way it's loaded in production.

##### Still susceptible to Sauce Labs connection issues

Sauce Labs connection issues can cause our CI to fail. This can possibly be worked
around by marking this test as optional/conditional (I believe this is possible
in Travis).

### 3. Keep ZBT

ZBT cross browser tests are configured to run whenever a merge is done, and since
we only deploy if all ZBT tests are green, test failures won't get into
production. Arguments for keeping the status quo are:

- If we choose to do cross browser testing ourselves, we will likely only
  be able to test the basic scenarios, i.e. will the widget load
  in this browser? Testing scenarios that require Chat or Talk agents to come online
  will take significant work. ZBT already contains helpers for these scenarios,
  so writing them in ZBT will be easier.
- Internet Explorer 11 is not long for this world. Most of the browsers are
  converging on standards and even browser engines, with IE11 being the notable
  exception. IE11 is the main source of cross browser bugs because of its need
  for polyfills, so any solution we choose will need to support it. Since the IE11
  user base is dwindling, and we have basic support for IE11 testing right now,
  is it worth adding a new test framework whose biggest use case is preventing
  IE11 bugs?

## Decision

We have decided to use the Samson Review process to kick off cross browser tests (Option 1).
Automatic post deploy (to staging) checks using ZBT will also still be run on each PR merge.
Deployers and buddies will continue to manually check Web Widget Staging Status before we deploy any new changes to production.
