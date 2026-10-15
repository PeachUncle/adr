# ADR-0036: Performance testing methodology

## Status

Accepted

Date of decision: 2026-01-09

## Context and Problem Statement

There are multiple different elements of our service that we could focus on during performance testing, and different ways we could test it,
ranging from simulating real-world usage as much as possible (i.e. registering landlords and properties via the browser) to artificial
benchmarks such as simply hitting a selection of endpoints with a large volume of requests.

## Considered Options

* Playwright end-to-end tests simulating real user journeys
* API-level tests simulating real-world usage patterns
* API-level synthetic benchmarks hitting selected endpoints with high volume

## Decision Outcome

Api-level tests simulating real-world usage patterns, because they strike the best balance between realism and speed of execution. They
allow us to simulate real-world usage patterns without the overhead of browser-based tests, making them faster to run and easier to
integrate with performance testing frameworks.

## Pros and Cons of the Options

### Playwright end-to-end tests simulating real user journeys

Using Playwright browser tests to visit each page in the user journeys under test, simulating real user behaviour as closely as possible.

* Good, because it is the closest simulation of real-world usage, ensuring that the requests being made are representative of what real
  users would do.
* Neutral, because while it would allow us to reuse existing code for testing (e.g. the page-object models), it would require some
  refactoring to make them available to the performance test suite.
* Bad, because browser tests are generally slower to run than API-level tests, meaning that the overall test suite would take longer to
  complete.
* Bad, because most performance testing frameworks are designed to support API requests out of the box, and would require additional
  effort to integrate with browser-based tests.

### API-level tests simulating real-world usage patterns

Directly calling the endpoints of the service in a way that simulates real-world usage patterns, e.g. submitting GETs and POSTs
in the same way that a real user would, but without using a browser.

* Good, because it still allows us to simulate real-world usage patterns.
* Good, because it would be faster to run than browser-based tests, allowing for more frequent execution of the performance test suite.
* Good, because most performance testing frameworks are designed to support API requests out of the box, making integration easier.
* Bad, because it is not as close a simulation of real-world usage as browser-based tests, potentially missing some aspects of user
  behaviour.
* Bad, because it would require additional effort to ensure that the form submissions remain in sync with any changes to the front-end code.

### API-level synthetic benchmarks hitting selected endpoints with high volume

Directly calling selected endpoints of the service, targeting those that are most likely to be performance bottlenecks, rather than
simulating real-world user journeys.

* Good, because it allows us to focus on the most critical parts of the service that are likely to be performance bottlenecks.
* Good, because it would be the fastest to run, allowing for very frequent execution of the performance test suite.
* Good, because most performance testing frameworks are designed to support API requests out of the box, making integration easier.
* Bad, because it does not simulate real-world usage patterns, potentially missing important aspects of user behaviour.
* Bad, because if we miss critical endpoints, we may not get a complete picture of the service's performance.
* Bad, because it may lead to optimisations that improve performance for the tested endpoints, but do not translate to overall better
  performance for real users.
* Bad, because it would require additional effort to ensure that the form submissions remain in sync with any changes to the front-end code.
