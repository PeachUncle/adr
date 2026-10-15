# ADR-004: Quarkus Reference Application

**Status:** Accepted
**Date:** 2025-01-24
**Updated:** 2025-10-26 (Added VP framework compliance)
**Decision Makers:** Development Team, Application Architects
**Consulted:** End Users, Application Developers
**Informed:** Stakeholders

## Context and Problem Statement

Users deploying their own applications with validated-patterns-toolkit need practical examples showing:

1. **How to structure** a cloud-native application for OpenShift
2. **How to configure** Kubernetes resources (Deployments, Services, Routes)
3. **How to integrate** with GitOps and ArgoCD
4. **How to implement** health checks, metrics, and observability
5. **How to manage** secrets and configuration
6. **How to handle** resource limits and autoscaling
7. **How to deploy** using Validated Patterns

Rather than building a complex management tool, we provide a **simple, well-documented Quarkus application** that serves as a reference implementation demonstrating best practices for applications deployed via validated-patterns-toolkit.

## Decision Drivers

* **Educational Value**: Teach by example, not just documentation
* **Simplicity**: Simple enough to understand quickly
* **Practical**: Real working application, not just a toy
* **Best Practices**: Demonstrate production-ready patterns
* **Cloud-Native**: Show Kubernetes/OpenShift native features
* **Reusable**: Users can copy and adapt for their needs
* **Fast Startup**: Demonstrate Quarkus benefits (< 1s startup)
* **Low Resources**: Show efficient resource usage

## Considered Options

### Option 1: Spring Boot Reference Application
- Mature ecosystem, familiar to many developers
- **Rejected**: Slower startup (10-15s), higher memory usage (200-300MB)

### Option 2: Node.js/Express Reference Application
- Fast, lightweight, simple
- **Rejected**: Less relevant for enterprise Java shops, different ecosystem

### Option 3: Quarkus Reference Application (Selected)
- Supersonic subatomic Java (< 1s startup, < 100MB memory)
- Kubernetes-native with excellent OpenShift integration
- Modern Java with reactive capabilities
- **Selected**: Best demonstrates cloud-native Java patterns

### Option 4: Go Reference Application
- Very fast, small footprint
- **Rejected**: Different language ecosystem, less relevant for Java-focused patterns

## Decision Outcome

**Chosen option:** Option 3 - Quarkus Reference Application

### Purpose and Scope

This is **NOT** a management application for validated-patterns-toolkit. Instead, it's a **reference implementation** showing:

✅ **What it IS:**
- Example of a well-structured cloud-native application
- Reference for Kubernetes resource configuration
- Demonstration of GitOps integration patterns
- Template for health checks and observability
- Example of secrets management
- Starting point users can copy and customize

❌ **What it is NOT:**
- Management UI for deploying patterns
- Monitoring dashboard for pattern status
- Configuration management tool
- Required component of validated-patterns-toolkit

### Application Structure

```
quarkus-reference-app/
├── src/
│   ├── main/
│   │   ├── java/io/validatedpatterns/reference/
│   │   │   ├── api/
│   │   │   │   ├── HealthResource.java          # Health check endpoints
│   │   │   │   ├── MetricsResource.java         # Custom metrics
│   │   │   │   ├── ConfigResource.java          # Configuration examples
│   │   │   │   └── ExampleResource.java         # Sample REST API
│   │   │   ├── service/
│   │   │   │   ├── ExampleService.java          # Business logic
│   │   │   │   └── ConfigService.java           # Configuration handling
│   │   │   ├── model/
│   │   │   │   └── ExampleModel.java            # Data models
│   │   │   └── config/
│   │   │       └── ApplicationConfig.java       # App configuration
│   │   ├── resources/
│   │   │   ├── application.properties           # Quarkus configuration
│   │   │   ├── application-dev.properties       # Dev profile
│   │   │   ├── application-prod.properties      # Production profile
│   │   │   └── META-INF/resources/
│   │   │       └── index.html                   # Simple UI
│   │   └── docker/
│   │       ├── Dockerfile.jvm                   # JVM mode
│   │       └── Dockerfile.native                # Native mode
│   └── test/
│       └── java/io/validatedpatterns/reference/
│           ├── api/
│           └── service/
├── charts/                                      # Helm charts (VP framework)
│   └── all/
│       └── quarkus-reference-app/               # Application Helm chart
│           ├── Chart.yaml                       # Chart metadata
│           ├── values.yaml                      # Default values
│           ├── .helmignore                      # Helm ignore patterns
│           └── templates/
│               ├── _helpers.tpl                 # Template helpers
│               ├── NOTES.txt                    # Post-install notes
│               ├── namespace.yaml               # Namespace (Wave -1)
│               ├── configmap.yaml               # ConfigMap (Wave 0)
│               ├── serviceaccount.yaml          # ServiceAccount (Wave 0)
│               ├── role.yaml                    # Role (Wave 1)
│               ├── rolebinding.yaml             # RoleBinding (Wave 1)
│               ├── deployment.yaml              # Deployment (Wave 2)
│               ├── service.yaml                 # Service (Wave 3)
│               └── route.yaml                   # Route (Wave 3)
├── values-global.yaml                           # Global pattern config
├── values-hub.yaml                              # Hub cluster config
├── values-dev.yaml                              # Dev environment overrides
├── values-prod.yaml                             # Prod environment overrides
├── values-secrets.yaml.template                 # Secrets template
├── k8s/                                         # Legacy Kubernetes manifests
│   ├── base/
│   │   ├── deployment.yaml                      # Deployment config
│   │   ├── service.yaml                         # Service config
│   │   ├── route.yaml                           # OpenShift Route
│   │   ├── configmap.yaml                       # Configuration
│   │   ├── secret.yaml                          # Secrets (template)
│   │   ├── serviceaccount.yaml                  # Service account
│   │   ├── role.yaml                            # RBAC role
│   │   ├── rolebinding.yaml                     # RBAC binding
│   │   └── kustomization.yaml                   # Kustomize base
│   └── overlays/
│       ├── dev/
│       │   └── kustomization.yaml               # Dev environment
│       └── prod/
│           └── kustomization.yaml               # Production environment
├── gitops/                                      # GitOps integration
│   ├── application.yaml                         # ArgoCD Application
│   └── values.yaml                              # Helm values (if using Helm)
├── tekton/                                      # CI/CD pipelines
│   ├── pipeline.yaml                            # Build pipeline
│   ├── task-build.yaml                          # Build task
│   ├── task-test.yaml                           # Test task
│   └── task-deploy.yaml                         # Deploy task
├── pom.xml                                      # Maven configuration
├── VALUES-README.md                             # Values files guide
└── README.md                                    # Comprehensive guide
```

### Validated Patterns Framework Compliance

**Status:** ✅ COMPLIANT (as of 2025-10-26)

The Quarkus Reference Application has been restructured to fully comply with the Validated Patterns (VP) framework requirements. This section documents the VP-specific structure and integration.

#### 4 Values Files Pattern

The VP framework requires exactly 4 values files for proper pattern deployment:

1. **values-global.yaml** - Global configuration shared across all clusters
   - Application name and namespace
   - Default replica count (2)
   - Container image configuration
   - Resource limits (128Mi-256Mi)
   - Service and route configuration
   - RBAC settings
   - Health check configuration
   - ArgoCD sync wave definitions
   - Common labels and annotations

2. **values-hub.yaml** - Hub cluster configuration
   - `clusterGroup` configuration for clustergroup chart integration
   - Namespaces to create (`quarkus-dev`)
   - Applications to deploy via ArgoCD
   - Hub-specific resource overrides
   - ArgoCD RBAC configuration
   - Monitoring and backup settings

3. **values-dev.yaml** - Development environment overrides
   - Single replica for development
   - Reduced resources (64Mi-128Mi)
   - Latest image tag (always pull)
   - Relaxed health checks
   - Development profile settings

4. **values-prod.yaml** - Production environment overrides
   - High availability (3 replicas)
   - Production resources (256Mi-512Mi)
   - Pinned image version (v1.0.0)
   - Strict health checks
   - Monitoring and alerting enabled
   - Backup configuration
   - Autoscaling enabled

**Additional:**
- **values-secrets.yaml.template** - Template for sensitive data (NEVER committed to Git)

#### Helm Chart Structure

The application is packaged as a Helm chart following VP conventions:

```yaml
# charts/all/quarkus-reference-app/Chart.yaml
apiVersion: v2
name: quarkus-reference-app
description: Quarkus Reference Application for Validated Patterns
type: application
version: 1.0.0
appVersion: "1.0"
keywords:
  - validated-patterns
  - quarkus
  - reference
  - openshift
annotations:
  validatedPatterns.io/pattern: "true"
  validatedPatterns.io/category: "reference"
  openshift.io/display-name: "Quarkus Reference Application"
```

#### ArgoCD Sync Waves

All Kubernetes resources include ArgoCD sync wave annotations to ensure proper deployment ordering:

| Resource | Wave | Purpose |
|----------|------|---------|
| Namespace | -1 | Infrastructure (created first) |
| ConfigMap | 0 | Configuration (before workloads) |
| ServiceAccount | 0 | Configuration (before workloads) |
| Role | 1 | RBAC (before workloads) |
| RoleBinding | 1 | RBAC (before workloads) |
| Deployment | 2 | Workloads (after RBAC) |
| Service | 3 | Networking (after workloads) |
| Route | 3 | Networking (after workloads) |

**Deployment Order:**
```
Wave -1: Namespace created
  ↓
Wave 0: ConfigMap, ServiceAccount created
  ↓
Wave 1: Role, RoleBinding created
  ↓
Wave 2: Deployment created (pods start)
  ↓
Wave 3: Service, Route created (traffic flows)
```

#### clustergroup Chart Integration

The application integrates with the VP framework's clustergroup chart via `values-hub.yaml`:

```yaml
# values-hub.yaml
clusterGroup:
  name: hub
  isHubCluster: true

  # Namespaces managed by clustergroup
  namespaces:
    - quarkus-dev

  # Applications deployed via ArgoCD
  applications:
    quarkus-reference-app:
      name: quarkus-reference-app
      namespace: quarkus-dev
      project: default
      path: quarkus-reference-app/charts/all/quarkus-reference-app
      repoURL: https://github.com/validated-patterns/validated-patterns-ansible-toolkit.git
      targetRevision: main
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=false  # Namespace created by clustergroup
```

**Integration Flow:**
1. clustergroup chart creates namespace (Wave -1)
2. clustergroup chart deploys ArgoCD Application
3. ArgoCD syncs the Quarkus Helm chart
4. Helm chart deploys resources in sync wave order

#### Self-Contained Pattern Principles

The application follows VP self-contained pattern principles:

✅ **Namespace Management**
- Namespace defined in Helm chart
- Created by clustergroup chart (Wave -1)
- No external namespace dependencies

✅ **Resource Ordering**
- Sync waves ensure proper ordering
- Infrastructure → Configuration → RBAC → Workloads → Networking
- Idempotent deployment

✅ **Configuration Management**
- 4 values files for different contexts
- Secrets managed separately (not in Git)
- Environment-specific overrides

✅ **GitOps Integration**
- Deployed via ArgoCD
- Automated sync with prune and self-heal
- Declarative configuration

#### Values File Hierarchy

Values files are applied in order, with later files overriding earlier ones:

```
values-global.yaml          (Base configuration)
  ↓
values-hub.yaml            (Hub cluster overrides)
  ↓
values-{env}.yaml          (Environment overrides: dev, prod)
  ↓
values-secrets.yaml        (Secrets - highest priority)
```

**Example Configuration Comparison:**

| Setting | Global | Dev | Prod |
|---------|--------|-----|------|
| Replicas | 2 | 1 | 3 |
| Memory Request | 128Mi | 64Mi | 256Mi |
| Memory Limit | 256Mi | 128Mi | 512Mi |
| CPU Request | 100m | 50m | 200m |
| CPU Limit | 500m | 250m | 1000m |
| Image Tag | latest | latest | v1.0.0 |
| Pull Policy | Always | Always | IfNotPresent |
| Profile | prod | dev | prod |
| Monitoring | true | false | true |
| Autoscaling | false | false | true |

### Key Features to Demonstrate

#### 1. Health Checks and Readiness

```java
@Path("/health")
public class HealthResource {

    @GET
    @Path("/live")
    @Produces(MediaType.APPLICATION_JSON)
    public Response liveness() {
        // Liveness probe - is the app running?
        return Response.ok()
            .entity(Map.of("status", "UP", "checks", List.of()))
            .build();
    }

    @GET
    @Path("/ready")
    @Produces(MediaType.APPLICATION_JSON)
    public Response readiness() {
        // Readiness probe - can the app serve traffic?
        boolean ready = checkDependencies();
        return ready ? Response.ok() : Response.status(503);
    }
}
```

#### 2. Configuration Management

```properties
# application.properties - Shows best practices

# Application info
quarkus.application.name=validated-patterns-reference
quarkus.application.version=1.0.0

# HTTP configuration
quarkus.http.port=8080
quarkus.http.host=0.0.0.0

# Health checks
quarkus.smallrye-health.root-path=/health

# Metrics
quarkus.micrometer.enabled=true
quarkus.micrometer.export.prometheus.enabled=true

# Logging
quarkus.log.level=INFO
quarkus.log.console.format=%d{HH:mm:ss} %-5p [%c{2.}] (%t) %s%e%n

# OpenShift integration
quarkus.kubernetes.deployment-target=openshift
quarkus.openshift.route.expose=true
```

#### 3. Kubernetes Resource Configuration

```yaml
# k8s/base/deployment.yaml - Reference implementation
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reference-app
  labels:
    app: reference-app
    app.kubernetes.io/name: reference-app
    app.kubernetes.io/part-of: validated-patterns
spec:
  replicas: 2
  selector:
    matchLabels:
      app: reference-app
  template:
    metadata:
      labels:
        app: reference-app
    spec:
      serviceAccountName: reference-app
      containers:
      - name: reference-app
        image: quay.io/validated-patterns/reference-app:latest
        ports:
        - containerPort: 8080
          name: http
          protocol: TCP
        env:
        - name: QUARKUS_PROFILE
          value: "prod"
        - name: APP_CONFIG
          valueFrom:
            configMapKeyRef:
              name: reference-app-config
              key: app.config
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          capabilities:
            drop:
            - ALL
```

#### 4. GitOps Integration

**Legacy Kustomize Approach:**
```yaml
# gitops/application.yaml - ArgoCD Application (Legacy)
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: reference-app
  namespace: openshift-gitops
spec:
  project: default
  source:
    repoURL: https://github.com/validated-patterns/reference-app.git
    targetRevision: main
    path: k8s/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: reference-app
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

**VP Framework Approach (Recommended):**
```yaml
# values-hub.yaml - Integrated with clustergroup chart
clusterGroup:
  name: hub
  isHubCluster: true

  namespaces:
    - quarkus-dev

  applications:
    quarkus-reference-app:
      name: quarkus-reference-app
      namespace: quarkus-dev
      project: default
      path: quarkus-reference-app/charts/all/quarkus-reference-app
      repoURL: https://github.com/validated-patterns/validated-patterns-ansible-toolkit.git
      targetRevision: main
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=false  # Managed by clustergroup
```

**Deployment via clustergroup chart:**
```bash
# The clustergroup chart automatically creates the ArgoCD Application
# No manual application.yaml needed
helm install hub-cluster \
  validated-patterns/clustergroup \
  -f values-global.yaml \
  -f values-hub.yaml \
  -n openshift-gitops
```

### Deployment Instructions

#### Option 1: Helm Deployment (Recommended for VP Framework)

**Development Environment:**
```bash
# Deploy with dev values
helm install quarkus-reference-app \
  ./charts/all/quarkus-reference-app \
  -f values-dev.yaml \
  -n quarkus-dev \
  --create-namespace

# Verify deployment
kubectl get pods -n quarkus-dev
kubectl get route -n quarkus-dev
```

**Production Environment:**
```bash
# Deploy with prod values and secrets
helm install quarkus-reference-app \
  ./charts/all/quarkus-reference-app \
  -f values-prod.yaml \
  -f values-secrets.yaml \
  -n quarkus-prod \
  --create-namespace

# Verify deployment
kubectl get pods -n quarkus-prod
kubectl get route -n quarkus-prod
```

**Hub Cluster (via clustergroup chart):**
```bash
# Deploy the entire pattern including the reference app
helm install hub-cluster \
  validated-patterns/clustergroup \
  -f values-global.yaml \
  -f values-hub.yaml \
  -n openshift-gitops

# The clustergroup chart will:
# 1. Create the quarkus-dev namespace
# 2. Deploy the ArgoCD Application
# 3. ArgoCD will sync the Helm chart
# 4. Resources deploy in sync wave order
```

**Dry Run (Test Configuration):**
```bash
# Render templates without deploying
helm template test-release \
  ./charts/all/quarkus-reference-app \
  -f values-dev.yaml

# Validate chart
helm lint ./charts/all/quarkus-reference-app
```

#### Option 2: Kustomize Deployment (Legacy)

**Development Environment:**
```bash
# Deploy using Kustomize
oc apply -k k8s/overlays/dev

# Verify deployment
oc get pods -n reference-app
oc get route -n reference-app
```

**Production Environment:**
```bash
# Deploy using Kustomize
oc apply -k k8s/overlays/prod

# Verify deployment
oc get pods -n reference-app
oc get route -n reference-app
```

#### Option 3: ArgoCD Application (GitOps)

**Create ArgoCD Application:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: quarkus-reference-app
  namespace: openshift-gitops
spec:
  project: default
  source:
    repoURL: https://github.com/validated-patterns/validated-patterns-ansible-toolkit.git
    targetRevision: main
    path: quarkus-reference-app/charts/all/quarkus-reference-app
    helm:
      valueFiles:
        - ../../../values-global.yaml
        - ../../../values-dev.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: quarkus-dev
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

**Apply the Application:**
```bash
oc apply -f gitops/application.yaml

# Watch sync progress
argocd app get quarkus-reference-app
argocd app sync quarkus-reference-app --watch
```

#### Verification Steps

**Check Sync Waves:**
```bash
# View resources in sync wave order
kubectl get all -n quarkus-dev \
  -o jsonpath='{range .items[*]}{.kind}{"\t"}{.metadata.name}{"\t"}{.metadata.annotations.argocd\.argoproj\.io/sync-wave}{"\n"}{end}' \
  | sort -k3 -n
```

**Check Health:**
```bash
# Check pod health
kubectl get pods -n quarkus-dev

# Check health endpoints
ROUTE=$(kubectl get route reference-app -n quarkus-dev -o jsonpath='{.spec.host}')
curl https://$ROUTE/health/live
curl https://$ROUTE/health/ready
```

**Check Logs:**
```bash
# View application logs
kubectl logs -n quarkus-dev -l app=reference-app -f
```

### Documentation Structure

The reference application includes comprehensive documentation:

```
quarkus-reference-app/
├── README.md                          # Overview and quick start
├── VALUES-README.md                   # Values files guide
├── docs/
│   ├── ARCHITECTURE.md                # Architecture decisions
│   ├── CONFIGURATION.md               # Configuration guide
│   ├── DEPLOYMENT.md                  # Deployment instructions
│   ├── DEVELOPMENT.md                 # Development guide
│   ├── PHASE1-SYNC-WAVES-COMPLETE.md  # Phase 1 completion report
│   ├── PHASE2-HELM-CHART-COMPLETE.md  # Phase 2 completion report
│   ├── PHASE3-VALUES-FILES-COMPLETE.md # Phase 3 completion report
│   └── TROUBLESHOOTING.md             # Common issues
```

### README.md Template

```markdown
# Validated Patterns Reference Application

A simple Quarkus application demonstrating best practices for applications
deployed with validated-patterns-toolkit.

## Purpose

This is a **reference implementation** showing:
- Cloud-native application structure
- Kubernetes resource configuration
- GitOps integration patterns
- Health checks and observability
- Secrets management
- Resource management

## Quick Start

```bash
# Build
./mvnw clean package

# Run locally
./mvnw quarkus:dev

# Build container
podman build -f src/main/docker/Dockerfile.jvm -t reference-app:latest .

# Deploy to OpenShift (Helm - Recommended)
helm install quarkus-reference-app \
  ./charts/all/quarkus-reference-app \
  -f values-dev.yaml \
  -n quarkus-dev \
  --create-namespace

# Deploy to OpenShift (Kustomize - Legacy)
oc apply -k k8s/overlays/dev
```

## What You Can Learn

- ✅ Quarkus application structure
- ✅ REST API best practices
- ✅ Health check implementation
- ✅ Metrics and monitoring
- ✅ Configuration management
- ✅ Kubernetes manifests
- ✅ **Validated Patterns framework compliance**
- ✅ **Helm chart structure and templating**
- ✅ **4 values files pattern**
- ✅ **ArgoCD sync waves**
- ✅ **clustergroup chart integration**
- ✅ GitOps integration
- ✅ CI/CD with Tekton
- ✅ Security best practices

## Customization

Copy this application and customize for your needs:
1. Rename packages and classes
2. Update Kubernetes manifests
3. Modify GitOps configuration
4. Add your business logic
5. Deploy with validated-patterns-toolkit

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Configuration](docs/CONFIGURATION.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Development](docs/DEVELOPMENT.md)

## Not a Management Tool

This is NOT a management application for validated-patterns-toolkit.
It's a reference showing how YOUR applications should be structured.
```

## Consequences

### Positive

* **Educational**: Users learn by example
* **Practical**: Real working code, not just documentation
* **Reusable**: Easy to copy and customize
* **Best Practices**: Demonstrates production patterns
* **Low Maintenance**: Simple application, easy to maintain
* **Fast**: Quarkus provides excellent startup and runtime performance
* **Clear Scope**: Not trying to be a management tool
* **VP Compliant**: Fully compliant with Validated Patterns framework
* **Helm-Based**: Modern deployment using Helm charts
* **Multi-Environment**: Supports dev, prod, and custom environments
* **GitOps Ready**: Integrates seamlessly with ArgoCD
* **Sync Waves**: Demonstrates proper resource ordering

### Negative

* **Limited Scope**: Doesn't provide management capabilities
* **Java-Focused**: May not be relevant for non-Java users
* **Maintenance**: Still needs updates as best practices evolve
* **Complexity**: VP framework adds structure (but improves consistency)

### Neutral

* **Optional**: Users can ignore if not relevant
* **Extensible**: Users can extend for their needs
* **Dual Structure**: Maintains both Helm and Kustomize for transition period

## Implementation Plan

### Phase 1: Basic Application ✅ COMPLETE
- [x] Create Quarkus project structure
- [x] Implement basic REST API
- [x] Add health checks
- [x] Add configuration examples
- [x] Write comprehensive README

### Phase 2: Kubernetes Integration ✅ COMPLETE
- [x] Create Kubernetes manifests
- [x] Add Kustomize overlays
- [x] Implement RBAC examples
- [x] Add resource limits examples
- [x] Document deployment process
- [x] Add ArgoCD sync wave annotations

### Phase 3: GitOps Integration ✅ COMPLETE
- [x] Create ArgoCD Application manifest
- [x] Add Helm chart
- [x] Document GitOps workflow
- [x] Add sync policies examples

### Phase 4: CI/CD ✅ COMPLETE
- [x] Create Tekton pipelines
- [x] Add build tasks
- [x] Add test tasks
- [x] Add deployment tasks
- [x] Document CI/CD process

### Phase 5: Documentation ✅ COMPLETE
- [x] Write architecture guide
- [x] Write configuration guide
- [x] Write deployment guide
- [x] Write development guide
- [x] Write troubleshooting guide

### Phase 6: VP Framework Compliance ✅ COMPLETE (2025-10-26)
- [x] Create Helm chart structure
- [x] Add sync wave annotations to all resources
- [x] Create values-global.yaml
- [x] Create values-hub.yaml
- [x] Create values-dev.yaml
- [x] Create values-prod.yaml
- [x] Create values-secrets.yaml.template
- [x] Integrate with clustergroup chart
- [x] Document VP framework compliance
- [x] Create VALUES-README.md
- [x] Update ADR-004 with VP details

## Success Criteria

### Application Performance ✅
* ✅ Application starts in < 1 second
* ✅ Memory usage < 100MB
* ✅ All health checks working
* ✅ Metrics exposed

### Deployment ✅
* ✅ Deploys successfully to OpenShift
* ✅ GitOps sync working
* ✅ Helm deployment working
* ✅ Kustomize deployment working (legacy)

### Documentation ✅
* ✅ Comprehensive documentation
* ✅ Users can easily copy and customize
* ✅ VP framework compliance documented
* ✅ Values files documented

### VP Framework Compliance ✅
* ✅ 4 values files created (global, hub, dev, prod)
* ✅ Helm chart structure implemented
* ✅ Sync wave annotations on all resources
* ✅ clustergroup chart integration
* ✅ Self-contained pattern principles
* ✅ Namespace management via clustergroup
* ✅ Secrets template provided
* ✅ Multi-environment support

## VP Framework Compliance Checklist

### MUST Requirements ✅

- [x] **Use clustergroup chart for deployment**
  - values-hub.yaml integrates with clustergroup
  - Applications defined in clusterGroup.applications
  - Namespaces managed by clustergroup

- [x] **Eventual consistency (idempotent)**
  - Helm charts are idempotent
  - ArgoCD sync with prune and self-heal
  - Resources can be reapplied safely

- [x] **No secrets in Git**
  - values-secrets.yaml in .gitignore
  - values-secrets.yaml.template provided
  - Secrets documented but not committed

- [x] **BYO cluster support**
  - No cluster-specific dependencies
  - Works on any OpenShift cluster
  - Configurable via values files

### SHOULD Requirements ✅

- [x] **Declarative execution**
  - All resources defined declaratively
  - Deployed via GitOps (ArgoCD)
  - No imperative commands required

- [x] **Modular design**
  - Helm chart is self-contained
  - Values files for different contexts
  - Easy to customize and extend

- [x] **Sync wave ordering**
  - All resources have sync-wave annotations
  - Proper deployment order enforced
  - Infrastructure → Config → RBAC → Workloads → Networking

- [x] **Multi-environment support**
  - values-dev.yaml for development
  - values-prod.yaml for production
  - Easy to add custom environments

### CAN Requirements ✅

- [x] **Helm-based deployment**
  - Full Helm chart implementation
  - Template helpers for reusability
  - Values-based configuration

- [x] **Monitoring integration**
  - Metrics exposed via Prometheus
  - Health checks implemented
  - Monitoring configurable via values

- [x] **Backup configuration**
  - Backup settings in values-prod.yaml
  - Configurable backup schedules
  - Optional feature (disabled by default)

- [x] **Autoscaling**
  - HPA configuration in values-prod.yaml
  - Configurable min/max replicas
  - Optional feature (disabled by default)

## References

### Application Framework
* [Quarkus](https://quarkus.io/)
* [Quarkus on OpenShift](https://quarkus.io/guides/deploying-to-openshift)
* [Quarkus Kubernetes Extension](https://quarkus.io/guides/deploying-to-kubernetes)

### Kubernetes & OpenShift
* [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
* [OpenShift Documentation](https://docs.openshift.com/)
* [Helm Documentation](https://helm.sh/docs/)

### GitOps & ArgoCD
* [ArgoCD](https://argo-cd.readthedocs.io/)
* [ArgoCD Sync Waves](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/)
* [GitOps Principles](https://opengitops.dev/)

### Validated Patterns
* [Validated Patterns](https://validatedpatterns.io/)
* [Validated Patterns Documentation](https://validatedpatterns.io/learn/)
* [clustergroup Chart](https://github.com/validatedpatterns/common/tree/main/clustergroup)
* [Pattern Structure](https://validatedpatterns.io/learn/structure/)

### Project Documentation
* [Refactoring Plan](../REFACTORING-PLAN-QUARKUS-APP.md)
* [Phase 1 Report](../../quarkus-reference-app/docs/PHASE1-SYNC-WAVES-COMPLETE.md)
* [Phase 2 Report](../../quarkus-reference-app/docs/PHASE2-HELM-CHART-COMPLETE.md)
* [Phase 3 Report](../../quarkus-reference-app/docs/PHASE3-VALUES-FILES-COMPLETE.md)
* [Values Files Guide](../../quarkus-reference-app/VALUES-README.md)

## Related ADRs

* [ADR-001: Project Vision and Scope](ADR-001-project-vision-and-scope.md)
* [ADR-002: Ansible Role Architecture](ADR-002-ansible-role-architecture.md)
* [ADR-003: Validation Framework](ADR-003-validation-framework.md)
* [ADR-010: OpenShift GitOps Operator](ADR-010-openshift-gitops-operator.md)
* [ADR-011: Helm Installation](ADR-011-helm-installation.md)
* [ADR-012: Validated Patterns Common Framework](ADR-012-validated-patterns-common-framework.md)
* [ADR-013: Validated Patterns Deployment Strategy](ADR-013-validated-patterns-deployment-strategy.md)
* [ADR-RESEARCH-IMPACT-ANALYSIS](ADR-RESEARCH-IMPACT-ANALYSIS.md)

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-01-24 | 1.0 | Initial ADR | Development Team |
| 2025-01-24 | 1.1 | Reframed as reference implementation | Development Team |
| 2025-10-26 | 2.0 | Added VP framework compliance | Development Team |

**Version 2.0 Changes:**
- Added "Validated Patterns Framework Compliance" section
- Documented 4 values files pattern
- Documented Helm chart structure
- Documented ArgoCD sync waves
- Documented clustergroup chart integration
- Added deployment instructions for Helm
- Updated application structure to include charts/
- Added VP Framework Compliance Checklist
- Updated success criteria
- Updated implementation plan with Phase 6
- Added comprehensive references
- Status changed from "Proposed" to "Accepted"
