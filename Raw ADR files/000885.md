# ADR-015: Load Testing and Performance Engineering Strategy

## Status
Accepted

## Context
BitVelocity requires comprehensive performance testing to:
- Establish performance baselines for all services
- Detect performance regressions early in CI/CD
- Practice capacity planning and scalability analysis
- Validate SLI/SLO targets
- Learn hands-on performance engineering patterns

The system spans multiple protocols (REST, gRPC, WebSocket, Kafka) requiring varied testing approaches.

## Decision

### Testing Framework Stack
- **Gatling (Java)**: Primary load testing framework for complex scenarios
- **k6**: Lightweight performance testing for CI/CD integration
- **JMeter**: Optional for specific protocol testing (SOAP, MQTT)

### Test Categories

#### 1. Smoke Tests
- **Purpose**: Quick validation, regression detection
- **Duration**: < 1 minute
- **Load**: 10 VUs
- **Frequency**: Every PR
- **Tool**: k6
- **Location**: `.github/workflows/performance-smoke.yml`

#### 2. Load Tests
- **Purpose**: Validate performance under expected load
- **Duration**: 5-15 minutes
- **Load**: Ramp to 100-500 users
- **Frequency**: Nightly
- **Tool**: Gatling

#### 3. Stress Tests
- **Purpose**: Find breaking points
- **Duration**: 15-30 minutes
- **Load**: Incremental until failure
- **Frequency**: Weekly
- **Tool**: Gatling

#### 4. Spike Tests
- **Purpose**: Test behavior under sudden load increases
- **Duration**: 5-10 minutes
- **Load**: Immediate spike to 200+ users
- **Frequency**: Weekly
- **Tool**: Gatling

#### 5. Endurance Tests
- **Purpose**: Detect memory leaks, resource exhaustion
- **Duration**: 2-4 hours
- **Load**: Sustained moderate load
- **Frequency**: Monthly

### Performance Targets (Initial Baselines)

| Service/Flow | p50 | p95 | p99 | Throughput |
|--------------|-----|-----|-----|------------|
| POST /orders | 50ms | 200ms | 500ms | 100 req/s |
| GET /products/{id} | 15ms | 50ms | 100ms | 500 req/s |
| gRPC ReserveStock | 30ms | 100ms | 200ms | 200 req/s |
| WebSocket fan-out | 50ms | 150ms | 300ms | 1000 msg/s |

### CI/CD Integration

```yaml
# Performance gates in pipeline
performance_smoke:
  thresholds:
    - p95 < 200ms
    - error_rate < 1%
    - degradation < 10% (compared to baseline)
```

### Metrics Collection
All tests must collect:
- Response time distributions (p50, p90, p95, p99)
- Error rates by type
- Throughput (requests/second)
- Resource utilization (CPU, memory, network)
- JVM metrics (if applicable)

### Test Data Management
- Synthetic data generators per domain
- Repeatable test data sets for deterministic results
- PII-free data for compliance

### Result Storage
- JSON results stored in git (trending analysis)
- Grafana dashboards for visualization
- Automated comparison with baselines

## Consequences

### Positive
- Early detection of performance regressions
- Hands-on learning of performance engineering
- Data-driven capacity planning
- Confidence in scalability
- Better understanding of system behavior under load

### Negative
- Additional CI/CD time (mitigated by parallel execution)
- Infrastructure costs for load testing environments
- Requires discipline to maintain test scenarios
- Initial learning curve for Gatling/k6

### Trade-offs
- Chose Gatling (Java) over Scala DSL for consistency with codebase
- k6 for CI due to speed, Gatling for comprehensive scenarios
- Accepted longer test times for production-like load profiles

## Implementation Plan

1. **Phase 1 (Week 1-2)**: Setup infrastructure
   - Create `bv-performance-testing` module
   - Set up Gatling project structure
   - Create baseline k6 smoke tests

2. **Phase 2 (Week 3)**: Implement core scenarios
   - Order creation flow (Gatling)
   - Product browsing (k6)
   - Inventory operations (Gatling)

3. **Phase 3 (Week 4)**: CI/CD integration
   - Add performance-smoke workflow
   - Configure thresholds and gates
   - Set up result reporting

4. **Phase 4 (Ongoing)**: Expand coverage
   - Add WebSocket/SSE scenarios
   - Implement stress and endurance tests
   - Build Grafana dashboards

## References
- `bv-performance-testing/README.md`
- `bv-performance-testing/performance-baselines/sli-targets.yaml`
- `.github/workflows/performance-smoke.yml`
- [Gatling Documentation](https://gatling.io/docs/)
- [k6 Documentation](https://k6.io/docs/)
