# ADR-010: Observability Requirements and Strategy

## Status

Accepted

## Context

We need to define our observability strategy including metrics collection, log management, distributed tracing, dashboards, and alerting. This strategy must provide visibility into our event-sourced, multi-service architecture while maintaining **portability across deployment platforms** and avoiding vendor lock-in.

Given our relatively low traffic expectations and prioritization of development ease and debugging capabilities, we focus on practical, developer-friendly solutions over enterprise-scale complexity.

## Decision

### Consolidated Observability Strategy

**Merging ADR-019 Content**: This ADR now consolidates all observability concerns from the previously separate ADR-019, creating a single comprehensive observability strategy.

### Developer-Focused Observability Framework

Our observability strategy balances **practical development needs** with **platform portability**, using OpenTelemetry as the foundation for all instrumentation while prioritizing debugging capabilities over enterprise complexity.

**Core Principle: Standards-Based Implementation with Developer Experience Focus**

- Use **OpenTelemetry** as the universal foundation for all observability
- Prioritize **debugging and development velocity** over comprehensive monitoring
- Implement **portable abstractions** that work across cloud providers
- Ensure **easy migration between platforms** (Cloudflare, AWS, Vercel, etc.)
- Maintain **vendor-agnostic configurations** to avoid lock-in

### Unified Instrumentation Strategy

**OpenTelemetry as Universal Standard:**

```typescript
// src/observability/telemetry.ts - Consolidated from ADR-019
import { NodeSDK } from '@opentelemetry/sdk-node';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

// Platform-agnostic wrapper library: @platform/observability
interface ObservabilityAdapter {
  exportMetrics(metrics: MetricData[]): Promise<void>;
  exportLogs(logs: LogData[]): Promise<void>;
  exportTraces(traces: SpanData[]): Promise<void>;
}

// Portable telemetry setup with consistent developer interface
class PortableTelemetry {
  private sdk: NodeSDK;

  constructor(private config: TelemetryConfig) {
    this.sdk = new NodeSDK({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: config.serviceName,
        [SemanticResourceAttributes.SERVICE_VERSION]: config.version,
        [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: config.environment,
      }),
      metricReader: this.createMetricReader(),
      spanProcessor: this.createSpanProcessor(),
      logRecordProcessor: this.createLogProcessor(),
    });
  }

  private createMetricReader() {
    // Can export to Prometheus, OTLP, or platform-specific endpoints
    switch (this.config.platform) {
      case 'cloudflare':
        return new CloudflareMetricsReader();
      case 'aws':
        return new AWSCloudWatchReader();
      case 'prometheus':
        return new PrometheusMetricsReader();
      default:
        return new OTLPMetricReader();
    }
  }
}

// Shared wrapper library enforcing consistency (from ADR-019)
export interface PlatformObservability {
  // Structured logging with JSON output
  log: {
    info(message: string, context?: Record<string, any>): void;
    error(message: string, error?: Error, context?: Record<string, any>): void;
    debug(message: string, context?: Record<string, any>): void;
    warn(message: string, context?: Record<string, any>): void;
  };

  // Metrics with standard interface
  metrics: {
    counter: {
      inc(name: string, value: number, tags?: Record<string, string>): void;
    };
    histogram: {
      observe(name: string, value: number, tags?: Record<string, string>): void;
    };
    gauge: {
      set(name: string, value: number, tags?: Record<string, string>): void;
    };
  };

  // Distributed tracing
  tracing: {
    startSpan(name: string, context?: SpanContext): Span;
    createTrace(correlationId?: string): TraceContext;
  };
}
```

**Q41: What metrics are most important to track? Business metrics vs technical metrics?**

**Answer: Prioritize technical metrics for debugging, with essential business metrics for product insights.**

**Technical Metrics (High Priority - Development Focus):**

- Event processing latency and queue depth
- Projection rebuild times and lag
- Database connection pool utilization
- HTTP response times (P50, P95, P99)
- Error rates by service and endpoint
- Memory usage and garbage collection metrics

**Business Metrics (Medium Priority - Product Insights):**

- User registration and activation rates
- Project creation frequency
- Contact form submissions and response rates
- Daily/monthly active users
- Feature usage patterns

**Implementation Priority:**

```typescript
// High priority metrics for development
const developmentMetrics = [
  'event.processing.latency',
  'projection.lag.seconds',
  'http.request.duration',
  'database.connection.pool.usage',
  'error.rate.by.service',
];

// Medium priority business metrics
const businessMetrics = [
  'user.registration.daily',
  'project.created.daily',
  'contact.submitted.daily',
];
```

**Q42: What log retention policies should we implement? Cost vs compliance requirements?**

**Answer: Simple, cost-effective retention with focus on debugging needs.**

**Retention Policy:**

```yaml
log_retention:
  local:
    duration: '7 days'
    level: 'debug'
    purpose: 'Development debugging'

  development:
    duration: '30 days'
    level: 'info'
    purpose: 'Integration testing and feature validation'

  production:
    duration: '90 days'
    level: 'warn'
    purpose: 'Incident investigation and audit trail'
```

**Rationale:**

- **90 days production**: Sufficient for incident investigation without excessive cost
- **No long-term compliance requirements** identified for personal portfolio platform
- **Cost optimization**: Focus on recent data for debugging over historical analytics
- **Debug level locally**: Maximum visibility during development

**Q43: How should we implement distributed tracing? Sampling strategies, trace correlation?**

**Answer: Lightweight tracing focused on debugging cross-service interactions.**

**Tracing Strategy:**

- **OpenTelemetry** with Jaeger for standardization
- **High sampling rate** in development (100%), lower in production (10%)
- **Request-based correlation** using trace IDs in logs
- **Focus on event flow** tracing for debugging event sourcing

```typescript
// Tracing configuration
const tracingConfig = {
  development: {
    samplingRate: 1.0, // Trace everything for debugging
    exportInterval: 5000, // 5 seconds
  },
  production: {
    samplingRate: 0.1, // 10% sampling for cost control
    exportInterval: 30000, // 30 seconds
  },
};

// Key spans to trace
const criticalSpans = [
  'event.published',
  'projection.updated',
  'user.authentication',
  'database.query',
  'external.api.call',
];
```

**Q44: What dashboards and alerts are needed? Developer vs ops vs business stakeholders?**

**Answer: Developer-focused dashboards with simple alerting for critical issues.**

**Dashboard Strategy:**

**Developer Dashboard (Primary Focus):**

- Real-time error rates and stack traces
- Event processing pipeline health
- Database query performance
- Response time percentiles
- Recent deployments and their impact

**Operations Dashboard (Secondary):**

- Infrastructure health (CPU, memory, connections)
- Cost tracking and resource utilization
- Security events and access patterns
- Backup and recovery status

**Business Dashboard (Minimal):**

- User growth trends
- Feature adoption rates
- Contact conversion metrics
- Performance against business KPIs

```typescript
// Dashboard configuration
interface Dashboard {
  name: string;
  audience: 'developer' | 'ops' | 'business';
  panels: string[];
  refreshInterval: string;
}

const dashboards: Dashboard[] = [
  {
    name: 'Development Health',
    audience: 'developer',
    panels: [
      'error-rates-by-service',
      'response-time-percentiles',
      'event-processing-lag',
      'recent-deployments',
      'database-slow-queries',
    ],
    refreshInterval: '30s',
  },
  {
    name: 'Infrastructure Overview',
    audience: 'ops',
    panels: [
      'resource-utilization',
      'cost-tracking',
      'security-events',
      'backup-status',
    ],
    refreshInterval: '5m',
  },
];
```

**Q45: How should we handle log aggregation across multiple services and apps?**

**Answer: Centralized structured logging with correlation for easy debugging.**

**Log Aggregation Strategy:**

- **Grafana Loki** for cost-effective log aggregation
- **Structured JSON logging** with consistent schema
- **Correlation IDs** for tracing requests across services
- **Centralized configuration** for log levels and destinations

```typescript
// Structured log format
interface LogEntry {
  timestamp: string;
  level: 'debug' | 'info' | 'warn' | 'error';
  service: string;
  traceId?: string;
  correlationId?: string;
  userId?: string;
  aggregateId?: string;
  eventType?: string;
  message: string;
  metadata?: Record<string, unknown>;
  error?: {
    name: string;
    message: string;
    stack: string;
  };
}

// Log aggregation configuration
const logAggregationConfig = {
  destinations: [
    {
      type: 'loki',
      endpoint: process.env.LOKI_ENDPOINT,
      labels: ['service', 'level', 'environment'],
    },
    {
      type: 'console',
      enabled: process.env.NODE_ENV === 'development',
      format: 'json',
    },
  ],
  correlation: {
    generateTraceId: true,
    propagateHeaders: ['x-trace-id', 'x-correlation-id'],
  },
  retention: {
    debug: '7d',
    info: '30d',
    warn: '90d',
    error: '90d',
  },
};
```

### Portability-First Observability Strategy

**Core Principle: Standards-Based Implementation**

- Use **OpenTelemetry** as the foundation for all observability
- Implement **portable abstractions** that work across cloud providers
- Ensure easy migration between platforms (Cloudflare, AWS, Vercel, etc.)
- Maintain **vendor-agnostic configurations**

### Primary Observability Architecture

**OpenTelemetry as Universal Standard:**

```typescript
// src/observability/telemetry.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

interface ObservabilityAdapter {
  exportMetrics(metrics: MetricData[]): Promise<void>;
  exportLogs(logs: LogData[]): Promise<void>;
  exportTraces(traces: SpanData[]): Promise<void>;
}

// Platform-agnostic telemetry setup
class PortableTelemetry {
  private sdk: NodeSDK;

  constructor(private config: TelemetryConfig) {
    this.sdk = new NodeSDK({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: config.serviceName,
        [SemanticResourceAttributes.SERVICE_VERSION]: config.version,
        [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: config.environment,
      }),
      metricReader: this.createMetricReader(),
      spanProcessor: this.createSpanProcessor(),
      logRecordProcessor: this.createLogProcessor(),
    });
  }

  private createMetricReader() {
    // Can export to Prometheus, OTLP, or platform-specific endpoints
    switch (this.config.platform) {
      case 'cloudflare':
        return new CloudflareMetricsReader();
      case 'aws':
        return new AWSCloudWatchReader();
      case 'prometheus':
        return new PrometheusMetricsReader();
      default:
        return new OTLPMetricReader();
    }
  }
}
```

### Platform-Agnostic Adapters

**Metrics Collection Strategy:**

```typescript
// src/observability/adapters/metrics.ts
interface MetricsAdapter {
  increment(name: string, value: number, tags: Tags): void;
  gauge(name: string, value: number, tags: Tags): void;
  histogram(name: string, value: number, tags: Tags): void;
}

// Cloudflare Workers adapter
class CloudflareMetricsAdapter implements MetricsAdapter {
  increment(name: string, value: number, tags: Tags) {
    // Use Cloudflare's analytics API
  }
}

// Prometheus adapter
class PrometheusMetricsAdapter implements MetricsAdapter {
  increment(name: string, value: number, tags: Tags) {
    // Push to Prometheus pushgateway or expose /metrics endpoint
  }
}

// AWS CloudWatch adapter
class CloudWatchMetricsAdapter implements MetricsAdapter {
  increment(name: string, value: number, tags: Tags) {
    // Send to CloudWatch metrics
  }
}

// Factory for platform detection
class MetricsAdapterFactory {
  static create(): MetricsAdapter {
    const platform = process.env.DEPLOYMENT_PLATFORM || 'auto-detect';

    switch (platform) {
      case 'cloudflare':
        return new CloudflareMetricsAdapter();
      case 'aws':
        return new CloudWatchMetricsAdapter();
      case 'prometheus':
        return new PrometheusMetricsAdapter();
      default:
        return this.autoDetect();
    }
  }
}
```

**Structured Logging with Multiple Destinations:**

```typescript
// src/observability/adapters/logging.ts
interface LogAdapter {
  log(entry: LogEntry): Promise<void>;
}

class MultiDestinationLogger implements LogAdapter {
  constructor(private adapters: LogAdapter[]) {}

  async log(entry: LogEntry): Promise<void> {
    // Send to all configured destinations
    await Promise.allSettled(this.adapters.map(adapter => adapter.log(entry)));
  }
}

// Platform-specific implementations
class CloudflareLogsAdapter implements LogAdapter {
  async log(entry: LogEntry): Promise<void> {
    console.log(JSON.stringify(entry)); // Cloudflare captures console output
  }
}

class LokiLogsAdapter implements LogAdapter {
  async log(entry: LogEntry): Promise<void> {
    // Send to Grafana Loki (works with any platform)
  }
}

class ElasticsearchLogsAdapter implements LogAdapter {
  async log(entry: LogEntry): Promise<void> {
    // Send to Elasticsearch cluster
  }
}
```

### Portable Configuration Strategy

**Environment-Based Configuration:**

```yaml
# config/observability.yml
observability:
  platform: ${DEPLOYMENT_PLATFORM:-auto-detect}

  metrics:
    exporters:
      - type: prometheus
        endpoint: ${PROMETHEUS_ENDPOINT}
        enabled: ${PROMETHEUS_ENABLED:-true}
      - type: otlp
        endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT}
        enabled: ${OTLP_ENABLED:-false}
      - type: platform-native
        enabled: ${PLATFORM_METRICS_ENABLED:-true}

  logging:
    exporters:
      - type: console
        enabled: true
      - type: loki
        endpoint: ${LOKI_ENDPOINT}
        enabled: ${LOKI_ENABLED:-false}
      - type: elasticsearch
        endpoint: ${ELASTICSEARCH_ENDPOINT}
        enabled: ${ELASTICSEARCH_ENABLED:-false}

  tracing:
    exporter: ${TRACE_EXPORTER:-jaeger}
    endpoint: ${TRACE_ENDPOINT}
    sampling_ratio: ${TRACE_SAMPLING_RATIO:-0.1}
```

### Recommended Portable Stack

**Metrics: Prometheus + Grafana**

- **Prometheus**: Industry standard, runs anywhere
- **Grafana**: Universal dashboards, supports multiple data sources
- **Deployment**: Can run on any platform, self-hosted or managed

**Logging: Grafana Loki**

- **Loki**: Prometheus-style logs, cost-effective
- **Promtail**: Log collection agent works everywhere
- **Deployment**: Self-hosted or Grafana Cloud

**Tracing: Jaeger with OpenTelemetry**

- **Jaeger**: CNCF graduated project, runs anywhere
- **OpenTelemetry**: Vendor-neutral instrumentation
- **Deployment**: Self-hosted or managed services

**Alternative: All-in-One Grafana Cloud**

- **Grafana Cloud**: Hosted metrics, logs, and traces
- **Benefits**: Fully managed, works with any deployment platform
- **Cost**: Pay-as-you-go, predictable pricing

### Implementation Architecture

```typescript
// src/observability/config.ts
interface ObservabilityConfig {
  platform: 'cloudflare' | 'aws' | 'vercel' | 'generic';
  metrics: {
    prometheus: {
      enabled: boolean;
      endpoint?: string;
    };
    grafanaCloud: {
      enabled: boolean;
      apiKey?: string;
    };
    platformNative: {
      enabled: boolean;
    };
  };
  logging: {
    loki: {
      enabled: boolean;
      endpoint?: string;
    };
    console: {
      enabled: boolean;
      level: string;
    };
  };
  tracing: {
    jaeger: {
      enabled: boolean;
      endpoint?: string;
    };
    otlp: {
      enabled: boolean;
      endpoint?: string;
    };
  };
}

// Platform detection utility
class PlatformDetector {
  static detect(): string {
    if (process.env.CF_WORKER) return 'cloudflare';
    if (process.env.AWS_LAMBDA_FUNCTION_NAME) return 'aws';
    if (process.env.VERCEL) return 'vercel';
    return 'generic';
  }
}
```

### Deployment-Specific Configurations

**Cloudflare Workers:**

```typescript
// src/observability/platforms/cloudflare.ts
export const cloudflareConfig: ObservabilityConfig = {
  platform: 'cloudflare',
  metrics: {
    prometheus: { enabled: true, endpoint: env.PROMETHEUS_GATEWAY },
    grafanaCloud: { enabled: true, apiKey: env.GRAFANA_API_KEY },
    platformNative: { enabled: true }, // Use Cloudflare Analytics
  },
  logging: {
    loki: { enabled: true, endpoint: env.LOKI_ENDPOINT },
    console: { enabled: true, level: 'info' },
  },
  tracing: {
    jaeger: { enabled: false }, // Limited in Workers
    otlp: { enabled: true, endpoint: env.OTEL_ENDPOINT },
  },
};
```

**AWS Lambda:**

```typescript
// src/observability/platforms/aws.ts
export const awsConfig: ObservabilityConfig = {
  platform: 'aws',
  metrics: {
    prometheus: { enabled: true, endpoint: env.PROMETHEUS_GATEWAY },
    grafanaCloud: { enabled: true, apiKey: env.GRAFANA_API_KEY },
    platformNative: { enabled: true }, // Use CloudWatch
  },
  logging: {
    loki: { enabled: true, endpoint: env.LOKI_ENDPOINT },
    console: { enabled: true, level: 'info' },
  },
  tracing: {
    jaeger: { enabled: true, endpoint: env.JAEGER_ENDPOINT },
    otlp: { enabled: true, endpoint: env.OTEL_ENDPOINT },
  },
};
```

**Generic/Self-Hosted:**

```typescript
// src/observability/platforms/generic.ts
export const genericConfig: ObservabilityConfig = {
  platform: 'generic',
  metrics: {
    prometheus: { enabled: true, endpoint: env.PROMETHEUS_GATEWAY },
    grafanaCloud: { enabled: false },
    platformNative: { enabled: false },
  },
  logging: {
    loki: { enabled: true, endpoint: env.LOKI_ENDPOINT },
    console: { enabled: true, level: 'debug' },
  },
  tracing: {
    jaeger: { enabled: true, endpoint: env.JAEGER_ENDPOINT },
    otlp: { enabled: false },
  },
};
```

### Alerting Strategy (Simplified for Low Traffic)

**Critical Alerts (Immediate Response):**

- Service completely down (> 2 minutes)
- Database connection failures
- Event processing stopped entirely
- Security breach indicators

**Warning Alerts (Within 1 Hour):**

- Error rate > 5% for 10 minutes
- Response time P95 > 5 seconds for 5 minutes
- Projection lag > 10 minutes
- Disk space > 80%

**Info Alerts (Daily Summary):**

- Performance trends
- Cost summaries
- Feature usage reports

```typescript
// Simplified alerting rules
const alertRules = [
  {
    name: 'Service Down',
    condition: 'up == 0',
    duration: '2m',
    severity: 'critical',
    channels: ['slack', 'email'],
  },
  {
    name: 'High Error Rate',
    condition: 'rate(http_requests_total{status=~"5.."}[5m]) > 0.05',
    duration: '10m',
    severity: 'warning',
    channels: ['slack'],
  },
  {
    name: 'Slow Response Time',
    condition: 'histogram_quantile(0.95, http_request_duration_seconds) > 5',
    duration: '5m',
    severity: 'warning',
    channels: ['slack'],
  },
];
```

## Implementation Phases

### Phase 1: Basic Observability (MVP)

- **OpenTelemetry instrumentation** with basic metrics
- **Structured logging** to Loki or console
- **Developer dashboard** in Grafana
- **Critical alerting** for service health
- **Simple tracing** for debugging

### Phase 2: Enhanced Monitoring (Growth)

- **Business metrics** and trends
- **Advanced alerting** with anomaly detection
- **Performance optimization** based on real usage
- **Cost tracking** and optimization

### Phase 3: Advanced Observability (Scale)

- **Machine learning-based** alerting
- **Advanced analytics** and forecasting
- **Business intelligence** integration
- **Real-time streaming** analytics

## Platform Migration Benefits

**Easy Migration Path:**

1. **Change configuration** to point to new platform
2. **Redeploy applications** with new environment variables
3. **Observability data** continues flowing to same destinations
4. **Dashboards and alerts** work unchanged

**Cost Optimization:**

- **Compare platforms** easily with same observability data
- **Negotiate better rates** by avoiding vendor lock-in
- **Mix platforms** for optimal cost/performance

**Risk Mitigation:**

- **No single point of failure** in tooling choices
- **Maintain operational visibility** during migrations
- **Preserve historical data** across platform changes

## Security and Compliance Considerations

**Data Sovereignty:**

- **Control data location** by choosing deployment regions
- **Compliance alignment** with industry requirements
- **Audit trail preservation** across platform migrations

**Access Control:**

- **Centralized authentication** via OIDC/SAML
- **Role-based permissions** in Grafana
- **API key management** for programmatic access

## Trade-offs Summary

**Development Experience vs. Enterprise Features:**

- Prioritizing debugging and development velocity over comprehensive monitoring
- Simple, understandable dashboards over complex analytics

**Cost vs. Insight:**

- Optimizing for low-cost solutions suitable for personal/startup scale
- Essential insights without premium enterprise tooling costs

**Simplicity vs. Completeness:**

- Focusing on actionable metrics and alerts
- Avoiding alert fatigue with targeted, meaningful notifications

## Next Steps

1. **Implement OpenTelemetry foundation** with platform adapters
2. **Set up Grafana Cloud or self-hosted Grafana** for universal dashboards
3. **Configure Prometheus metrics collection** with essential metrics
4. **Implement Loki logging** with 90-day retention
5. **Create developer-focused dashboard** with key debugging metrics
6. **Set up critical alerting** for service health

---

**This comprehensive approach provides practical observability for development and debugging while maintaining platform portability and cost-effectiveness. It consolidates all observability concerns into a single, coherent strategy that balances developer needs with operational requirements.**

## Related ADRs

### Supersedes

- **ADR-019**: Observability and Centralized Logging - Content merged into this comprehensive ADR

### Dependencies

- **Requires**: ADR-006 (Event Sourcing) - Observability must track event processing
- **Requires**: ADR-011 (Message Bus) - Monitoring Kafka streaming and event flow

### Influences

- **Influences**: ADR-008 (Infrastructure) - Deployment platform affects observability choices
- **Influences**: ADR-025 (Error Handling) - Error handling strategy affects logging and alerting
- **Influences**: ADR-024 (Performance) - Performance requirements define monitoring needs

## Edge Runtime Compatibility

### Challenge: OpenTelemetry NodeSDK Incompatibility

The OpenTelemetry NodeSDK requires Node.js-specific APIs (zlib, net, tls) that are not available in edge runtimes:
- Next.js Edge Runtime (Vercel Edge, Cloudflare Pages)
- Cloudflare Workers
- Deno Deploy
- Other V8 isolate-based runtimes

### Solution: Platform-Specific Packages with Shared Contracts

To maintain DDD bounded context consistency while addressing runtime constraints, we use separate packages with identical TypeScript interfaces:

**@platform/observability** - Full OpenTelemetry implementation
- Node.js runtime services (ECS, Lambda, traditional servers)
- Full distributed tracing with OpenTelemetry SDK
- Jaeger/OTLP trace export

**@platform/observability-edge** - Edge-compatible implementation
- Next.js Edge Runtime, Cloudflare Workers
- Structured logging with correlation IDs
- Degraded tracing (spans logged as JSON)
- Zero Node.js dependencies

### DDD Alignment

**Bounded Context Consistency:**
The Platform Monolith bounded context (Landing Page, Identity, Notifications, Service Discovery) maintains consistent observability contracts across all services, regardless of runtime environment.

```typescript
// Same interface in both packages
export interface PlatformObservability {
  log: Logger;
  metrics: Metrics;
  tracing: Tracing;
}

// Landing page (edge runtime)
import { createEdgeObservability } from '@platform/observability-edge';
const observability = createEdgeObservability(config);

// Identity service (Node.js runtime)
import { createObservability } from '@platform/observability';
const observability = createObservability(config);
```

**Why This Maintains DDD Principles:**

1. **Domain Boundaries Unchanged**: All services in Platform Monolith share the same observability domain model
2. **Consistent Contracts**: Identical TypeScript interfaces ensure predictable behavior
3. **Trace Context Propagation**: Correlation IDs flow across service boundaries
4. **Deployment Transparency**: Domain logic doesn't know or care about runtime differences

**Trade-offs:**

- **Degraded Capabilities**: Edge runtime uses correlation IDs instead of full distributed tracing spans
- **Package Duplication**: Two packages instead of one, but only at the infrastructure layer
- **Acceptable for DDD**: Technical implementation details don't violate domain boundaries

### Implementation Details

**@platform/observability-edge** provides:
- `EdgeStructuredLogger` - JSON console logging with trace context
- `EdgeMetricsCollector` - In-memory metrics with Prometheus format
- `EdgeTracingManager` - Correlation ID generation and span logging
- `CloudflareEdgeAdapter` - Adapter implementation for edge runtimes

**Configuration Example:**

```typescript
// apps/landing-page/src/lib/observability-setup.ts
import { createEdgeObservability } from '@platform/observability-edge';

export const observability = createEdgeObservability({
  serviceName: 'platform-modular-monolith',
  version: '1.0.0',
  environment: process.env.NODE_ENV || 'development',
  platform: 'cloudflare',
  samplingRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
});
```

### Migration Path

When services move from edge runtime to Node.js runtime (or vice versa), simply change the import:

```diff
- import { createEdgeObservability } from '@platform/observability-edge';
+ import { createObservability } from '@platform/observability';

- const observability = createEdgeObservability(config);
+ const observability = createObservability(config);
```

All usage code remains unchanged due to shared TypeScript interfaces.

## AI Agent Guidance

### Implementation Priority

**High** - Essential for development debugging and production operations

### Code Generation Patterns

```typescript
// Node.js runtime services (ECS, Lambda)
import { observability } from '@platform/observability';

// Edge runtime services (Cloudflare Workers, Next.js Edge)
import { observability } from '@platform/observability-edge';

// Consistent structured logging (same API across both packages)
observability.log.info('User registered successfully', {
  userId,
  email: user.email,
  registrationSource,
  correlationId: request.correlationId,
});

// Standard metrics collection (same API across both packages)
observability.metrics.counter.inc('user.registration.total', 1, {
  source: registrationSource,
  environment: process.env.NODE_ENV,
});

// Distributed tracing (same API across both packages)
const span = observability.tracing.startSpan('user.registration.process');
try {
  // Business logic
  await registerUser(userData);
  span.setStatus('OK');
} catch (error) {
  span.recordError(error);
  span.setStatus('ERROR');
  throw error;
} finally {
  span.end();
}
```

### Common Integration Points

- Node.js services must use `@platform/observability` (full OpenTelemetry)
- Edge runtime services must use `@platform/observability-edge` (zero Node.js dependencies)
- Never import vendor SDKs directly (Datadog, New Relic, etc.)
- Always include correlationId, tenantId, userId in log context
- Use OpenTelemetry Protocol (OTLP) for telemetry export from Node.js services
- Edge services log structured JSON with correlation IDs for manual correlation

### Platform Migration Benefits

- **Easy Migration**: Change configuration to point to new platform
- **Cost Optimization**: Compare platforms with same observability data
- **Risk Mitigation**: No single point of failure in tooling choices
- **Preserve History**: Maintain operational visibility during migrations

---

_Last Updated: September 15, 2025_
_Consolidated with ADR-019 for comprehensive observability strategy_
