# 1. Kong as API Gateway

## Status

Accepted

Date: 2025-06-18

## Context

After deciding to implement an API Gateway pattern in our architecture, we need to select a specific implementation that
meets our requirements.

Our key requirements include:

- Declarative configuration capability
- Support for microservices architecture
- Built-in monitoring and observability
- Flexible plugin system
- High performance and low latency
- Native Kubernetes integration and orchestration
- Container-friendly deployment

## Decision

We will use Kong as our API Gateway solution, specifically version 3.9 running in DB-less mode with declarative
configuration. Kong stands out as a leading open-source API Gateway with a robust feature set and active
community support.

The implementation will include:

- Kong running as a Kubernetes deployment
- Kong running with docker containers for a non-production environment
- Declarative configuration using Custom Resources (CRDs)
- Core plugins limited to routing and monitoring
- Built-in Kubernetes service discovery
- Native integration with Kubernetes Ingress
- Health checking enabled
- Direct integration with our microservices

## Consequences

### Positive

- DB-less mode simplifies deployment and reduces operational overhead
- Declarative configuration enables GitOps practices
- Native integration with Kubernetes Ingress and Services
- Automatic service discovery in Kubernetes
- High performance with minimal latency impact
- Strong community support and documentation
- Built-in health checking and monitoring
- Seamless horizontal scaling in Kubernetes

### Negative

- Learning curve to team members unfamiliar with Kong
- Need to manage Kong Custom Resources in Kubernetes
- Additional Kubernetes resources to maintain
- Potential bottleneck if it is not properly scaled

### Neutral

- Need for team training on Kong configuration and management
- Regular updates are required to maintain security and features
- Configuration changes handled through Kubernetes manifests
- Separate concerns like authentication and transformation moved to dedicated services

## Implementation Notes

- Using Kong 3.9 Kubernetes deployments
- Configuration through Kubernetes CRDs
- Environment variables through ConfigMaps and Secrets
- Initial plugin: correlation-id only
- Health checks configured for Kubernetes probes
- Service discovery through Kubernetes Services

## Related Documents

- [ADR-0002: API Gateway](./../../global/0002-api-gateway.md)
- [Kong Official Documentation](https://docs.konghq.com/)
- [Kong Docker Hub](https://hub.docker.com/_/kong)
- [Kong Kubernetes Documentation](https://docs.konghq.com/kubernetes-ingress-controller/)
- [Kong Custom Resource Definitions](https://docs.konghq.com/kubernetes-ingress-controller/latest/references/custom-resources/)
- [Kubernetes Ingress Documentation](https://kubernetes.io/docs/concepts/services-networking/ingress/)

## Contributors

- Àlex Grau Roca