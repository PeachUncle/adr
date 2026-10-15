# Automated web testing (2023)

ADR started in February 2023.

## Context and problem statement

What technical solution for end-2-end (e2e) testing on web applications to start with?

## Requirements

* Tests can be run from the command line, with no link to an external service (no SaaS)
* Test reports can be generated in HTML format
* Language must be part of: .NET, Go, TypeScript
* (Optional) Pipelines for code lifecycle & test execution are easy to make

## Considered options

* **Tools**
  * [Cucumber](https://cucumber.io/) ([GitHub org](https://github.com/cucumber))
    * [Godog](https://github.com/cucumber/godog) _official_: active development
    * [GoBDD](https://github.com/go-bdd/gobdd) _unofficial_ ([docs](https://go-bdd.github.io/gobdd/)): no release since 2021
  * [Cypress](https://www.cypress.io/) ([docs](https://docs.cypress.io/), [sources](https://github.com/cypress-io/cypress) _★ 42.6k_)
    * Guides: [Page Object Model by BrowserStack](https://www.browserstack.com/guide/cypress-page-object-model), [Cucumber](https://testersdock.com/cypress-cucumber-bdd/)
  * [Jest](https://jestjs.io/) ([docs](https://jestjs.io/docs/getting-started), [sources](https://github.com/facebook/jest) _★ 41.4k_)
  * [Playwright](https://playwright.dev/) ([docs](https://playwright.dev/docs/intro), [sources](https://github.com/microsoft/playwright) _★ 47.7k_)
    * Guides: [Page Object Models](https://playwright.dev/docs/pom), [BDD](https://dev.to/jankaritech/behavior-driven-development-bdd-using-playwright-n1o)
  * [Selenium](https://www.selenium.dev/) ([docs](https://www.selenium.dev/documentation/), [sources](https://github.com/SeleniumHQ/selenium) _★ 25.8k_)
    * [tebeka/selenium](https://github.com/tebeka/selenium): no update since 2021
    * [sourcegraph/go-selenium](https://github.com/sourcegraph/go-selenium): no update since 2017
  * [Taiko](https://taiko.dev/) ([sources](https://github.com/getgauge/taiko) _★ 3.2k_)
* **Patterns**
  * Page Object
  * BDD (Behavior-Driven Development)
    * Gherkin language

## Decision outcome

* 🟡 **Cypress** is an proven solution but there is a risk the company change its open source strategy over time (and restrict for example the featureset or license model)
* 🟠 **Jest** is very interesting for unit/integration testing, maybe not well suited for e2e testing.
* 🟢 **Playwright** has a very good documentation and featureset, not linked to a company ← _we have our winner!_
* 🟠 **Selenium** has no strong drivers in Go (as of today) and doesn't have the modern features the recent technologies have
* 🔴 **Taiko** doesn't have the same audience as the other massively used tools

## Implementation examples

* [hobbyfarm/e2e-testing](https://github.com/hobbyfarm/e2e-testing)
