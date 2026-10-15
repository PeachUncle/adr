# ADR-017: Optional Observability Stack

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template needs observability capabilities (metrics, logging, tracing) for production monitoring and debugging. However, the observability stack adds significant complexity and resource consumption. Key challenges include:

1. **Resource Consumption**: Full observability stack (Prometheus, Grafana, Loki, Tempo, Promtail) requires substantial memory and CPU
2. **Development Overhead**: Not all developers need observability during local development
3. **Learning Curve**: Five additional services to understand and troubleshoot
4. **Startup Time**: More services means longer `docker compose up` time
5. **Production Necessity**: Observability is essential for production but optional for development

The template must support comprehensive observability while allowing developers to opt out when resources are constrained or observability isn't needed.

## Decision

We implement observability as an **opt-in feature** via Cookiecutter template conditionals using the `include_observability` flag.

**Cookiecutter Configuration** (`template/cookiecutter.json`):
```json
{
  "include_observability": "yes",
  "prometheus_version": "v2.54.1",
  "grafana_version": "11.3.0",
  "loki_version": "3.2.1",
  "promtail_version": "3.2.1",
  "tempo_version": "2.6.1",
  "grafana_port": "3000",
  "prometheus_port": "9090",
  "loki_port": "3100",
  "tempo_http_port": "3200",
  "tempo_otlp_grpc_port": "4317",
  "tempo_otlp_http_port": "4318"
}
```

**Stack Components**:

| Service | Purpose | Port |
|---------|---------|------|
| **Prometheus** | Metrics collection and storage | 9090 |
| **Grafana** | Visualization dashboards | 3000 |
| **Loki** | Log aggregation | 3100 |
| **Tempo** | Distributed tracing | 3200, 4317, 4318 |
| **Promtail** | Docker log collection | N/A |

**Conditional Docker Compose** (`compose.yml`):
```yaml
{% if cookiecutter.include_observability == "yes" %}
  prometheus:
    image: prom/prometheus:{{ cookiecutter.prometheus_version }}
    # ... configuration

  loki:
    image: grafana/loki:{{ cookiecutter.loki_version }}
    # ... configuration

  tempo:
    image: grafana/tempo:{{ cookiecutter.tempo_version }}
    ports:
      - "${TEMPO_OTLP_GRPC_PORT:-4317}:4317"  # OTLP gRPC
      - "${TEMPO_OTLP_HTTP_PORT:-4318}:4318"  # OTLP HTTP
    # ... configuration

  grafana:
    image: grafana/grafana:{{ cookiecutter.grafana_version }}
    # ... configuration

  promtail:
    image: grafana/promtail:{{ cookiecutter.promtail_version }}
    # ... configuration
{% endif %}
```

**Conditional Backend Integration** (`backend/app/main.py`):
```python
{% if cookiecutter.include_observability == "yes" %}
from app.observability import setup_observability
{% endif %}

app = FastAPI(...)

{% if cookiecutter.include_observability == "yes" %}
# Setup observability (tracing, metrics, logging)
setup_observability(app)
{% endif %}
```

**Fail-Open Design Pattern**:
```yaml
# Backend does NOT depend on observability services
backend:
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
    keycloak:
      condition: service_healthy
    # NOTE: No dependency on prometheus, grafana, loki, tempo
```

## Consequences

### Positive

1. **Reduced Resource Usage**: Without observability, saves approximately:
   - Prometheus: ~256MB RAM
   - Grafana: ~256MB RAM
   - Loki: ~256MB RAM
   - Tempo: ~256MB RAM
   - Promtail: ~128MB RAM
   - **Total: ~1.1GB RAM saved**

2. **Faster Development Startup**: Five fewer services to start, reducing `docker compose up` time by 30-60 seconds.

3. **Simpler Development**: Developers not focused on observability aren't distracted by extra services, ports, and logs.

4. **Production-Ready When Enabled**: Full OpenTelemetry-based observability stack with:
   - Metrics: Prometheus scraping `/metrics` endpoint
   - Logging: Promtail collecting Docker logs to Loki
   - Tracing: OTLP export to Tempo

5. **Fail-Open Architecture**: Application continues functioning if observability services are unavailable - critical for production reliability.

6. **Pre-Configured Dashboards**: Grafana includes provisioned datasources and dashboards-as-code:
   ```
   observability/grafana/datasources/datasources.yml
   observability/grafana/dashboards/*.json
   ```

### Negative

1. **Two Code Paths**: Jinja2 conditionals in templates create two code paths to maintain and test.

2. **One-Time Decision**: `include_observability` is set at project generation; changing later requires manual edits.

3. **All-or-Nothing**: Cannot selectively include just metrics or just tracing; it's the complete stack or nothing.

4. **Docker Socket Access**: Promtail requires Docker socket access for log collection, which has security implications:
   ```yaml
   promtail:
     volumes:
       - /var/run/docker.sock:/var/run/docker.sock:ro
   ```

### Neutral

1. **Resource Limits Optional**: Docker Compose resource limits are commented out for development flexibility:
   ```yaml
   # deploy:
   #   resources:
   #     limits:
   #       memory: 512M
   ```

2. **OpenTelemetry Standard**: Uses OTLP (OpenTelemetry Protocol) for tracing, enabling future integration with other backends (Jaeger, Datadog, etc.).

## Alternatives Considered

### Always-On Observability

**Approach**: Include full observability stack in all generated projects.

**Why Not Chosen**:
- Resource-constrained developer machines struggle with extra 1GB+ RAM
- Not all projects need observability during development
- Increases complexity for learning the template

### External Observability Only

**Approach**: Support only external services (Datadog, New Relic, Grafana Cloud).

**Why Not Chosen**:
- Requires paid accounts or external infrastructure
- Not self-contained for local development
- Harder to debug without local tooling

### Minimal Observability (Prometheus Only)

**Approach**: Include only Prometheus for metrics, exclude logging/tracing.

**Why Not Chosen**:
- Incomplete observability story
- Debugging without logs/traces is significantly harder
- Three pillars (metrics, logs, traces) work together for effective troubleshooting

### Runtime Toggle (Environment Variable)

**Approach**: Single docker-compose with services disabled via profiles or environment variables.

**Why Not Chosen**:
- Docker Compose profiles add complexity
- Services still defined in compose.yml even when disabled
- Cookiecutter conditional provides cleaner separation

---

## Configuration Details

**Observability Service URLs** (when enabled):

| Service | URL | Purpose |
|---------|-----|---------|
| Grafana | http://localhost:3000 | Dashboards and exploration |
| Prometheus | http://localhost:9090 | Direct metrics queries |
| Loki | http://localhost:3100 | Log API |
| Tempo | http://localhost:3200 | Trace API |
| Backend Metrics | http://localhost:8000/metrics | Raw Prometheus metrics |

**Useful Queries**:
```promql
# Request rate by endpoint
rate(http_requests_total{job="backend"}[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="backend"}[5m]))
```

```logql
# Backend error logs
{container="project-slug-backend"} |= "ERROR"
```

---

## Related ADRs

- [ADR-010: Docker Compose Development](./010-docker-compose-development.md) - Container orchestration
- [ADR-016: Cookiecutter Template Engine](./016-cookiecutter-template-engine.md) - Template conditionals

## Implementation References

- `template/cookiecutter.json` - `include_observability` flag and version settings
- `template/{{cookiecutter.project_slug}}/compose.yml` - Conditional observability services
- `template/{{cookiecutter.project_slug}}/observability/` - Configuration files for each service
- `template/{{cookiecutter.project_slug}}/observability/README.md` - Observability documentation
- `template/{{cookiecutter.project_slug}}/backend/app/main.py` - Conditional observability setup
