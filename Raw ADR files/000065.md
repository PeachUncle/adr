# ADR-017: Analytics & Reporting as its own service

## Date:
2024-09-26

## Status:
Accepted

## Context:
Analytics & Reporting is a separate service. It collects data from all over the system.

We differentiate between:
Analytics: Backend-part of data collection, aggregation and processing, such as: statistical analysis or ETL (extract, 
transform, load). Needs access to a large set of data, but not necessarily recent data. 
It tends to process data in sparse (f. ex. nightly) batch jobs.
Reporting: User-facing and human-readable presentation of data.

Goal: Separation of concerns between operational (Reporting) and Analytics processes. 
No process that interacts with the user in a time critical manner should depend on analytics.

Conflicting goal: Easier to have Analytics & Reporting in the same service, for cost and complexity reasons.
Less configuration needed.

We resolve this conflict by leveraging reporting channels of communication independent of UI, for example: 
Email.
If in the future, requirements of reporting in our own UI arises, the Reporting part of this service needs to be 
split and enter the operational realm of our system.

To mitigate the risk of strong coupling inside Analytics & Reporting service,
we use clean/hexagonal Architecture principles including encapsulation of Use-Cases, 
allowing for cheaper technological transitions and split between Reporting and Analytics.

## Decision:

- One service for both Analytics and Reporting
- No operational time-critical process should depend on this service, instead, it should only be needed to collect
data from other systems and generate reports.
- The service has access to all the data needed for its purposes, therefore it connects several databases and queues.

## Consequences:

### Strengthened characteristics:
- Evolvability (additional analytics and reporting tools (f.ex. Data Warehouse) 
could be included in the service or only need access to this service)
- Cost (only one service)
- Maintainability
- Fault-tolerance

### Weakened characteristics:
- Adaptability
- Security (access to all data containers while also maintaining an external connection)
