# ADR-0037: Performance testing platform

## Status

Accepted

Date of decision: 2026-01-13

## Context and Problem Statement

Where should we run our performance tests? For the purpose of this ADR we can assume our performance tests will run in a container, or can
be containerised without too much effort.

## Considered Options

* A developer's laptop
* A standard GitHub Actions runner
* A 'large runner' on GitHub Actions
* On ECS (either in a different VPC in the same region on nft, in a different region on nft, or on one of our other environments e.g. test)
* A different cloud provider (e.g. GCP, Azure)

## Decision Outcome

A standard GitHub Actions runner in the first instance, as it should allow us to run the main sets of tests that we are interested in, does
not incur additional costs or admin, and should be quick to set up. If it proves to be underpowered for our needs, we can then consider
moving to a 'large runner' on GitHub Actions.

## Pros and Cons of the Options

### A developer's laptop

The tests would be run on a developer's own machine, either in a container or natively.

* Good, because it is easy to set up and run.
* Good, because it incurs no additional cost.
* Good, because it requires no additional time to set up vs. creating the tests themselves.
* Good, because all requests must travel over the public internet, and not from a datacenter, so we can test real-world network conditions.
* Bad, because results may vary significantly between different developers' machines.
* Bad, because external factors (e.g. the developer's Wi-Fi connection) may affect results.
* Bad, because the tests can only be run manually, so cannot be integrated into CI/CD pipelines or scheduled.

### A standard GitHub Actions runner

The tests would be run on a standard GitHub Actions runner, either in a container or natively.

* Good, because it is easy to set up and run.
* Good, because it incurs no additional cost.
* Good, because it can be integrated into CI/CD pipelines and scheduled extremely easily.
* Good, because requests would travel over the public internet, and so would be closer to real-world network conditions.
* Neutral, because we can't currently know whether the resources available on the runner will be sufficient for our tests.
* Bad, because GitHub Actions are time-limited (6 hours for public repos per job) meaning that we could not run long endurance tests.
* Bad, because we would have to find a way for the runner to bypass our IP allowlisting in order to access nft.

### A 'large runner' on GitHub Actions

The tests would be run in a 'large runner' on GitHub Actions, (still hosted by GitHub), either in a container or natively. Large runners can
have more CPU and RAM than standard runners and can be assigned a static IP address.

* Good, because it is easy to set up and run.
* Good, because it can be integrated into CI/CD pipelines and scheduled extremely easily.
* Good, because we can assign a static IP address to the runner, allowing it to be allowlisted in nft.
* Good, because we can specify more CPU and RAM than standard runners if needed.
* Good, because requests would travel over the public internet, and so would be closer to real-world network conditions.
* Bad, because it incurs additional cost.
* Bad, because GitHub Actions are time-limited (6 hours for public repos per job) meaning that we could not run long endurance tests.
* Bad, because no established approval process to be able to use large runners, so it may take time to get permission and set up billing.

### On ECS

The tests would be run on ECS, either in a different VPC in the same region on nft, in a different region on nft, or on one of our other
environments (e.g. test).

* Good, because we have full control over the environment and can configure it to have more resources as needed.
* Good, because we can run long endurance tests if needed without time limits.
* Good, because we would have a static IP and so would not need to find a way for the tests to bypass our IP allowlisting in order to access
  nft.
* Good, because we can use some of our existing terraform modules to create the infrastructure.
* Good, because we can trigger tests from our CI/CD pipelines and schedule them as needed.
* Bad, because it incurs additional cost.
* Bad, because requests __might not__ travel over the public internet (as they are going from one AWS IP address to another), so we could
  not guarantee that we're testing real world network conditions.
* Bad, because it would take time and effort to set up the infrastructure.

### A different cloud provider (e.g. GCP, Azure)

The tests would be run on a container service on a different cloud provider, e.g. GCP or Azure.

* Good, because we have full control over the environment and can configure it to have more resources as needed.
* Good, because we can run long endurance tests if needed without time limits.
* Good, because we can use a static IP and so would not need to find a way for the tests to bypass our IP allowlisting in order to access
  nft.
* Good, because we can trigger tests from our CI/CD pipelines and schedule them as needed.
* Good, because requests would travel over the public internet, and so would be closer to real-world network conditions.
* Bad, because it incurs additional cost.
* Bad, because it would take significant time and effort to set up the infrastructure.
* Bad, because we would be setting up infrastructure on a new cloud provider, which we have little experience with.
* Bad, because we would not be able to use our existing terraform modules to create the infrastructure.
* Bad, because we would need to seek approval for setting up an account with a new cloud provider which may take time.


