# ADR-005: OpenTelemetry and Sentry for Observability

**Date:** 2024-01-15  
**Status:** Accepted  
**Deciders:** Platform Team, DevOps Team  
**Technical Story:** Observability and monitoring strategy

## Context

The Dashboard Starter Kit needs comprehensive observability to support:

1. **Production Monitoring**: Real-time visibility into application health and performance
2. **Error Tracking**: Automatic error capture, alerting, and debugging information
3. **Performance Monitoring**: Request tracing, database query analysis, bottleneck identification
4. **User Experience**: Frontend performance monitoring and error tracking
5. **Multi-Tenant Insights**: Tenant-specific metrics and issue isolation
6. **Debugging**: Distributed tracing across modules and external services
7. **Compliance**: Audit trails and monitoring for security/compliance requirements
8. **Scalability**: Observability solution that scales with application growth

We need to choose monitoring and observability tools that provide comprehensive coverage without significant performance impact or operational complexity.

## Decision

We will implement **OpenTelemetry for distributed tracing** and **Sentry for error tracking** as our primary observability stack.

### Architecture Approach:
- **OpenTelemetry**: Distributed tracing, metrics, and logging instrumentation
- **Sentry**: Error tracking, performance monitoring, and alerting
- **Structured Logging**: JSON-structured logs with correlation IDs
- **Request Context**: Trace IDs propagated through AsyncLocalStorage
- **Automatic Instrumentation**: Framework-level instrumentation with minimal code changes

### OpenTelemetry Setup:
```typescript
// packages/core/src/telemetry.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';

export function initTelemetry() {
  const sdk = new NodeSDK({
    instrumentations: [
      getNodeAutoInstrumentations({
        '@opentelemetry/instrumentation-http': {
          enabled: true,
        },
        '@opentelemetry/instrumentation-express': {
          enabled: true,
        },
        '@opentelemetry/instrumentation-pg': {
          enabled: true,
        },
      }),
    ],
  });
  
  sdk.start();
}
