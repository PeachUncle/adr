# ADR-0035: Performance testing scope

## Status

Accepted

Date of decision: 2026-01-09

## Context and Problem Statement

What types of performance tests are in scope for our performance testing e.g. stress tests, spike tests etc

### Terminology

For the purposes of this ADR, we define the following types of tests:

- basic tests (sometimes confusing referred to as just 'performance tests') - testing individual actions/requests are performant independent
  of the wider load on the system
- load tests - simulating our predicted 'normal' usage of the system, and ensuring actions/requests are performant under that load
- stress tests - simulating our predicted 'high' usage of the system, and ensuring actions/requests are performant under that load
- spike tests - simulating sudden spikes in usage, and ensuring the system can handle them without significant degradation of performance
- soak tests - simulating sustained 'normal' usage over a long period of time, ensuring the system can handle it without degradation of
  performance
  In all cases, the tests would measure maximum response times, average response times, and error rates against defined thresholds, and
  would only pass if those thresholds are met.
- breaking point tests - gradually increasing load until the system breaks, to determine its maximum capacity

## Considered Options

* Full suite of tests: basic, load, spike, soak, stress, breaking point
* Full suite minus breaking point tests
* Basic tests, load, and spike tests
* Basic tests and load tests only

## Decision Outcome

Basic tests, average use tests, and spike tests, as this ensures that we have a good understanding of the performance of the system under
expected and
high loads, as well as its ability to handle sudden spikes, without the complexity and cost of breaking point tests or endurance tests.

This should be coupled with monitoring in production for performance degredation over time and automations to restart services if
performance
degrades beyond acceptable levels.

If we wish to observe the failure mode of the system under extreme loads we can consider running breaking point tests as a one-off in the
future.

## Pros and Cons of the Options

### Full suite of  tests

The most comprehensive suite of tests, covering everything up to and including stress tests in order to
know exactly how much performance headroom we have and what impact changes have on that headroom.

* Good, because it gives us a baseline of performance for each type of action.
* Good, because it benchmarks the performance we'd expect to see during normal usage to check that it's acceptable.
* Good, because it tests that the service can handle sustained higher-than-expected loads.
* Good, because it tests that the service can gracefully withstand sudden spikes in load followed by rapid ramp-downs as might happen on
  registration deadlines.
* Good, because it tests the endurance of the service over a long period of time.
* Good, because it lets us test under what load the service would fall over or performance would degrade, letting us calculate our headroom.
* Good, because it would allow us to run different types of tests at different frequencies or on different triggers.
* Bad, because the full suite would take a long time to run, making it less likely we'd do so very often.
* Bad, because it would be expensive to run the full suite of tests, particularly the breaking point tests.
* Bad, because we might need to give advanced notice to other MHCLG Teams e.g. Cloud Ops (and maybe AWS) before running the breaking point
  tests.

### Full suite minus breaking point tests

As above, but without the breaking point tests, on the basis that the stress test should give us a lower bound on our headroom.

* Good, because it gives us a baseline of performance for each type of action.
* Good, because it benchmarks the performance we'd expect to see during normal usage to check that it's acceptable.
* Good, because it tests that the service can handle sustained higher-than-expected loads.
* Good, because it tests that the service can gracefully withstand sudden spikes in load followed by rapid ramp-downs as might happen on
  registration deadlines.
* Good, because it tests the endurance of the service over a long period of time.
* Good, because it avoids the most expensive type of tests.
* Good, because it would allow us to run different types of tests at different frequencies or on different triggers.
* Bad, because the endurance focused tests like the soak test would still take a long time to run, making it less likely we'd do so very
  often.
* Bad, because it would still be quite expensive to run this collection of tests, although not as expensive as the breaking point tests.
* Bad, because we would not have tested what the failure mode of the service is under unexpectedly large loads such as during a DDoS attack.

### Basic tests, average use tests, and spike tests

A reduced suite of tests focusing on the most likely scenarios - normal usage and sudden spikes in load.

* Good, because it gives us a baseline of performance for each type of action.
* Good, because it benchmarks the performance we'd expect to see during normal usage to check that it's acceptable.
* Good, because it tests that the service can gracefully withstand sudden spikes in load followed by rapid ramp-downs as might happen on
  registration deadlines.
* Good, because it only includes the types of tests that run relatively quickly and cheaply.
* Bad, because we would not have tested what the failure mode of the service is under unexpectedly large loads such as during a DDoS attack.
* Bad, because we would not have tested that the service can handle sustained higher-than-expected loads.
* Bad, because we would not have tested that no issues occur under sustained load, e.g. memory leaks.

### Basic tests and average use tests only

The minimal suite of tests focusing on ensuring that the service performs well under expected usage.

* Good, because it gives us a baseline of performance for each type of action.
* Good, because it benchmarks the performance we'd expect to see during normal usage to check that it's acceptable.
* Good, because it only includes the types of tests that run relatively quickly and cheaply.
* Bad, because we would not have tested what the failure mode of the service is under unexpectedly large loads such as during a DDoS attack.
* Bad, because we would not have tested that the service can handle sustained higher-than-expected loads.
* Bad, because we would not have tested that no issues occur under sustained load, e.g. memory leaks.
* Bad, because we would not have tested that the service can gracefully withstand sudden spikes in load followed by rapid ramp-downs as
  might happen on registration deadlines.



