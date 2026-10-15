# ADR 02: Full Managed Serverless on a Single Cloud Provider

[<- Back](../README.md)

  “No server is easier to manage than no server”
  - @Werner, #reInvent

## Context

We want to focus on building applications without worrying about infrastructure
management.

## Decision

We will build a fully managed serverless architecture on a single cloud provider.

Serverless architecture, when integrated with a microservices structure,
presents various benefits, creating a flexible, highly scalable, and
cost-effective system that can promptly adapt to evolving business needs. With
serverless computing, there are considerable cost savings as you only pay for
the resources your code uses, negating the need to finance underused server
capacity. Its ability to auto-scale based on demand eliminates concerns over
manual server provisioning and avoids over- or under-provisioning issues. This
serverless approach accelerates the development and deployment cycles, enabling
faster time-to-market since there's no need to stress over infrastructure
management, scaling, or configuration. It simplifies your infrastructure by
removing the need to manage and maintain servers or operating systems, and
increases reliability as the infrastructure is cloud provider-managed and is
thus more resilient to failures. Lastly, serverless architectures permit
developers to concentrate more on implementing business logic in their code,
relieving them from infrastructure-related concerns.

The sub-decisions associated with this ADR include:

- We will use Amazon Web Services (AWS).

- We will use the following fully managed services:
  - S3 for static web hosting.
  - CloudFront for content delivery.
  - Route 53 for DNS management.
  - API Gateway for REST API.
  - Kinesis for event streaming.
  - Lambda for serverless functions.
  - EventBridge for event routing.
  - DynamoDB for NoSQL database.
  - Cognito for user authentication.
  - CloudWatch for logging and monitoring.
  - IAM for policy-as-code.

## Consequences

- Reduced operational overhead.
- Dependence on a single cloud provider.
- May incur extra costs depending on the cloud provider and usage.

## References

- [Serverless Microservices](https://docs.aws.amazon.com/whitepapers/latest/microservices-on-aws/serverless-microservices.html)
- [Serverless Framework](https://www.serverless.com/framework/docs/providers/aws/guide/intro)
- [Serverless Architectures](https://martinfowler.com/articles/serverless.html)
