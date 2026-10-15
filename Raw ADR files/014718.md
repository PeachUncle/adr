# ADR-0038: Performance testing triggers

## Status

Accepted

Date of decision: 2026-01-13

## Context and Problem Statement

We need to decide when we should run our performance tests (and which tests to run), so that we can balance the time and money costs of
running them with the benefits of catching performance regressions early.

## Considered Options

* Run full performance tests as a post-merge (non-failing) pipeline.
* Run a subset of faster/cheaper performance tests as a post-merge (non-failing) pipeline, and full tests on a schedule (e.g., nightly or
  weekly).
* Run full performance tests on a schedule (e.g., nightly or weekly).
* Run performance tests only on demand (e.g., when a developer suspects a performance regression).

## Decision Outcome

Run full performance tests on a schedule (e.g., nightly or weekly), because it provides a good balance between cost and timely detection of
performance regressions - likely nightly to make it easier to identify if there is a single change that caused a regression or if it was an
incremental degradation over multiple changes.

## Pros and Cons of the Options

### Run full performance tests as a post-merge (non-failing) pipeline

Our full performance test suite would run on every merge to main after the code has been deployed to nft.

* Good, because performance regressions would be detected quickly after code changes are merged.
* Good, because we would be more likely to be able to determine which code changes caused any regressions.
* Bad, because running full performance tests on every merge could be time-consuming and costly.
* Bad, because we would need some sort of queuing mechanism to avoid overlapping performance test runs if merges happen in quick succession.
* Bad, because regressions might take some time to fix, masking any new issues caused by further merges in the meantime.
* Neutral, because while it might help identify the change that tipped the tests into failure, that change may not be the main cause of the
  degradation.

### Run a subset of faster/cheaper performance tests as a post-merge (non-failing) pipeline, and full tests on a schedule (e.g., nightly or weekly)

A smaller set of performance tests that are quicker and cheaper to run would be executed on every merge to main after deployment to nft.
Full performance tests would be run on a regular schedule.

* Good, because we would get quicker feedback on potential performance regressions after merges, while still running full tests
  regularly to catch any issues missed by the smaller set.
* Good, because the smaller set of tests would be less time-consuming and costly to run on every merge.
* Good, because we would be more likely to be able to determine which code changes caused any regressions detected by the smaller set of
  tests.
* Bad, because regressions might take longer to detect compared to running full tests on every merge.
* Bad, because we would still need some sort of queuing mechanism to avoid overlapping performance test runs if merges happen in quick
  succession.
* Bad, because regressions might take some time to fix, masking any new issues caused by further merges in the meantime.
* Neutral, because while it might help identify the change that tipped the tests into failure, that change may not be the main cause of the
  degradation.

### Run full performance tests on a schedule (e.g., nightly or weekly)

Full performance tests would be executed on a regular schedule. Depending on the frequency, a check could be made to see if there were any
merges since the last run to avoid unnecessary test runs.

* Good, because it would be less time-consuming and costly compared to running tests on every merge.
* Good, because we would not need to worry about overlapping test runs due to frequent merges.
* Bad, because performance regressions could go undetected for longer periods, making it harder to identify the code changes that caused
  them.
* Bad, because developers would receive feedback on performance regressions less frequently, making fixing them more disruptive.

### Run performance tests only on demand (e.g., when a developer suspects a performance regression)

Performance tests would be executed only when a developer specifically requests them.

* Good, because it would be the least time-consuming and costly option.
* Bad, because performance regressions could go undetected for long periods, making it harder to identify the code changes that caused them.
* Bad, because developers would receive feedback on performance regressions infrequently, making fixing them more disruptive.
* Bad, because it relies on developers to identify potential performance issues, which may lead to some regressions being missed.
