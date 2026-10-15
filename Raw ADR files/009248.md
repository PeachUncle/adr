# ADR-011: Port Allocation Strategy

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template runs multiple services via Docker Compose that need to expose ports to the host machine for development. Key challenges include:

1. **Port Conflicts**: Common ports (5432, 8080, 3000) are often used by other applications
2. **Multiple Projects**: Developers may run multiple project-starter instances simultaneously
3. **Developer Experience**: Ports should be memorable and easy to type
4. **Debugging**: Port assignments should be logical for troubleshooting
5. **Convention**: Some ports have strong conventions (e.g., 5432 for PostgreSQL)

The template needs a consistent port allocation strategy that minimizes conflicts while remaining intuitive.

## Decision

We implement a **conflict-avoidant port allocation strategy** using non-standard but memorable ports for services that commonly conflict.

**Port Allocations** (defined in `template/cookiecutter.json`):

| Service | Port | Rationale |
|---------|------|-----------|
| **PostgreSQL** | 5435 | Avoids conflict with local PostgreSQL (5432) |
| **Redis** | 6379 | Standard Redis port (conflicts less common) |
| **Keycloak** | 8080 | Standard HTTP port for Java services |
| **Backend (FastAPI)** | 8000 | Standard Python/ASGI convention |
| **Frontend (Vite)** | 5173 | Vite default development port |
| **Grafana** | 3000 | Grafana default (when observability enabled) |
| **Prometheus** | 9090 | Prometheus default |
| **Loki** | 3100 | Loki default |
| **Tempo HTTP** | 3200 | Tempo default |
| **Tempo OTLP gRPC** | 4317 | OpenTelemetry standard |
| **Tempo OTLP HTTP** | 4318 | OpenTelemetry standard |

**Configuration** (`template/cookiecutter.json`):
```json
{
  "postgres_port": "5435",
  "redis_port": "6379",
  "keycloak_port": "8080",
  "backend_port": "8000",
  "frontend_port": "5173",
  "grafana_port": "3000",
  "prometheus_port": "9090",
  "loki_port": "3100",
  "tempo_http_port": "3200",
  "tempo_otlp_grpc_port": "4317",
  "tempo_otlp_http_port": "4318"
}
```

**Environment Variable Overrides** (`compose.yml`):
```yaml
postgres:
  ports:
    - "${POSTGRES_PORT:-5435}:5432"

keycloak:
  ports:
    - "${KEYCLOAK_PORT:-8080}:8080"

backend:
  ports:
    - "${BACKEND_PORT:-8000}:8000"
```

## Consequences

### Positive

1. **PostgreSQL Conflict Avoidance**: Port 5435 avoids the most common conflict - local PostgreSQL installations default to 5432. Developers can run both simultaneously.

2. **Environment Customization**: All ports overridable via environment variables, enabling:
   ```bash
   POSTGRES_PORT=5436 docker compose up  # Use different port if 5435 also conflicts
   ```

3. **Memorable Ports**: PostgreSQL at 5435 is easy to remember (543x family), backend at 8000 follows Python convention.

4. **Standard Observability Ports**: Grafana/Prometheus/Loki/Tempo use their default ports - developers familiar with these tools find them where expected.

5. **Vite Default**: Frontend port 5173 is Vite's default, matching Vite documentation and tutorials.

6. **Debugging Clarity**: Port numbers help identify which service is involved:
   - 5xxx = Database-related
   - 8xxx = Application services
   - 3xxx/9xxx = Observability

### Negative

1. **Non-Standard PostgreSQL Port**: Developers must remember to use 5435 instead of 5432 for database connections:
   ```bash
   psql -h localhost -p 5435 -U app_user  # Note: -p 5435
   ```

2. **Keycloak Port Conflict**: Port 8080 may conflict with other Java applications or development servers. Common enough to warrant documentation.

3. **Multiple Project Instances**: Running two project-starter instances still requires manual port changes via environment variables.

### Neutral

1. **Cookiecutter Customization**: Ports can be changed at project generation time, but defaults work for most scenarios.

2. **Docker Internal Ports**: Internal service-to-service communication uses standard ports (PostgreSQL still listens on 5432 inside the container).

## Alternatives Considered

### Standard Ports Only

**Approach**: Use conventional ports (PostgreSQL 5432, Redis 6379, etc.)

**Why Not Chosen**:
- PostgreSQL 5432 conflicts with nearly every local PostgreSQL installation
- Developers would need to stop local services or configure overrides immediately
- Poor initial developer experience

### High Random Ports (e.g., 15432, 16379)

**Approach**: Use high port numbers to virtually eliminate conflicts.

**Why Not Chosen**:
- Harder to remember and type
- Loses connection to conventional port numbers
- No clear pattern for debugging

### Single Offset (All +1000)

**Approach**: Shift all standard ports by 1000 (PostgreSQL 6432, Redis 7379, etc.)

**Why Not Chosen**:
- Some ports still conflict (Redis 7379 is sometimes used)
- Pattern not universally applicable
- PostgreSQL at 6432 is less memorable than 5435

### Dynamic Port Allocation

**Approach**: Let Docker assign random available ports.

**Why Not Chosen**:
- Unpredictable ports break IDE database connections
- Frontend/backend URL configuration becomes complex
- Poor developer experience for debugging

---

## Related ADRs

- [ADR-010: Docker Compose Development](./010-docker-compose-development.md) - Service orchestration
- [ADR-003: PostgreSQL as Primary Database](./003-postgresql-primary-database.md) - Database service

## Implementation References

- `template/cookiecutter.json` - Default port definitions
- `template/{{cookiecutter.project_slug}}/compose.yml` - Docker port mappings with env var overrides
- `template/{{cookiecutter.project_slug}}/.env.example` - Environment variable documentation
- `template/{{cookiecutter.project_slug}}/CLAUDE.md` - Service ports reference table
