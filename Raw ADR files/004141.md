# ADR-0008: Local-First Development Strategy

**Status**: Accepted  
**Date**: 2025-12-14  
**Deciders**: Tony Moores  
**Technical Story**: Phase 0 - Foundation, Cost Optimization

## Context

TJMPaaS is entering implementation phase after completing comprehensive governance and design documentation (96 markdown files, ~12,076 lines). The project charter established GCP as the pilot cloud platform (ADR-0001), but infrastructure costs during early development phases create financial constraints.

### Problem Statement

Determine the optimal deployment strategy for Phases 0-2 (Q4 2025 - Q2 2026) that:
- Minimizes infrastructure costs during early development
- Preserves cloud-ready architecture and portability
- Leverages existing local hardware and infrastructure
- Maintains eventual GCP deployment capability
- Supports solo developer productivity
- Enables validation before cloud commitment

### Current Situation

**Local Hardware** (monsoon workstation):
- CPU: Intel Core i7-7700 (4 cores, 8 threads @ 4.2GHz max)
- RAM: 64 GB DDR4
- Storage: 2.73 TB (2x 1TB SSD + 1TB external)
- Network: Gigabit Ethernet
- OS: Linux Mint Debian Edition 7 (LMDE 7 Gigi, Debian 13 trixie base)

**Existing Infrastructure**:
- Docker installed and operational
- Existing service images (~12 impl-* services from previous work)
- PostgreSQL images (15-alpine, 16-alpine, 16)
- MongoDB image (latest)
- Development tools (Swagger UI, calibre, Plex)
- Testing infrastructure (testcontainers/ryuk)
- Total Docker infrastructure: ~12GB of existing images

**Financial Constraint**:
- Early-stage development (no revenue yet)
- Cloud costs accumulate during experimental/learning phases
- Solo developer can work effectively on local hardware
- Prefer to defer cloud costs until services are production-ready

### Goals

- Zero infrastructure cost during Phase 0-2 (Q4 2025 - Q2 2026)
- Maintain cloud-ready architecture (containers, 12-factor, Kubernetes patterns)
- Validate architecture locally before cloud deployment
- Preserve flexibility to move to GCP when appropriate
- Document clear migration path (local → cloud)

### Constraints

- Must remain cloud-ready (no local-specific dependencies)
- Must work with Scala 3, Pekko/Akka, functional programming stack
- Must support containerization and Kubernetes patterns
- Must enable solo developer productivity
- Architecture must not diverge from cloud patterns

## Decision

**Adopt local-first development strategy for Phases 0-2** with:

1. **100% Local Development** (Phase 0-1, Q4 2025 - Q1 2026)
   - All services developed and tested on monsoon workstation
   - Docker Compose for infrastructure orchestration
   - Minikube for local Kubernetes learning and validation
   - Zero cloud infrastructure costs

2. **Hybrid Validation** (Phase 2, Q2 2026)
   - Continue local development as primary environment
   - GCP Free Tier for cloud validation only
   - Minimal cloud costs ($0-5/month)

3. **Strategic Cloud Adoption** (Phase 3+, Q3 2026+)
   - Deploy to GCP staging/production as services mature
   - Cloud costs scale with service readiness and revenue
   - Local development remains primary workflow

4. **Cloud-Ready Architecture Maintained**
   - All services containerized (Docker/OCI)
   - 12-factor app principles
   - Environment-agnostic configuration
   - Kubernetes-compatible deployment patterns
   - No local-specific dependencies

## Rationale

### Why Local-First Works for TJMPaaS

**Architecture is Cloud-Agnostic**:
- Scala 3 + JVM runs identically everywhere
- Docker containers ensure runtime consistency
- Kubernetes patterns work on Minikube/Kind/GKE
- No cloud-specific APIs in core services
- Configuration via environment variables

**Hardware Capacity Validated**:
Monsoon workstation can comfortably run full TJMPaaS stack:

| Component | Requirement | Monsoon | Status |
|-----------|-------------|---------|--------|
| **Infrastructure Services** | 8-12GB RAM | 64GB total | ✅ Excellent |
| PostgreSQL (3 instances) | 1.5GB | - | ✅ |
| Kafka + Zookeeper | 2GB | - | ✅ |
| Redis | 512MB | - | ✅ |
| Monitoring (Prometheus + Grafana) | 1GB | - | ✅ |
| **TJMPaaS Services (5-6 simultaneous)** | 8-12GB RAM | - | ✅ |
| Entity Management Service | 2GB | - | ✅ |
| Cart Service | 2GB | - | ✅ |
| Order Service | 2GB | - | ✅ |
| Product Catalog | 2GB | - | ✅ |
| Provisioning Service | 1.5GB | - | ✅ |
| **Development Tools** | 6-8GB RAM | - | ✅ |
| IDE (IntelliJ/VS Code) | 3GB | - | ✅ |
| Docker Desktop | 2GB | - | ✅ |
| Browsers + terminals | 2GB | - | ✅ |
| Mill builds | 1GB | - | ✅ |
| **OS + System** | 8-10GB RAM | - | ✅ |
| Linux kernel + services | 4GB | - | ✅ |
| File cache | 4GB | - | ✅ |
| Buffer | 2GB | - | ✅ |
| **Total Used** | ~38GB | - | - |
| **Available Buffer** | - | 26GB free | ✅ Outstanding |

**Comparison to Cloud Development VM**:

| Resource | Monsoon (Local) | Typical Cloud Dev VM | Advantage |
|----------|----------------|---------------------|-----------|
| CPU | 4c/8t @ 4.2GHz | 2c @ 2.0GHz | **2x faster** |
| RAM | 64GB | 8-16GB | **4-8x more** |
| Storage | 2TB SSD | 50-100GB | **20-40x more** |
| Network Latency | 0ms (local) | 5-50ms (cloud) | **Instant** |
| I/O Throughput | NVMe SSD | Network-attached | **10x faster** |
| Cost | $0/month | $50-200/month | **100% savings** |

**Existing Infrastructure Leveraged**:
- PostgreSQL images already present (15-alpine, 16-alpine, 16)
- MongoDB image available (latest, 910MB)
- Development tooling operational (Docker, testing infrastructure)
- ~12GB of existing impl-* service images (learning reference)
- No setup needed - just orchestration

**Cost Optimization**:

**Scenario 1: Immediate Cloud Development**
- GCP Development Environment: $150-200/month
  - e2-standard-4 VM (4 vCPU, 16GB RAM): $120/month
  - 200GB SSD storage: $30/month
  - Network egress: $10-20/month
  - Load balancer: $20/month
- **6 months (Phase 0-2): $900-1,200**

**Scenario 2: Local-First Development** (This ADR)
- Local development: $0/month
- GCP Free Tier validation (Phase 2): $0-5/month
- **6 months (Phase 0-2): $0-30**
- **Savings: $870-1,170**

**Scenario 3: Hybrid Cloud Development** (Rejected)
- Local + cloud staging from start: $50-100/month
- **6 months (Phase 0-2): $300-600**
- **Savings vs Scenario 1: $300-600**
- **Cost vs Scenario 2: $300-600 more**

**Development Velocity Benefits**:

1. **Zero Latency**: Local development = instant feedback loops
2. **Offline Capable**: Work without internet dependency
3. **Complete Control**: Full system access for debugging
4. **No Rate Limits**: No API quotas or throttling
5. **Fast Iteration**: Rebuild/restart in seconds, not minutes
6. **Rich Tooling**: Full IDE debugging, profiling, tracing

**Cloud Portability Preserved**:

**12-Factor App Compliance**:
- ✅ Codebase: Git version control
- ✅ Dependencies: Explicitly declared (Mill build.sc)
- ✅ Config: Environment variables (no hardcoded values)
- ✅ Backing Services: Attached resources (PostgreSQL, Kafka, Redis)
- ✅ Build/Release/Run: Docker images, immutable releases
- ✅ Processes: Stateless (state in databases/actors)
- ✅ Port Binding: Self-contained HTTP servers
- ✅ Concurrency: Scale via process model (Kubernetes pods)
- ✅ Disposability: Fast startup, graceful shutdown
- ✅ Dev/Prod Parity: Containers ensure consistency
- ✅ Logs: Stdout/stderr, structured logging
- ✅ Admin Processes: One-off tasks as containers

**Migration Path is Straightforward**:
1. Service runs in Docker locally → runs in GKE identically
2. docker-compose.yml → Kubernetes manifests (automated conversion)
3. Local PostgreSQL → Cloud SQL (connection string change only)
4. Local Kafka → Confluent Cloud or GCP Pub/Sub (configuration change)
5. Environment variables handle all differences

### Why Not Cloud-First?

**Cloud-First Drawbacks**:
- **Cost Accumulation**: $150-200/month during experimentation
- **Slower Iteration**: Network latency on every operation
- **Internet Dependency**: Can't work offline
- **Setup Overhead**: GCP account, billing, IAM, networks, etc.
- **Learning Curve**: Cloud platform + service development simultaneously
- **Premature Optimization**: Optimizing for scale before validating architecture

**Better Approach**: Validate architecture locally first, then migrate proven services to cloud.

## Alternatives Considered

### Alternative 1: Immediate Cloud Development

**Description**: Deploy directly to GCP from day one (per ADR-0001 original intent)

**Pros**:
- Production environment from start
- No migration needed
- Validates cloud patterns immediately
- No local setup

**Cons**:
- **Cost**: $150-200/month accumulates during learning/experimentation
- **Slower Iteration**: Network latency impacts development speed
- **Internet Required**: Can't work offline
- **Setup Complexity**: GCP configuration before coding
- **Premature**: Optimize for cloud scale before validating architecture

**Cost Analysis**:
- Phase 0-1 (6 months): ~$1,200
- Phase 2 (3 months): ~$600
- **Total Phase 0-2: ~$1,800**

**Reason for rejection**: Cost accumulates during experimental phase; local development faster and validates architecture before cloud commitment

### Alternative 2: Cloud Development Instances

**Description**: Use cloud VMs for development, services deployed locally within VM

**Pros**:
- Cloud environment
- Accessible from anywhere
- Snapshots and backups
- Scalable resources

**Cons**:
- **Cost**: $100-150/month for dev VM
- **Performance**: Worse than local (2 vCPU vs 4c/8t, 16GB vs 64GB)
- **Latency**: SSH/RDP latency impacts productivity
- **Complexity**: Remote development setup
- **Still not production**: Dev VM ≠ production GKE

**Cost Analysis**:
- 6 months: ~$900

**Reason for rejection**: Worse performance than local hardware, still accumulates costs, adds remote development complexity

### Alternative 3: Hybrid from Start

**Description**: Local development + cloud staging environment from beginning

**Pros**:
- Best of both worlds
- Cloud validation early
- Staging environment ready

**Cons**:
- **Cost**: $50-100/month for staging
- **Complexity**: Manage two environments from start
- **Premature**: Staging before services validated
- **Overhead**: Deployment automation before services stable

**Cost Analysis**:
- 6 months: ~$450

**Reason for rejection**: Staging premature before services validated; adds complexity during learning phase

### Alternative 4: Use GCP Free Tier Only

**Description**: Stay within GCP Always Free tier limits

**Pros**:
- Free cloud resources
- Real cloud environment
- No local setup

**Cons**:
- **Severe Limitations**:
  - e2-micro instance (2 vCPU shared, 1GB RAM) - insufficient for TJMPaaS stack
  - 30GB standard persistent disk - too small
  - No always-free database (Cloud SQL trial only)
  - US regions only
- **Not Viable**: Can't run TJMPaaS services (2GB+ each) on 1GB VM
- **Time Limits**: Some free tier resources have usage hour limits

**Reason for rejection**: Free tier resources insufficient for TJMPaaS development; 1GB RAM can't run services requiring 2GB+ each

### Alternative 5: Paid Cloud Tiers (AWS, Azure, DigitalOcean)

**Description**: Use alternative cloud providers with better free tiers or lower costs

**Pros**:
- Potentially lower costs
- Different free tier offerings
- Alternative platforms

**Cons**:
- **Still Costs Money**: Even cheaper clouds cost $30-50/month minimum for viable dev environment
- **Delays GCP Learning**: Want to learn GCP for eventual deployment
- **Migration Complexity**: Would need to migrate twice (alt cloud → GCP)
- **Inconsistent**: Different cloud patterns don't transfer

**Cost Analysis**:
- DigitalOcean: $48/month (4GB droplet)
- AWS: $50-100/month (t3.medium + services)
- Azure: $60-120/month (B2s + services)
- 6 months: ~$300-720

**Reason for rejection**: Still accumulates costs; defeats local-first cost optimization; delays GCP-specific learning

## Consequences

### Positive

- **Zero Infrastructure Cost**: $0/month during Phase 0-2 (saves $900-1,200 vs cloud)
- **Faster Development**: Local execution = instant feedback, zero latency
- **Offline Capable**: Work without internet dependency
- **Complete Control**: Full system access for debugging, profiling, tracing
- **No Rate Limits**: No API quotas or service throttling
- **Rich Development Experience**: Full IDE integration, local debugging
- **Hardware Advantage**: 64GB RAM > typical cloud dev VMs (8-16GB)
- **Validate Before Scale**: Prove architecture locally before cloud costs
- **Flexibility**: Can move to cloud anytime (cloud-ready architecture preserved)
- **Learning Curve**: Learn service development without simultaneous cloud platform learning

### Negative

- **Local Machine Dependency**: Development tied to monsoon availability
- **Manual Setup**: Must configure local infrastructure (one-time)
- **Environment Drift**: Local and cloud environments could diverge (mitigated by containers)
- **No Production Parity**: Local PostgreSQL ≠ Cloud SQL (mitigated by connection string abstraction)
- **Backup Responsibility**: Must manage local backups (Git + external drive)
- **Network Simulation**: Local can't fully simulate cloud networking complexity

### Neutral

- **Migration Eventually Needed**: Services will move to cloud (planned, not a surprise)
- **Two Environments**: Local + cloud (standard practice)
- **Setup Time**: Initial docker-compose setup required (4-6 hours one-time)

## Implementation

### Phase 0-1: Local-First Foundation (Q4 2025 - Q1 2026)

**Objective**: Develop and validate services entirely on monsoon workstation

#### Infrastructure Setup

**1. Create Local Infrastructure Configuration**

Directory structure:
```
~/TJMSolns/Projects/TJMPaaS/local-infra/
├── docker-compose.yml           # Complete infrastructure stack
├── .env.example                 # Environment variable template
├── prometheus.yml               # Metrics collection
├── grafana-datasources.yml      # Grafana configuration
├── kafka-topics.sh              # Kafka topic creation
├── postgres-init.sql            # Database initialization
└── README.md                    # Quick start guide
```

**2. Docker Compose Configuration**

Complete local infrastructure stack:

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL - Primary Database
  postgres:
    image: postgres:16-alpine
    container_name: tjmpaas-postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: tjmpaas
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-tjmpaas_dev}
      POSTGRES_DB: tjmpaas
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./postgres-init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - tjmpaas-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tjmpaas"]
      interval: 10s
      timeout: 5s
      retries: 5

  # PostgreSQL - Multi-Tenant Database
  postgres-tenants:
    image: postgres:16-alpine
    container_name: tjmpaas-postgres-tenants
    ports:
      - "5433:5432"
    environment:
      POSTGRES_USER: tjmpaas
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-tjmpaas_dev}
      POSTGRES_DB: tenants
    volumes:
      - postgres-tenants-data:/var/lib/postgresql/data
    networks:
      - tjmpaas-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tjmpaas"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis - Caching and Session Store
  redis:
    image: redis:7-alpine
    container_name: tjmpaas-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - tjmpaas-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Kafka - Event Streaming
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: tjmpaas-zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
      - zookeeper-logs:/var/lib/zookeeper/log
    networks:
      - tjmpaas-network

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: tjmpaas-kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "9093:9093"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092,PLAINTEXT_INTERNAL://kafka:9093
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_INTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT_INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    volumes:
      - kafka-data:/var/lib/kafka/data
    networks:
      - tjmpaas-network
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Kafka UI - Topic Management
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: tjmpaas-kafka-ui
    depends_on:
      - kafka
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9093
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
    networks:
      - tjmpaas-network

  # Prometheus - Metrics Collection
  prometheus:
    image: prom/prometheus:latest
    container_name: tjmpaas-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    networks:
      - tjmpaas-network

  # Grafana - Metrics Visualization
  grafana:
    image: grafana/grafana:latest
    container_name: tjmpaas-grafana
    depends_on:
      - prometheus
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}
      GF_USERS_ALLOW_SIGN_UP: "false"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    networks:
      - tjmpaas-network

  # Jaeger - Distributed Tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: tjmpaas-jaeger
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"  # Jaeger UI
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    environment:
      COLLECTOR_ZIPKIN_HOST_PORT: ":9411"
    networks:
      - tjmpaas-network

  # Adminer - Database Management UI
  adminer:
    image: adminer:latest
    container_name: tjmpaas-adminer
    depends_on:
      - postgres
      - postgres-tenants
    ports:
      - "8081:8080"
    networks:
      - tjmpaas-network

networks:
  tjmpaas-network:
    driver: bridge

volumes:
  postgres-data:
  postgres-tenants-data:
  redis-data:
  zookeeper-data:
  zookeeper-logs:
  kafka-data:
  prometheus-data:
  grafana-data:
```

**3. Prometheus Configuration**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'entity-management-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['host.docker.internal:8082']

  - job_name: 'cart-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['host.docker.internal:8083']

  - job_name: 'order-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['host.docker.internal:8084']

  - job_name: 'product-catalog-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['host.docker.internal:8085']

  - job_name: 'provisioning-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['host.docker.internal:8086']
```

**4. Grafana Datasource Configuration**

```yaml
# grafana-datasources.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

**5. Kafka Topics Initialization**

```bash
# kafka-topics.sh
#!/bin/bash

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
sleep 30

# Create TJMPaaS topics
docker exec tjmpaas-kafka kafka-topics --create --if-not-exists \
  --topic entity-management.tenants.v1 \
  --bootstrap-server localhost:9093 \
  --partitions 3 \
  --replication-factor 1

docker exec tjmpaas-kafka kafka-topics --create --if-not-exists \
  --topic entity-management.organizations.v1 \
  --bootstrap-server localhost:9093 \
  --partitions 3 \
  --replication-factor 1

docker exec tjmpaas-kafka kafka-topics --create --if-not-exists \
  --topic entity-management.users.v1 \
  --bootstrap-server localhost:9093 \
  --partitions 3 \
  --replication-factor 1

docker exec tjmpaas-kafka kafka-topics --create --if-not-exists \
  --topic entity-management.roles.v1 \
  --bootstrap-server localhost:9093 \
  --partitions 3 \
  --replication-factor 1

docker exec tjmpaas-kafka kafka-topics --create --if-not-exists \
  --topic entity-management.audit.v1 \
  --bootstrap-server localhost:9093 \
  --partitions 6 \
  --replication-factor 1

docker exec tjmpaas-kafka kafka-topics --create --if-not-exists \
  --topic cart.events.v1 \
  --bootstrap-server localhost:9093 \
  --partitions 3 \
  --replication-factor 1

docker exec tjmpaas-kafka kafka-topics --create --if-not-exists \
  --topic order.events.v1 \
  --bootstrap-server localhost:9093 \
  --partitions 6 \
  --replication-factor 1

docker exec tjmpaas-kafka kafka-topics --create --if-not-exists \
  --topic product.events.v1 \
  --bootstrap-server localhost:9093 \
  --partitions 3 \
  --replication-factor 1

echo "Kafka topics created successfully"
docker exec tjmpaas-kafka kafka-topics --list --bootstrap-server localhost:9093
```

**6. PostgreSQL Initialization**

```sql
-- postgres-init.sql
-- Create databases for services
CREATE DATABASE entity_management;
CREATE DATABASE cart_service;
CREATE DATABASE order_service;
CREATE DATABASE product_catalog;
CREATE DATABASE provisioning_service;

-- Create read-only user for reporting/analytics
CREATE USER tjmpaas_readonly WITH PASSWORD 'readonly_dev';

-- Grant read-only access
GRANT CONNECT ON DATABASE entity_management TO tjmpaas_readonly;
GRANT CONNECT ON DATABASE cart_service TO tjmpaas_readonly;
GRANT CONNECT ON DATABASE order_service TO tjmpaas_readonly;
GRANT CONNECT ON DATABASE product_catalog TO tjmpaas_readonly;
GRANT CONNECT ON DATABASE provisioning_service TO tjmpaas_readonly;

-- Note: Schema-level permissions granted after service initialization
```

**7. Quick Start Guide**

```markdown
# TJMPaaS Local Infrastructure Quick Start

## Prerequisites

- Docker installed and running
- Docker Compose installed
- 8GB+ RAM available (16GB+ recommended)
- 20GB+ disk space

## Starting Infrastructure

### First Time Setup

1. **Copy environment template**:
   ```bash
   cd ~/TJMSolns/Projects/TJMPaaS/local-infra
   cp .env.example .env
   # Edit .env to set passwords
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Verify services are healthy**:
   ```bash
   docker-compose ps
   ```

4. **Create Kafka topics**:
   ```bash
   chmod +x kafka-topics.sh
   ./kafka-topics.sh
   ```

5. **Access management UIs**:
   - Kafka UI: http://localhost:8080
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090
   - Jaeger: http://localhost:16686
   - Adminer: http://localhost:8081

### Daily Development

**Start infrastructure** (fast startup using existing volumes):
```bash
docker-compose up -d
```

**Stop infrastructure** (preserves data):
```bash
docker-compose stop
```

**View logs**:
```bash
docker-compose logs -f [service-name]
```

**Restart a specific service**:
```bash
docker-compose restart [service-name]
```

### Service Connection Details

**PostgreSQL**:
- Host: localhost
- Port: 5432
- User: tjmpaas
- Password: (from .env)
- Databases: entity_management, cart_service, order_service, product_catalog, provisioning_service

**PostgreSQL (Tenants)**:
- Host: localhost
- Port: 5433
- User: tjmpaas
- Password: (from .env)
- Database: tenants

**Redis**:
- Host: localhost
- Port: 6379

**Kafka**:
- Bootstrap Servers: localhost:9092
- Topics: Auto-created or via kafka-topics.sh

**Prometheus**:
- URL: http://localhost:9090

**Grafana**:
- URL: http://localhost:3000
- Username: admin
- Password: (from .env)

**Jaeger**:
- URL: http://localhost:16686

### Cleanup

**Stop and remove containers** (preserves volumes):
```bash
docker-compose down
```

**Remove everything including volumes** (DANGER: loses all data):
```bash
docker-compose down -v
```

## Service Development Workflow

1. **Start infrastructure**: `docker-compose up -d`
2. **Verify connectivity**: Check management UIs
3. **Run service locally**: `mill <service>.run`
4. **Service connects to**: localhost:5432 (PostgreSQL), localhost:9092 (Kafka), etc.
5. **Monitor**: Grafana (metrics), Jaeger (traces), Kafka UI (events)
6. **Stop infrastructure when done**: `docker-compose stop`

## Troubleshooting

**Service won't start**:
```bash
docker-compose logs [service-name]
```

**Port already in use**:
- Check for conflicting services: `sudo netstat -tlnp | grep [port]`
- Stop conflicting service or change port in docker-compose.yml

**Out of memory**:
- Check Docker memory limits: `docker stats`
- Increase Docker Desktop memory allocation
- Stop unused services

**Slow performance**:
- Check disk space: `df -h`
- Clean up old containers: `docker system prune`
- Monitor resource usage: `docker stats`
```

#### Local Kubernetes Setup

**Option 1: Minikube** (Recommended)

```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=16384 --disk-size=50g

# Enable useful addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Access Kubernetes dashboard
minikube dashboard
```

**Option 2: Kind** (Kubernetes in Docker)

```bash
# Install Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create cluster
kind create cluster --name tjmpaas-local --config kind-config.yml

# kind-config.yml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
- role: worker
- role: worker
```

**Option 3: k3s** (Lightweight Kubernetes)

```bash
# Install k3s
curl -sfL https://get.k3s.io | sh -

# Check status
sudo k3s kubectl get node
```

**Recommendation for TJMPaaS**: Start with Minikube (most similar to GKE), use Kind if Docker-based workflow preferred, consider k3s for minimal overhead.

#### Service Development Workflow

**1. Clone Service Template**:
```bash
cd ~/TJMSolns/Projects
git clone https://github.com/TJMSolns/TJMSolns-ServiceTemplate.git TJMSolns-EntityManagementService
cd TJMSolns-EntityManagementService
```

**2. Implement Service**:
- Follow Entity Management Service design (18 files in doc/internal/technical/services/entity-management/)
- Mill build: `mill <module>.compile`
- Run tests: `mill <module>.test`
- Run locally: `mill <module>.run` (connects to localhost:5432, localhost:9092, etc.)

**3. Containerize**:
```bash
# Build Docker image
mill <module>.assembly
docker build -t tjmsolns/entity-management-service:0.1.0 .
```

**4. Test Locally**:
```bash
# Run service container
docker run -d \
  --name entity-management-service \
  --network tjmpaas-network \
  -p 8082:8080 \
  -e POSTGRES_HOST=postgres \
  -e KAFKA_BOOTSTRAP_SERVERS=kafka:9093 \
  -e REDIS_HOST=redis \
  tjmsolns/entity-management-service:0.1.0

# Check logs
docker logs -f entity-management-service

# Test endpoints
curl http://localhost:8082/health
curl http://localhost:8082/ready
curl -X POST http://localhost:8082/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{"name":"ACME Corp","plan":"professional"}'
```

**5. Validate**:
- Metrics: http://localhost:9090 (Prometheus)
- Traces: http://localhost:16686 (Jaeger)
- Events: http://localhost:8080 (Kafka UI)
- Database: http://localhost:8081 (Adminer)

### Phase 2: Hybrid Validation (Q2 2026)

**Objective**: Validate cloud deployment with minimal cost using GCP Free Tier

#### GCP Free Tier Usage Strategy

**Always Free Resources** (No time limit):
- 1 non-preemptible e2-micro VM instance per month (US regions only)
- 30 GB-months standard persistent disk
- 5 GB-month snapshot storage (Regional)
- 1 GB network egress per month (North America to all region destinations)

**Free Trial Resources** ($300 credit, 90 days):
- GKE Autopilot cluster
- Cloud SQL PostgreSQL (db-f1-micro)
- Pub/Sub (10 GB messages per month)
- Cloud Logging (first 50 GB per month)

**Phase 2 Strategy**:

**Week 1-2: Single Service Deployment**
- Deploy Entity Management Service to GKE Autopilot (Free Trial)
- Use Cloud SQL db-f1-micro (Free Trial)
- Validate Kubernetes manifests work correctly
- Test multi-tenant data isolation in cloud
- **Cost**: $0 (within Free Trial credits)

**Week 3-4: Integration Validation**
- Deploy Cart Service alongside Entity Management
- Test inter-service communication
- Validate Kafka Pub/Sub integration
- Test distributed tracing
- **Cost**: $0-5/month (minimal overage)

**Week 5-8: Performance Baseline**
- Load testing cloud deployment
- Compare local vs cloud performance
- Validate SLO targets (<200ms p95)
- Document cloud-specific configurations
- **Cost**: $0-5/month

**Outcome**: Services validated in cloud environment before committing to ongoing costs.

### Phase 3+: Strategic Cloud Adoption (Q3 2026+)

**Trigger Conditions** (When to increase cloud usage):
1. **Service Maturity**: 3+ services production-ready
2. **External Access Needed**: Demo to clients/stakeholders
3. **Team Growth**: Multiple developers need shared environment
4. **Revenue Generation**: Services generating income to cover costs
5. **Scale Testing**: Need to validate high-volume scenarios

**Phased Migration**:

**Stage 1: Staging Environment** (1-2 services)
- Deploy mature services to GKE staging
- Cloud SQL for persistence
- Pub/Sub for events
- **Cost**: $50-100/month

**Stage 2: Production Beta** (3-4 services)
- Production GKE cluster (small)
- Multi-region Cloud SQL
- Monitoring and logging
- **Cost**: $200-300/month

**Stage 3: Production Scale** (5+ services)
- Full GKE cluster
- Multi-region deployment
- CDN, load balancing
- **Cost**: $500-1000+/month (scales with usage)

**Local Development Remains Primary**:
Even in Phase 3+, developers work locally:
- Fast iteration cycles
- Offline capability
- Zero local infrastructure cost
- Cloud for staging/production only

### Migration Checklist (Local → Cloud)

When moving a service from local to cloud:

**Pre-Migration**:
- [ ] Service containerized and tested locally
- [ ] Environment variables externalized (no hardcoded values)
- [ ] Health checks implemented (/health, /ready)
- [ ] Metrics exposed (Prometheus format)
- [ ] Structured logging to stdout/stderr
- [ ] Graceful shutdown implemented (SIGTERM handling)
- [ ] Connection strings use environment variables
- [ ] Secrets managed via environment (not hardcoded)
- [ ] Service documented in SERVICE-CANVAS.md

**Migration Steps**:
- [ ] Create GCP project (if not exists)
- [ ] Push Docker image to Artifact Registry
- [ ] Create Kubernetes namespace
- [ ] Create Cloud SQL instance
- [ ] Create Pub/Sub topics
- [ ] Create Kubernetes secrets (database passwords, API keys)
- [ ] Deploy service to GKE
- [ ] Verify health checks passing
- [ ] Verify metrics collection
- [ ] Verify logging aggregation
- [ ] Run integration tests
- [ ] Update DNS (if applicable)

**Post-Migration**:
- [ ] Monitor for 24 hours
- [ ] Validate SLO targets
- [ ] Document cloud-specific configuration
- [ ] Update service documentation
- [ ] Create runbooks for cloud operations

**Rollback Plan**:
If issues arise, service can continue running locally while cloud issues resolved. No service interruption.

## Validation

### Success Criteria

**Phase 0-1 (Q4 2025 - Q1 2026)**:
- ✅ All infrastructure services running locally (PostgreSQL, Kafka, Redis, monitoring)
- ✅ Entity Management Service implemented and tested locally
- ✅ 2-3 additional services implemented
- ✅ All services containerized
- ✅ Architecture validated (CQRS, event sourcing, actor model, multi-tenant)
- ✅ Zero cloud infrastructure costs ($0/month)
- ✅ Performance targets met locally (<200ms p95 response time)

**Phase 2 (Q2 2026)**:
- ✅ At least 1 service deployed to GKE (Free Trial)
- ✅ Cloud deployment validated (Kubernetes, Cloud SQL, Pub/Sub)
- ✅ Multi-tenant isolation validated in cloud
- ✅ Cloud costs within Free Tier + minimal overage ($0-5/month)
- ✅ Migration process documented and proven

**Phase 3+ (Q3 2026+)**:
- ✅ Strategic cloud deployment based on maturity and revenue
- ✅ Local development remains primary workflow
- ✅ Cloud costs justified by business value

### Metrics

**Cost Optimization**:
- Target: $0/month Phase 0-1, $0-5/month Phase 2
- Actual: Track monthly GCP spending
- Savings vs cloud-first: ~$1,200 over 6 months

**Development Velocity**:
- Service implementation time: Track days from design to running
- Iteration cycle time: Track rebuild/restart time (target: <2 minutes)
- Deployment time (local): Track docker-compose restart (target: <1 minute)

**Performance**:
- Local response times: <200ms p95 for queries, <500ms p95 for commands
- Local throughput: 100+ requests/second per service
- Resource utilization: <40GB RAM used with full stack running

**Architecture Validation**:
- Actor model: Supervision working, no deadlocks
- CQRS: Read/write separation validated
- Event sourcing: Event replay working correctly
- Multi-tenant: Isolation validated, no cross-tenant data leakage
- Integration: Services communicate via Kafka successfully

**Cloud Readiness**:
- All services containerized: 100%
- 12-factor compliance: 100%
- Environment-agnostic: No local-specific code
- Migration time: <1 day per service

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Local machine failure** | Medium | - Regular Git commits/pushes<br>- External backup drive (2TB available)<br>- Service code in GitHub<br>- Data re-seedable from events<br>- Can restore development environment in <4 hours |
| **Environment drift** (local ≠ cloud) | Medium | - Containers ensure consistency<br>- Same PostgreSQL version (16)<br>- Same Kafka version (7.5.0)<br>- 12-factor app compliance<br>- Regular cloud validation (Phase 2) |
| **Performance differences** (local vs cloud) | Low | - Local hardware superior to typical cloud VMs<br>- Cloud likely slower, not faster<br>- Can optimize for cloud after validation<br>- Performance monitoring in both environments |
| **Network simulation limitations** | Low | - Local can't replicate cloud network latency<br>- Mitigated: Resilience patterns (timeouts, retries, circuit breakers)<br>- Validated in Phase 2 cloud testing |
| **Storage limitations** | Low | - 2TB local storage available<br>- TJMPaaS services use <100GB<br>- Can add external storage if needed |
| **Backup discipline** | Medium | - Automated Git pre-commit hooks<br>- Weekly external drive backups<br>- Docker volumes backed up monthly<br>- Event store provides audit trail |
| **Premature optimization** | Low | - Local development catches architectural issues early<br>- Validated architecture before cloud costs<br>- Can refactor locally cheaply |

## Related Decisions

- [ADR-0001: GCP as Pilot Platform](./ADR-0001-gcp-pilot-platform.md) - Cloud platform choice preserved, timeline adjusted
- [ADR-0003: Containerization Strategy](./ADR-0003-containerization-strategy.md) - Containers enable local/cloud parity
- [ADR-0004: Scala 3 Technology Stack](./ADR-0004-scala3-technology-stack.md) - JVM runs identically everywhere
- [ADR-0005: Reactive Manifesto Alignment](./ADR-0005-reactive-manifesto-alignment.md) - Reactive principles work locally and in cloud
- [PDR-0004: Repository Organization Strategy](./PDR-0004-repository-organization.md) - Multi-repo enables local development per service
- Future: LOCAL-DEVELOPMENT-GUIDE.md (practical quick start)
- Future: Update ROADMAP.md to reflect local-first phases

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Kind (Kubernetes in Docker)](https://kind.sigs.k8s.io/)
- [k3s - Lightweight Kubernetes](https://k3s.io/)
- [GCP Free Tier](https://cloud.google.com/free)
- [GCP Always Free Resources](https://cloud.google.com/free/docs/free-cloud-features#free-tier)
- [12-Factor App Methodology](https://12factor.net/)
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Confluent Kafka Docker Images](https://hub.docker.com/r/confluentinc/cp-kafka)
- [Redis Docker Hub](https://hub.docker.com/_/redis)

## Notes

### Hardware ROI Analysis

**Monsoon Workstation Value**:
- Equivalent cloud dev environment: $150-200/month
- Monsoon already owned and operational
- 6 months local development: Saves $900-1,200
- Monsoon pays for itself in 6 months of avoided cloud costs

**Hardware Advantages**:
- 64GB RAM = 4-8x typical cloud dev VM
- Local NVMe SSD = 10x faster than network-attached cloud storage
- 0ms latency = instant feedback loops
- Offline capable = work anywhere, anytime

### Docker Images Already Present

Monsoon has existing infrastructure from previous work:
- ~12 impl-* service images (implementation examples, learning reference)
- PostgreSQL 15-alpine, 16-alpine, 16 (multiple versions for compatibility)
- MongoDB latest (910MB)
- Development tools (Swagger UI, adminer-style tools)
- Testing infrastructure (testcontainers/ryuk)

**Value**: ~$500-1000/month equivalent cloud infrastructure already available locally. Just need orchestration (docker-compose).

### Production Parity

**What's Different**:
- Local PostgreSQL ≠ Cloud SQL (but same PostgreSQL version, APIs identical)
- Local Kafka ≠ Pub/Sub (different protocols, requires code changes)
- Local networking ≠ Cloud networking (latency, firewalls)

**What's Same**:
- Docker containers run identically
- Application code unchanged
- JVM behavior identical
- Scala libraries identical
- Business logic identical

**Mitigation**: Abstract backing services via interfaces, configuration handles differences.

### Progressive Validation Strategy

**Phase 0-1**: Validate architecture patterns locally
- Actor supervision working correctly?
- CQRS read/write separation effective?
- Event sourcing event replay working?
- Multi-tenant isolation complete?
- Performance targets met?

**Phase 2**: Validate cloud deployment
- Kubernetes manifests correct?
- Cloud SQL connection working?
- Pub/Sub integration functional?
- Monitoring/logging operational?
- Multi-tenant works in cloud?

**Phase 3+**: Validate at scale
- High-volume scenarios?
- Multi-region deployment?
- Disaster recovery?
- Cost optimization?

**Rationale**: Fix architectural issues locally (cheap) before encountering them in cloud (expensive).

### When Local-First Stops Making Sense

**Trigger Conditions** (Move to cloud):
1. **Team Growth**: 3+ developers need shared environment (local dev scales to ~2 developers comfortably)
2. **External Access**: Clients/stakeholders need access (local not accessible)
3. **Scale Validation**: Need to test 1000+ requests/second (local sufficient for 100 req/s)
4. **Revenue**: Services generating income to cover cloud costs
5. **Multi-Region**: Need global deployment (local single-region only)
6. **Compliance**: Regulatory requirements mandate cloud (local dev environment insufficient)

**Until Then**: Local-first remains optimal.

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-12-14 | Initial draft and acceptance | Tony Moores |
