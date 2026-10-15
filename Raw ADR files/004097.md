# ADR: Extract the Reporting System

## Status

PROPOSED

## Context

Managers request and receive various operational and analytical reports,
including financial reports, expert performance reports, and ticketing
reports.

Due to reliability issues, the monolithic system frequently “freezes up” or
crashes. We think it’s mostly due to spikes in usage, and the number of
customers using the system.

Change is difficult and risky in this large monolith - whenever a change is
made, it takes too long and something else usually breaks.

To tackle both issues, we decided to first extract self-containing components
from the main system and enable asynchronous handling of tasks where possible.

As a first step, we will start with components which appear to be easy to isolate
and promise potential for significant savings of system resources.

## Decision

We decided to decouple the report generation processes from the main system.

The decoupling will happen via the following changes:

1. Dedicate a swarm of read-only replicas of our main database to reporting.
2. Configure our reporting tools to use the new replicas only.
3. Bring up a swarm of new pods for our monolith to easily handle the reporting
needs of our application.
4. Configure our load balancer to route all reporting requests to only hit our
replica servers.
5. Change our scheduled reporting tasks (e.g. cronjobs) to use our new pods
exclusively.
6. Introduce a queue based delivery of reporting tasks, along with an
at-least-once delivery of such tasks.
7. Refactor any existing code which triggers reporting processes to use the new
reporting queues to initiate their tasks.

## Consequences

1. Load on our system during report generation drops without much development
effort.
2. Scalable reporting which can be adjusted to our budget and priorities. (In
case of budget limitations, we can also introduce queues based on priorities.)
3. Further refactoring, or complete rewriting of the reporting module is now 
easier.
4. When components which write to our database are refactored, the reporting
module will need to change to collect the necessary data needed for reporting,
meaning additional complexity.
5. When email sending changes in our system, the reporting sub-system will need
to be updated as well, meaning additional complexity.
