# ADR-016: Chaos Engineering Framework

## Status
Accepted

## Context
To build confidence in system reliability and validate resilience patterns, BitVelocity needs systematic chaos engineering practices. This provides hands-on learning of:
- Failure mode analysis
- Incident response
- Observability under stress
- Circuit breaker and retry patterns
- Distributed system failure scenarios

## Decision

### Chaos Engineering Platform
**Chaos Mesh** - Selected for:
- Native Kubernetes integration
- Rich experiment types
- Easy YAML-based configuration
- Good documentation
- Active community
- Free and open-source

### Experiment Categories

#### 1. Pod Chaos
- Pod kill
- Pod failure
- Container kill
- Specific container restart

#### 2. Network Chaos
- Network delay/latency
- Packet loss
- Network partition
- Bandwidth limitation
- DNS failure

#### 3. Stress Chaos
- CPU stress
- Memory stress
- I/O stress

#### 4. Time Chaos
- Clock skew
- Time offset

#### 5. Application Chaos
- JVM chaos (future)
- HTTP chaos
- Kernel chaos

### Safety Guidelines

**Blast Radius Control**:
1. Start with `mode: one` (single pod)
2. Progress to `mode: fixed` with specific count
3. Never use `mode: all` in shared environments
4. Use label selectors carefully

**Environment Strategy**:

- Dev: Open experimentation
- Staging: Scheduled chaos (nightly)
- Production: Manual game days only (future)

**Always Have**:

- Rollback plan (pause/delete experiment)
- Active monitoring during experiment
- Team notification before running
- Post-mortem documentation

### Game Days

Structured chaos exercises with team participation:

**Format**:
1. **Preparation** (15min): Set baseline, verify monitoring
2. **Chaos Injection** (30min): Run experiments, observe
3. **Incident Response** (30min): Team responds as in production
4. **Recovery** (15min): Clean up, verify restoration
5. **Debrief** (30min): Discuss learnings, action items

**Frequency**:

- Monthly game days for primary domains
- Quarterly cross-domain scenarios
- Ad-hoc for new features

### Experiment Workflow

```yaml
# Standard experiment template
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: <service>-<type>-<scenario>
  namespace: bitvelocity
spec:
  action: <pod-kill | pod-failure>
  mode: <one | fixed | all>
  selector:
    namespaces: [bitvelocity]
    labelSelectors:
      app: <service-name>
  duration: '<duration>'
  scheduler:
    cron: '@every <interval>'  # optional
```

### Validation Criteria

Every experiment must define:
- **Hypothesis**: Expected behavior
- **Blast radius**: What can be affected
- **Success criteria**: Metrics/logs to check
- **Failure indicators**: What means experiment failed
- **Recovery validation**: How to confirm system recovered

### Integration with Observability

Required instrumentation for chaos engineering:
- Circuit breaker state metrics
- Retry attempt counters
- Error rate by type
- Latency percentiles
- Resource utilization
- Distributed tracing for failure propagation

### Documentation

All experiments must be documented with:
- Purpose and learning objectives
- Expected vs actual behavior
- Metrics collected
- Findings and improvements identified
- Action items created

## Consequences

### Positive
- Hands-on resilience pattern learning
- Identifies weak points before production
- Builds team confidence in failure handling
- Improves observability and alerting
- Documents failure modes and responses
- Validates architecture decisions

### Negative
- Requires stable observability stack
- Can be disruptive if not carefully scoped
- Requires discipline and documentation
- Initial setup and learning curve
- May expose uncomfortable truths about system

### Trade-offs
- Chose Chaos Mesh over Litmus for better K8s integration
- Manual game days over automated chaos (learning > automation)
- Structured experiments over random chaos (educational value)

## Implementation Plan

1. **Phase 1 (Week 1)**: Setup
   - Install Chaos Mesh on dev cluster
   - Create experiment templates
   - Document safety procedures

2. **Phase 2 (Week 2)**: Basic Experiments
   - Pod kill experiments for 3 services
   - Network latency experiments
   - Document baseline behavior

3. **Phase 3 (Week 3)**: Game Day Preparation
   - Create first game day runbook
   - Practice with team
   - Set up communication channels

4. **Phase 4 (Week 4)**: First Game Day
   - Run inventory service failure scenario
   - Document learnings
   - Create improvement backlog

5. **Phase 5 (Ongoing)**: Expansion
   - Add more experiment types
   - Increase complexity
   - Introduce cross-service scenarios
   - Consider CI integration (staging)

## Examples

### Simple Pod Kill
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: order-service-pod-kill
spec:
  action: pod-kill
  mode: one
  selector:
    labelSelectors:
      app: order-service
  scheduler:
    cron: '@every 2m'
```

### Network Latency
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: inventory-latency
spec:
  action: delay
  mode: all
  selector:
    labelSelectors:
      app: inventory-service
  delay:
    latency: '200ms'
    jitter: '50ms'
  duration: '5m'
```

## References
- `bv-chaos-experiments/README.md`
- `bv-chaos-experiments/game-days/runbook-inventory-failure.md`
- [Chaos Mesh Documentation](https://chaos-mesh.org/docs/)
- [Principles of Chaos Engineering](https://principlesofchaos.org/)
- ADR-007: Observability Baseline (monitoring requirements)
- ADR-006: Retry & Backoff Policies (patterns to validate)
