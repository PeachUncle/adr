[ADR-OPS-001] Deployment Strategy Implementation
==============================================

## Context and Problem Statement
We need to define a deployment strategy for the production environment that ensures system availability and allows for rapid recovery in case of failures.
The system serves critical business operations, requiring high availability during updates.

### Decision Drivers
* **Zero Downtime**: Updates must not interrupt active user sessions or API calls.
* **Rollback Speed**: Ability to instantly revert to the previous known good state.
* **Risk Mitigation**: Ability to verify changes in a production-like environment before switching traffic.
* **Complexity**: Operational complexity of the deployment pipeline.

## Considered Options
* **Rolling Deployment**: Gradually replace instances.
* **Blue-Green Deployment**: Provision parallel environment and switch traffic.
* **Canary Deployment**: Gradually shift traffic percentage.
* **Recreate**: Stop old, start new (Downtime).

## Decision Outcome
**Chosen Option**: **Blue-Green Deployment** (Serverless variant)

**Justification**:
Blue-Green deployment offers the optimal balance between safety and complexity for our Serverless architecture.
1.  **Instant Rollback**: Switching traffic back to the "Blue" (previous) version is an atomic DNS/Routing change.
2.  **Verification**: The "Green" (new) version can be fully automated E2E tested in the production environment before receiving real traffic.
3.  **Serverless Fit**: With Lambda/API Gateway, creating parallel environments (Versions/Aliases) is cheap and fast compared to VM-based replication.

### Positive Consequences
* **Safety**: Zero downtime updates guaranteed by atomic switchover.
* **Confidence**: Testing against production configuration reduces "it works on my machine" issues.
* **NoOps**: Fits natively with AWS Lambda Aliases and Weighted Traffic.

### Negative Consequences
* **Cost**: Transiently doubled resource usage (though negligible for Serverless/Scale-to-Zero).
* **Database Complexity**: Schema changes must be backward compatible to support both Blue and Green versions simultaneously.
