# ADR-0003: Use Grafana Stack for Observability

## Status

Accepted

## Context

Grafana-banana requires comprehensive observability to monitor application health, performance, and behavior in development and production. The observability solution needs to:

- Collect metrics, logs, and traces (three pillars of observability)
- Support distributed tracing across frontend and backend
- Provide real-time dashboards and visualization
- Enable alerting and anomaly detection
- Scale with application growth
- Support both .NET and Angular/browser instrumentation
- Integrate with OpenTelemetry standards
- Be cost-effective for development and production
- Have active community and support
- Support long-term data retention and analysis

## Decision

We will use the Grafana observability stack consisting of:

1. **Grafana**: Visualization and dashboarding platform
2. **Prometheus**: Metrics collection and storage
3. **Tempo**: Distributed tracing backend
4. **Loki**: Log aggregation system
5. **Promtail**: Log shipping agent
6. **OpenTelemetry**: Instrumentation standard for metrics and traces

This provides a complete, integrated observability solution that covers all three pillars: metrics, logs, and traces.

## Consequences

### Positive

1. **Unified Platform**: Single pane of glass for all observability data
2. **Open Source**: No vendor lock-in, community-driven
3. **OpenTelemetry Support**: Standards-based instrumentation
4. **Rich Visualizations**: Powerful, customizable Grafana dashboards
5. **Distributed Tracing**: Full request tracing from frontend to backend
6. **Cost Effective**: Free to self-host, predictable costs
7. **Flexible Deployment**: Can run locally, in containers, or in cloud
8. **Active Development**: Regular updates and improvements
9. **Strong Community**: Large user base and extensive documentation
10. **Integration**: Works well with .NET and Angular
11. **Alerting**: Built-in alerting capabilities
12. **Data Correlation**: Link metrics, logs, and traces
13. **PromQL**: Powerful query language for metrics
14. **LogQL**: Efficient log querying
15. **Cloud Native**: Designed for containerized environments

### Negative

1. **Operational Complexity**: Multiple services to manage
2. **Resource Usage**: Requires significant infrastructure for production
3. **Learning Curve**: Each component has its own concepts
4. **Storage Management**: Need to plan retention policies
5. **Query Language**: PromQL and LogQL require learning
6. **Configuration**: Initial setup and configuration can be complex
7. **Cardinality Issues**: High-cardinality metrics can be problematic
8. **No Built-in Profiling**: Need additional tools for code profiling

### Neutral

1. **Self-Hosted**: Requires infrastructure management (vs. SaaS)
2. **Docker Compose**: Works well for development, needs orchestration for production
3. **Prometheus Data Model**: Time-series model has specific characteristics
4. **Log Format**: Prefers structured logging

## Implementation

### Timeline
- Initial setup: Completed
- Dashboard development: Ongoing
- Production deployment: As needed

### Owner
@markcoleman

### Dependencies
- Docker and Docker Compose for local development
- Kubernetes or similar for production deployment
- OpenTelemetry SDKs for .NET and browser
- Prometheus client libraries
- Serilog for structured logging

### Architecture

```
┌─────────────┐
│   Frontend  │
│  (Angular)  │
└──────┬──────┘
       │ OTLP traces
       │ HTTP metrics
       ├─────────────────┐
       │                 │
       v                 v
┌──────────────┐   ┌─────────┐
│   Backend    │   │  Tempo  │
│   (.NET)     │   │ (Traces)│
└──────┬───────┘   └─────────┘
       │
       ├─────────────────┐
       │                 │
       v                 v
┌────────────┐    ┌──────────┐
│ Prometheus │    │   Loki   │
│ (Metrics)  │    │  (Logs)  │
└─────┬──────┘    └────┬─────┘
      │                │
      │    ┌───────────┘
      │    │
      v    v
   ┌─────────┐
   │ Grafana │
   │ (Dashb) │
   └─────────┘
```

### Configuration Highlights

1. **Prometheus**: Scrapes `/metrics` endpoint every 15 seconds
2. **Loki**: Receives logs from Promtail
3. **Tempo**: Receives OTLP traces from both frontend and backend
4. **Grafana**: Pre-provisioned dashboards and data sources

## Alternatives Considered

### Alternative 1: Elastic Stack (ELK/EFK)

**Pros:**
- Mature, well-established
- Excellent full-text search
- Rich querying with Elasticsearch
- Good for log analysis
- Large ecosystem
- Kibana for visualization

**Cons:**
- More resource-intensive
- Complex to operate
- Elasticsearch licensing changes
- Not designed primarily for metrics/traces
- Higher learning curve
- More expensive at scale

**Why Rejected:**
While the Elastic stack is powerful for logs, it's not optimized for metrics and traces. Grafana stack provides better integration between all three pillars and is more resource-efficient.

### Alternative 2: Datadog (SaaS)

**Pros:**
- Fully managed (no operational burden)
- Excellent UI/UX
- Great APM features
- Strong machine learning capabilities
- Good mobile app
- Comprehensive integrations
- Advanced alerting

**Cons:**
- Expensive (cost scales with usage)
- Vendor lock-in
- Data leaves your infrastructure
- Less flexibility
- Not suitable for on-premises requirements
- Proprietary agents

**Why Rejected:**
Cost is prohibitive for many use cases, and vendor lock-in is a concern. Self-hosted Grafana stack provides more control and predictable costs.

### Alternative 3: New Relic (SaaS)

**Pros:**
- Comprehensive APM
- Fully managed
- Good developer experience
- Real user monitoring
- Synthetic monitoring
- Good documentation

**Cons:**
- Expensive at scale
- Vendor lock-in
- Proprietary agents
- Data sovereignty concerns
- Limited customization
- Less control over retention

**Why Rejected:**
Similar to Datadog, cost and vendor lock-in are concerns. Grafana stack provides equivalent functionality with more control.

### Alternative 4: Jaeger + Prometheus + Custom Logging

**Pros:**
- Open source
- Jaeger excellent for tracing
- Prometheus industry standard
- Flexible logging options
- Cloud Native Computing Foundation projects
- Good Kubernetes integration

**Cons:**
- Need separate visualization (like Grafana anyway)
- More complex to correlate data
- Multiple UIs to manage
- Additional configuration overhead
- Less integrated experience

**Why Rejected:**
Would likely end up adding Grafana for visualization anyway, making the full Grafana stack a better integrated solution.

### Alternative 5: Azure Application Insights

**Pros:**
- Fully managed
- Good .NET integration
- Automatic instrumentation
- Reasonable cost for Azure customers
- Good correlation features
- Smart detection

**Cons:**
- Azure vendor lock-in
- Less suitable for multi-cloud
- Limited for non-Azure deployments
- Less flexible than open-source
- Query language specific to Azure
- Limited customization

**Why Rejected:**
Cloud vendor lock-in is undesirable. Grafana stack works consistently across any environment (local, cloud, on-premises).

### Alternative 6: Honeycomb (SaaS)

**Pros:**
- Excellent for high-cardinality data
- Great trace analysis
- Good for debugging
- Innovative UX
- Modern architecture
- Good observability practices

**Cons:**
- Expensive
- SaaS only
- Smaller ecosystem
- Newer company
- Less suitable for metrics
- Learning curve for unique approach

**Why Rejected:**
Cost and SaaS-only model are limitations. While innovative, Grafana stack provides more comprehensive and cost-effective solution.

## References

- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Tempo Documentation](https://grafana.com/docs/tempo/latest/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Project Observability Guide](../../observability/README.md)
- [Project Repository](https://github.com/markcoleman/Grafana-banana)

## Related ADRs

- [ADR-0001: Use .NET 9 for Backend Framework](./ADR-0001-dotnet-backend-framework.md)
- [ADR-0002: Use Angular for Frontend Framework](./ADR-0002-angular-frontend-framework.md)

## Metadata

| Field | Value |
|-------|-------|
| **Created** | 2025-10-25 |
| **Updated** | 2025-10-25 |
| **Author** | @markcoleman |
| **Reviewers** | Architecture Review Board |
| **Status** | Accepted |
| **Implementation Status** | Complete |
