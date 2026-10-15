# [ADR-INF-001] Adopt Identity-Based Security (No VPC) for Serverless Compute

## Status
Accepted

## Context
In a traditional server-based architecture, network isolation (VPC) is the primary defense boundary.
However, we are adopting a **Serverless Architecture** (ADR-0006) using fully managed services like AWS Lambda, DynamoDB, and Cognito.

Deploying these serverless resources into a VPC introduces significant challenges:
1.  **Complexity**: Requires managing subnets, NAT Gateways, and Route Tables.
2.  **Cost**: NAT Gateways incur high hourly and data processing charges.
3.  **Performance**: Potential cold start overhead (though improved in recent years) and added network hops.
4.  **Redundancy**: Most AWS managed services (DynamoDB, S3, Cognito, EventBridge) are accessed via public HTTPS endpoints protected by IAM, meaning VPC traffic often exists just to reach a public endpoint anyway.

## Related Requirements
*   Satisfies [Encryption in Transit ](../../spec/non-functional-requirements/security.md#NFR-SEC-001)
*   Satisfies [Least Privilege ](../../spec/non-functional-requirements/security.md#NFR-SEC-005)
*   Satisfies [Availability SLO ](../../spec/non-functional-requirements/availability.md#NFR-OPS-001) (Proxy for NoOps/Maintainability)

## Decision
We will **NOT** deploy Serverless Compute components (e.g., Lambda functions) into a Virtual Private Cloud (VPC).
Instead, we will adopt an **Identity-Based Security (Zero Trust)** model.

Rules:
1.  **Identity per Function**: Each Lambda function must have a dedicated IAM Execution Role with least-privilege permissions.
2.  **Encryption Everywhere**: All data in transit must be encrypted via TLS (standard for AWS APIs).
3.  **No Persistent Network**: We accept that functions run in the provider's managed network space.

## Rationale
Primary: **Operational Efficiency (NoOps)**
    Removing the VPC layer eliminates an entire class of infrastructure to manage (Subnets, NACLs, NATs). This aligns perfectly with our goal of minimizing operational overhead.

Secondary: **Cost Optimization**
    Eliminating NAT execution costs significantly reduces the "idle cost" of the platform.

## Exceptions
A VPC **MAY** be introduced in the future ONLY if:
1.  We need to access a resource that *only* resides in a VPC (e.g., RDS, ElastiCache, or an on-premise connection via VPN/DirectConnect).
2.  Compliance requirements explicitly mandate network-layer isolation for specific processing.

Currently, we use DynamoDB (HTTPS) and generic APIs, so no exception applies.

## Consequences
Positive:
- Simplified architecture diagram.
- Reduced AWS bill (No NAT Gateway).
- Reduced Terraform/CloudFormation code complexity.

Negative:
- **Security Perception**: "No VPC" can raise eyebrows with traditional security auditors. We must clearly document our reliance on IAM and Encryption as compensatory controls.
