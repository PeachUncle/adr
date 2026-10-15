# ADR.5 Cloud Deployment

This ADR proposes a deployment scheme for the Road Warrior product, taking into account the implied elasticity
requirement (which is adaptation for the varying load), as well as the desire to reduce the maintenance and support
efforts (since the project is a start-up).

## Status `APPROVED`

## Rationale

### Component Autoscaling

Based on the nature of the product we expect that load will vary over time, depending on the season, upcoming holidays,
and similar circumstances. This leads us to the idea that the system should adapt to the load within given limits
(available computing resources). Such an adaptation should not require human intervention under normal conditions, and
provide quick response to the changes in data flow density.

Auto-scaling is achievable by leveraging cloud orchestrator functionality, for example Horizontal Pod Autoscaler in
Kubernetes, that automatically creates new replicas based on resource consumption metrics of running instances.
Respectively, it can also shut down redundant instances if pressure is low. As a matter of fact, similar functionality
is provided by many cloud platforms.

### Observability

For efficient incident handling all components of the product should generate uniform logs, which are collected into
centralized logging platform, e.g., Kibana, GrayLog. Application-level logging should use tracing id with each request,
so an operator can find all the system activity related to a particular request, in the centralized log storage.

Similarly, all components should expose uniform set of metrics that allow to monitor system health using tools
like Prometheus, Grafana.

The last but not least are health check endpoints of the components allowing the orchestrator system to monitor
particular components liveness, and consequentially the overall health of the system, and raise an alert for the
support team in case if something goes wrong.

The observability features mentioned above are frequently seen as an integral part of common cloud platforms.

### CI/CD Integration

A reliable and performant CI/CD process is a crucial part of the success of a software product, since it reduces
overall time-to-market value, facilitates new versions to be released faster.

Common cloud platforms are known for their good integration with CI/CD pipelines.

## Decision

We suggest choosing one of the common cloud platforms for deployment, for example Amazon EKS, Google Kubernetes Engine, or Azure Kubernetes Service. The decision yet to made based on cost analysis, quality of customer support,
and availability of service (the latter must not be less than one required for the product).

## Consequences

Positive:

* Avoiding infrastructure support costs.

Negative:

* There is a certain overhead in terms of development of cloud-related features.