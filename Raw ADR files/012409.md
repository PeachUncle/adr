# [ADR-0003] Service Mesh Implementation

## Status

Accepted

## Date

2023-06-10

## Context

As part of our MACH architecture implementation ([ADR-0001](0001-adopt-mach-architecture.md)), we need a service mesh to manage service-to-service communication within our microservices architecture. While the API Gateway ([ADR-0002](0002-api-gateway-selection.md)) handles external traffic, a service mesh is needed to manage internal communication between services.

A service mesh provides:
- Service discovery
- Load balancing
- Traffic management
- Circuit breaking
- Mutual TLS (mTLS) encryption
- Observability (metrics, logs, traces)
- Resilience features (retries, timeouts, circuit breakers)

We need to select a service mesh solution that integrates well with our Kubernetes infrastructure and complements our API Gateway choice.

## Decision

We will implement **Kuma Service Mesh** as our service mesh solution.

Kuma will be deployed in Kubernetes using the official Helm chart, with the following configuration:

- Deployed in the `api-gateway` namespace alongside Kong
- Configured in "standalone" mode for our single Kubernetes cluster
- Integrated with Prometheus for metrics collection
- Configured with mutual TLS (mTLS) for secure service-to-service communication
- Set up with appropriate traffic policies for resilience

## Consequences

### Positive

- **Kong Integration**: Kuma is developed by Kong Inc. and has excellent integration with Kong API Gateway.
- **Simplicity**: Kuma is designed to be simpler to operate compared to alternatives like Istio.
- **Multi-platform**: Kuma supports both Kubernetes and VMs, which may be useful for hybrid deployments.
- **Security**: Built-in mTLS provides secure service-to-service communication.
- **Observability**: Kuma provides detailed metrics, logs, and traces for monitoring and troubleshooting.
- **Traffic Control**: Kuma offers traffic routing, splitting, and fault injection capabilities.
- **Envoy-based**: Kuma uses Envoy proxy, which is a battle-tested data plane.

### Negative

- **Resource Usage**: Adding a service mesh increases resource usage due to the sidecar proxies.
- **Complexity**: Despite being simpler than some alternatives, a service mesh still adds complexity to the system.
- **Learning Curve**: Team members need to learn service mesh concepts and Kuma-specific configuration.
- **Debugging Challenges**: Debugging issues in a service mesh can be more complex due to the additional network hop.

## Alternatives Considered

### Istio

**Pros**:
- Most feature-rich service mesh
- Large community and ecosystem
- Strong security features
- Comprehensive traffic management
- Good observability integration

**Cons**:
- High complexity
- Steep learning curve
- Higher resource usage
- Can be challenging to operate and troubleshoot

This option was rejected due to concerns about complexity and resource usage, especially for our initial implementation.

### Linkerd

**Pros**:
- Lightweight and simple to use
- Low resource overhead
- Good performance
- Focused on Kubernetes
- Easy installation

**Cons**:
- Fewer features compared to Istio and Kuma
- Less flexibility for complex use cases
- Limited multi-platform support
- Smaller ecosystem

This option was considered but rejected in favor of Kuma due to Kuma's better integration with Kong API Gateway.

### AWS App Mesh

**Pros**:
- Tight integration with AWS services
- Managed control plane
- Good observability with AWS X-Ray
- Relatively simple to use

**Cons**:
- Vendor lock-in to AWS
- Limited features compared to other options
- Less community support
- Not suitable for multi-cloud or hybrid deployments

This option was rejected due to concerns about vendor lock-in and our desire for a cloud-agnostic solution.

### No Service Mesh

**Pros**:
- Simplicity
- Lower resource usage
- Fewer moving parts
- Easier debugging

**Cons**:
- No built-in service-to-service security
- Limited observability for service-to-service communication
- No centralized traffic management
- Each service needs to implement resilience patterns

This option was rejected because the benefits of a service mesh outweigh the added complexity for our microservices architecture.

## References

- [Kuma Service Mesh Documentation](https://kuma.io/docs/)
- [Kuma and Kong Integration](https://konghq.com/blog/kuma-service-mesh-kong-api-gateway)
- [Service Mesh Interface (SMI)](https://smi-spec.io/)
- [CNCF Service Mesh Landscape](https://landscape.cncf.io/card-mode?category=service-mesh)
- [Service Mesh Comparison](https://servicemesh.es/)
