# ADR-001: High-Level Architecture for Digital Lending Platform

## Status

Accepted – reference decision for similar projects unless a specific engagement requires a different baseline.

## Context

We need an architecture that:

- Can handle transaction-heavy digital lending workloads.
- Fits in regulated banking environments.
- Can be operated by internal teams or multiple vendors over time.
- Allows incremental delivery and evolution.

The target clients typically already have:

- Legacy cores and ESBs.
- An enterprise identity provider.
- A strategic preference for AWS, Azure or GCP.

## Decision

We will implement the digital lending platform as:

1. A set of domain-aligned services deployed on a managed Kubernetes service (EKS in the AWS reference).
2. A data layer built on Aurora PostgreSQL and Redis.
3. An event and integration layer using Kafka/MSK and dedicated adapter services.
4. A DevSecOps toolchain using IaC, CI/CD pipelines and GitOps for deployments.

## Rationale

- Kubernetes via EKS gives enough control for security, networking and observability while delegating control-plane management to the cloud provider.
- Domain-aligned services map well to teams and business capabilities, simplifying ownership and change management.
- PostgreSQL is a mature, widely understood relational database that fits lending use cases.
- Kafka/MSK provides durable event streaming for decoupled processing (analytics, collections, notifications).

## Alternatives Considered

### Alternative 1: Pure Serverless

**Pros:**

- Minimal infrastructure management.
- Fine-grained scale-to-zero for sporadic workloads.

**Cons:**

- Cold-start and tail-latency concerns for interactive flows.
- Operational complexity when hundreds of functions are involved.
- Vendor-specific constructs that complicate multi-cloud or on-prem scenarios.

We still use serverless components where they make sense, but not as the entire foundation.

### Alternative 2: Monolithic Application on PaaS

**Pros:**

- Simpler model for small teams.
- Lower cognitive load for new developers.

**Cons:**

- Limited options for fine-grained scaling.
- Harder to align separate teams and vendors around one deployable artefact.
- Greater risk of big-bang changes.

A well-structured monolith can be a stepping stone for early-stage products, but our target clients usually require a more composable architecture.

## Consequences

**Positive:**

- Clear mapping from business domains to services and teams.
- Reusable platform patterns across multiple clients.
- Strong fit with modern observability and security tooling.

**Negative:**

- Higher baseline complexity compared to a simple monolith.
- Requires platform engineering experience to operate safely.

We mitigate this by:

- Keeping the number of services small initially.
- Providing platform and enablement support.
- Documenting patterns and decisions clearly so new engineers and vendors can onboard quickly.
