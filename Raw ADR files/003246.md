# ADR-0004: Deployment Strategy for PolyShop Microservices

## Status
Accepted

## Date
2025-11-17

## Context
PolyShop consists of independently deployable microservices:
- Auth
- Product
- Inventory
- Order
- Payment
- Search
- Analytics
- Notification
- Gateway

Each service must support:
- local development
- CI/CD automation
- container-based execution
- production-ready orchestration
- rolling updates
- zero downtime

To achieve this, we must define a deployment standard that fits all environments.

## Decision

PolyShop adopts a **container-first, Kubernetes-native deployment model** with the following layers:

---

# 1. Local Development (docker-compose)
`docker-compose.dev.yml` provides:
- Postgres (multiple DBs)
- Kafka + Zookeeper
- Redis
- MinIO (media)
- All services (auth, product, order, etc.)
- Gateway
- Prometheus + Grafana for local metrics

Helps new developers run the environment with:

```

docker compose -f docker-compose.dev.yml up

```

---

# 2. CI Build Strategy
Every service follows:

### **Two-stage Docker build**
1. **Builder stage**
   - For Java services: Maven or Gradle + JDK  
   - For Node services: npm install + build  
   - For Python services: pip install

2. **Runtime stage**
   - Java → distroless or Eclipse Temurin JRE  
   - Node → node:lts-slim  
   - Python → python:3-slim  

### **Tagging**
- `latest`
- `commit-sha`
- `service-version`

---

# 3. Deployment Target: Kubernetes
PolyShop uses Kubernetes (K8s) as the primary production runtime.

All manifests stored in:

```

/infra/k8s/base/
/infra/k8s/overlays/{dev,staging,prod}/

```

Each service includes:

### **Base Manifests**
- `Deployment.yaml`
- `Service.yaml`
- `ConfigMap.yaml`
- `Secret.yaml`
- `Ingress.yaml`
- `HorizontalPodAutoscaler.yaml`

### Required K8s features:
- readinessProbe
- livenessProbe
- resource requests/limits
- rollingUpdate strategy
- podAntiAffinity
- serviceAccount per service

---

# 4. GitOps With ArgoCD
PolyShop uses **ArgoCD** for continuous deployment.

Flow:

```

Github Push → CI builds image → ArgoCD detects change → Deploys to cluster

```

Benefits:
- declarative infra
- rollback versioning
- environment isolation

Argo config stored in:

```

/ci-cd/argo/

```

---

# 5. Canary & Blue/Green Rollouts
For high-risk services (Payment, Order, Gateway):

### Strategy:
- 5–10% traffic → new version  
- Compare metrics  
- Promote or rollback automatically  

Using **Argo Rollouts**:

```

/ci-cd/argo/rollouts/

```

---

# 6. Secrets & Config
Secrets come from:
- Kubernetes Secrets (non-production)
- External Secret Manager (AWS / GCP / Azure)

Config loading rules:
- Environment variables override ConfigMap values
- `.env` not used in production

---

# 7. Health Checks
Each service exposes `/health`.

If `/health` returns DOWN → kube kills and restarts pod.

---

# 8. Observability
All services emit:
- Metrics: Prometheus
- Logs: Loki
- Traces: Jaeger

Stored in:

```
/monitoring/
```

---

# Alternatives Considered

### 1. Docker Swarm
Rejected — limited ecosystem, weak scaling.

### 2. Serverless / Functions
Rejected — PolyShop has stateful workloads and long-running flows (Order Saga, Search indexing).

### 3. Nomad
Rejected — smaller community support.

---

# Consequences

### Positive
- Strong reproducibility
- Automatic rollbacks
- Easy scaling
- Full observability
- GitOps reduces errors
- Zero-downtime deployments

### Negative
- More complex initial setup
- Requires Kubernetes expertise
- CI/CD pipeline heavier

---

## Final Decision
PolyShop will use:
- Docker for builds
- Docker Compose for local development
- Kubernetes + ArgoCD for production
- GitOps and automated rollouts for all microservices

This ensures a resilient, scalable deployment environment suitable for PolyShop’s growth.
