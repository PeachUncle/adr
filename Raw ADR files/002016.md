# ADR-005: Infrastructure & Deployment Strategy

**Date:** 2025-11-15  
**Status:** Accepted  
**Deciders:** Agent Backend, Agent Blockchain  
**Technical Story:** Phase 0.4 - Infrastructure Setup  
**Relates to:** ADR-001 (Tech Stack), ADR-003 (CI/CD)  
**Revision:** 2 (Added multi-cloud strategy, security architecture, disaster recovery details, blockchain node requirements)

---

## Context and Problem Statement

Ghost Protocol requires a scalable, secure, and cost-effective infrastructure strategy that supports:
- Multi-environment deployment (development, staging, production)
- Scalable microservices architecture (API Gateway, Indexer, RPC Orchestrator, AI Engine)
- Blockchain node deployment and orchestration
- High availability and disaster recovery
- Observability (monitoring, logging, alerting)
- Security and compliance (secrets management, network isolation)

**Question:** What infrastructure stack, deployment strategy, and cloud provider should we use for Ghost Protocol?

## Decision Drivers

- **Scalability:** Support 100K+ users, 1M+ transactions/day
- **Reliability:** 99.9% uptime SLA, auto-healing, disaster recovery
- **Cost Optimization:** Minimize cloud spend during development, predictable production costs
- **Security:** Network isolation, secrets management, compliance (SOC 2, GDPR)
- **Developer Experience:** Easy local development, fast deployment cycles
- **Multi-Cloud:** Avoid vendor lock-in, support multiple cloud providers
- **Observability:** Complete visibility into system health and performance
- **Compliance:** GDPR, SOC 2, audit trails

## Considered Options

### Cloud Provider Options

1. **AWS (Amazon Web Services)**
2. **GCP (Google Cloud Platform)**
3. **Azure (Microsoft Azure)**
4. **Multi-Cloud (Hybrid approach)**
5. **Self-Hosted (On-premise)**

### Orchestration Options

1. **Kubernetes (EKS/GKE/AKS)**
2. **AWS ECS/Fargate**
3. **Google Cloud Run**
4. **Docker Swarm**

### Infrastructure as Code Options

1. **Terraform**
2. **Pulumi**
3. **AWS CloudFormation**
4. **Ansible**

### Monitoring Stack Options

1. **Prometheus + Grafana + Loki**
2. **Datadog**
3. **New Relic**
4. **ELK Stack (Elasticsearch, Logstash, Kibana)**

## Decision Outcome

**Chosen stack:**

### Cloud Provider: AWS (Primary) with Multi-Cloud Abstraction Strategy
- **Primary:** AWS for production (mature ecosystem, proven at scale)
- **Multi-Cloud Path:** Abstraction layers for future portability (see Multi-Cloud Strategy below)
- **Cost:** Start with AWS Free Tier, optimize with Reserved Instances

**Justification:**
- AWS has most mature ecosystem for blockchain workloads
- Best support for Kubernetes (EKS), RDS PostgreSQL
- Kubernetes provides compute-layer portability across clouds
- Lowest cost for development phase (generous free tier)
- Dragonfly (opensource Redis alternative) self-hosted on Kubernetes reduces vendor lock-in

**Multi-Cloud Abstraction Strategy:**

**Layer 1: Compute (Kubernetes - Fully Portable)**
- All application workloads run on Kubernetes
- Kubernetes manifest are cloud-agnostic (works on EKS/GKE/AKS)
- Use Helm charts for package management
- **Migration Path:** Change cluster endpoint, re-apply manifests

**Layer 2: Data Services (Provider-Specific Modules)**
```
Terraform Module Structure:
infra/terraform/modules/
├── database/
│   ├── aws/         # RDS PostgreSQL module
│   ├── gcp/         # Cloud SQL PostgreSQL module (future)
│   └── azure/       # Azure PostgreSQL module (future)
├── cache/
│   ├── kubernetes/  # Dragonfly deployed on Kubernetes (portable, opensource)
│   ├── aws/         # ElastiCache Redis module (alternative, legacy)
│   ├── gcp/         # Memorystore Redis module (alternative, future)
│   └── azure/       # Azure Cache for Redis module (alternative, future)
└── storage/
    ├── aws/         # S3 module
    ├── gcp/         # GCS module (future)
    └── azure/       # Blob Storage module (future)
```

**Layer 3: Data Portability**
- **Database:** PostgreSQL (standard SQL, portable via pg_dump/pg_restore)
- **Cache:** Dragonfly (Kubernetes-native, portable across clouds) with Redis protocol compatibility
- **Event Indexing:** DuckDB or LMDB (embedded, portable)
- **Storage:** IPFS (decentralized, censorship-resistant) + S3-compatible API (MinIO gateway for cross-cloud sync)

**Migration Strategy (AWS → GCP/Azure):**
1. Provision equivalent services on target cloud (Terraform modules)
2. Setup cross-cloud VPN for data sync
3. Replicate PostgreSQL via logical replication
4. Sync S3 to GCS/Blob via rclone
5. Cutover DNS to new cloud
6. Decommission AWS resources

**Provider Boundaries (Explicit):**
- **Kubernetes Workloads:** Cloud-agnostic (100% portable)
- **Managed Databases:** Provider-specific, data portable via standard protocols
- **Secrets Management:** Provider-specific initially, migrate to Vault for multi-cloud
- **Monitoring:** Self-hosted on Kubernetes (100% portable)

**Trade-off Acknowledgment:**
- **Benefit:** Kubernetes workloads portable, exit strategy exists
- **Cost:** Managed services (RDS, ElastiCache) are provider-specific, require migration effort
- **Mitigation:** Use standard protocols (PostgreSQL, Redis) for data portability

---

### Orchestration: Kubernetes (EKS)
- **Development:** Docker Compose (local), Minikube (optional)
- **Staging:** EKS (managed Kubernetes)
- **Production:** EKS with multi-AZ deployment

**Justification:**
- Industry standard for microservices orchestration
- Declarative configuration (GitOps-ready)
- Auto-scaling, self-healing, rolling updates
- Portable across cloud providers (multi-cloud ready)

---

### Infrastructure as Code: Terraform
- **Modules:** VPC, Compute, Database, Storage, Networking
- **Environments:** Separate workspaces (dev, staging, prod)
- **State:** Remote state in S3 + DynamoDB locking

**Justification:**
- Declarative, cloud-agnostic
- Mature ecosystem, extensive provider support
- State management and change planning
- Team collaboration via remote state

---

### Monitoring Stack: Prometheus + Grafana + Loki + OpenTelemetry
- **Metrics:** Prometheus (time-series database)
- **Visualization:** Grafana dashboards
- **Logs:** Loki (log aggregation)
- **Distributed Tracing:** OpenTelemetry + Jaeger/Tempo
- **Alerts:** AlertManager + PagerDuty integration

**Justification:**
- Open-source, self-hosted (cost-effective)
- Kubernetes-native (service discovery, auto-scaling)
- Rich ecosystem (exporters, dashboards)
- OpenTelemetry provides distributed tracing for microservices
- No vendor lock-in

**Tracing Strategy:**
- **OpenTelemetry SDK:** Instrument all backend services (NestJS, Go)
- **Trace Backend:** Jaeger (development) → Grafana Tempo (production)
- **Sampling:** 100% in dev, 10% in production (reduce cost)
- **Context Propagation:** W3C Trace Context headers across services

---

### Security Architecture

**Network Topology:**
```
┌─────────────────── AWS VPC (10.0.0.0/16) ──────────────────────┐
│                                                                 │
│  ┌────────── Public Subnets (DMZ) ─────────┐                  │
│  │  10.0.1.0/24 (AZ-a)                      │                  │
│  │  10.0.2.0/24 (AZ-b)                      │                  │
│  │  10.0.3.0/24 (AZ-c)                      │                  │
│  │                                          │                  │
│  │  - ALB (Application Load Balancer)      │                  │
│  │  - NAT Gateways (egress only)           │                  │
│  │  - Bastion Host (jump box, optional)    │                  │
│  └──────────────────────────────────────────┘                  │
│               │                                                 │
│               ▼                                                 │
│  ┌───────── Private Subnets (Application) ─┐                  │
│  │  10.0.11.0/24 (AZ-a)                     │                  │
│  │  10.0.12.0/24 (AZ-b)                     │                  │
│  │  10.0.13.0/24 (AZ-c)                     │                  │
│  │                                          │                  │
│  │  - EKS Worker Nodes                      │                  │
│  │  - No public IPs                         │                  │
│  │  - Security Groups: Allow only ALB       │                  │
│  └──────────────────────────────────────────┘                  │
│               │                                                 │
│               ▼                                                 │
│  ┌───────── Private Subnets (Data) ─────────┐                 │
│  │  10.0.21.0/24 (AZ-a)                     │                  │
│  │  10.0.22.0/24 (AZ-b)                     │                  │
│  │  10.0.23.0/24 (AZ-c)                     │                  │
│  │                                          │                  │
│  │  - RDS PostgreSQL (Multi-AZ)             │                  │
│  │  - Dragonfly (on Kubernetes, Multi-AZ)   │                  │
│  │  - DuckDB/LMDB (Event Indexing)          │                  │
│  │  - Security Groups: Allow only EKS nodes │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**IAM & RBAC Strategy:**

**AWS IAM (Infrastructure Level):**
```yaml
IAM Roles:
  - eks-cluster-role:
      Principal: EKS service
      Policies: AmazonEKSClusterPolicy
  
  - eks-node-role:
      Principal: EC2 instances (worker nodes)
      Policies: AmazonEKSWorkerNodePolicy, AmazonEC2ContainerRegistryReadOnly
  
  - eks-pod-role (IRSA - IAM Roles for Service Accounts):
      - api-gateway-role:
          Permissions: RDS connect, Secrets Manager read, S3 read/write
      - indexer-role:
          Permissions: RDS write, S3 write
      - rpc-orchestrator-role:
          Permissions: EC2 describe (node management)

IAM Users:
  - admin-user:
      MFA: Required
      Permissions: Full access (break-glass only)
  
  - developer-user:
      MFA: Required
      Permissions: Read-only (kubectl get, logs)

IAM Policies:
  - Least Privilege: Each role has minimum required permissions
  - Explicit Deny: Deny destructive actions by default
  - Time-Based: Temporary credentials via STS (15-60 min sessions)
```

**Kubernetes RBAC (Application Level):**
```yaml
ClusterRoles:
  - cluster-admin:
      Subjects: admin-user (break-glass only)
      Permissions: Full cluster access
  
  - developer:
      Subjects: developer-user
      Permissions: Read-only (get, list, watch)
  
  - ci-cd-deployer:
      Subjects: github-actions-service-account
      Permissions: Create, update deployments, configmaps, secrets

Namespaces:
  - production:
      NetworkPolicy: Deny all by default, allow specific
      PodSecurityPolicy: Restricted
  
  - staging:
      NetworkPolicy: Less restrictive
      PodSecurityPolicy: Baseline

ServiceAccounts:
  - api-gateway-sa:
      Namespace: production
      IRSA: api-gateway-role
  
  - indexer-sa:
      Namespace: production
      IRSA: indexer-role
```

**Encryption Strategy:**

**Encryption at Rest:**
```yaml
RDS PostgreSQL:
  - KMS encryption: Enabled (aws/rds key)
  - Storage: Encrypted volumes
  - Backups: Encrypted snapshots

ElastiCache Redis:
  - KMS encryption: Enabled (aws/elasticache key)
  - At-rest encryption: Enabled

S3 Buckets:
  - Server-side encryption: SSE-KMS (custom CMK)
  - Versioning: Enabled
  - Bucket keys: Enabled (reduce KMS API calls)

EKS etcd:
  - KMS encryption: Enabled (secrets at rest)
  - Custom CMK: aws/eks-etcd key

EBS Volumes (Worker Nodes):
  - KMS encryption: Enabled (aws/ebs key)
  - All volumes encrypted by default
```

**Encryption in Transit:**
```yaml
External Traffic:
  - TLS 1.3 minimum (ALB)
  - HTTPS only (redirect HTTP → HTTPS)
  - Certificate: ACM (AWS Certificate Manager)
  - HSTS: Enabled (max-age=31536000)

Internal Traffic (Service Mesh - Future):
  - mTLS: Istio/Linkerd service mesh
  - Certificate rotation: Automatic (cert-manager)
  - Zero-trust: Verify every connection

Database Connections:
  - PostgreSQL: SSL/TLS required (sslmode=require)
  - Redis: TLS enabled (redis-tls:6379)
```

**Secrets Management:**

**Development:**
- Environment variables (.env.local)
- Git-ignored files
- Never committed to repository

**Staging/Production:**
```yaml
AWS Secrets Manager:
  - Database credentials: Auto-rotation (30 days)
  - API keys: Manual rotation
  - Encryption: KMS-encrypted
  - Access: IAM roles only

Kubernetes Secrets:
  - External Secrets Operator: Sync from AWS Secrets Manager
  - etcd encryption: Enabled (KMS)
  - RBAC: Restrict access per namespace
  - Never hardcoded in manifests

Future (Multi-Cloud):
  - HashiCorp Vault: Centralized secrets
  - Dynamic secrets: Short-lived credentials
  - PKI: Certificate authority
```

**Vulnerability Management:**

**Container Image Security:**
```yaml
Image Scanning:
  - Trivy: Scan all images in CI/CD
  - Fail build: Critical/High vulnerabilities
  - Registry: ECR with image scanning enabled
  - Base images: Official, minimal (Alpine, Distroless)

Image Provenance:
  - Signed images: Cosign (Sigstore)
  - SBOM: Generate for all images
  - Reproducible builds: Deterministic Dockerfiles
  - Immutable tags: Never use 'latest'

Runtime Security:
  - Falco: Runtime threat detection
  - AppArmor/SELinux: Mandatory access control
  - Seccomp: Restrict syscalls
  - Read-only root filesystem: Enforce where possible
```

**Dependency Scanning:**
```yaml
CI/CD Pipeline:
  - Snyk: Scan package.json, Cargo.toml
  - Dependabot: Automated PRs for updates
  - CodeQL: Static analysis (SAST)
  - OWASP ZAP: Dynamic analysis (DAST)

Frequency:
  - Every PR: SAST + dependency scan
  - Daily: DAST on staging
  - Weekly: Full security audit
```

**Compliance & Audit:**

**Logging & Monitoring:**
```yaml
Audit Logs:
  - CloudTrail: All AWS API calls
  - Retention: 90 days
  - Immutable: Write-once, read-many (S3 Object Lock)

Kubernetes Audit:
  - kube-apiserver audit logs
  - Log all authorization decisions
  - Retention: 90 days in S3

Application Logs:
  - Centralized: Loki
  - Structured: JSON format
  - PII masking: Automatic redaction
  - Retention: 30 days

Security Events:
  - GuardDuty: Threat detection
  - Security Hub: Compliance checks
  - Inspector: Vulnerability assessment
```

**Compliance Frameworks:**
```yaml
SOC 2:
  - Access control: RBAC, IAM
  - Encryption: At rest, in transit
  - Monitoring: CloudTrail, GuardDuty
  - Incident response: Runbooks

GDPR:
  - Data deletion: API endpoints for right to be forgotten
  - Data portability: Export user data
  - Consent management: Privacy policy
  - Data residency: EU regions (future)

PCI DSS (if handling payments):
  - Network segmentation: Separate subnets
  - Encryption: All cardholder data
  - Access control: Least privilege
  - Logging: All access to cardholder data
```

---

### Secrets Management: AWS Secrets Manager + HashiCorp Vault
- **Development:** Environment variables (.env.local)
- **Staging/Production:** AWS Secrets Manager
- **Future:** HashiCorp Vault (when scaling to multi-cloud)

**Justification:**
- AWS Secrets Manager: Native AWS integration, automatic rotation
- Vault: Multi-cloud, advanced features (dynamic secrets, PKI)
- Start simple (Secrets Manager), migrate to Vault when needed

---

### Deployment Strategy: GitOps (ArgoCD)
- **CI/CD:** GitHub Actions (build + test)
- **Deployment:** ArgoCD (Kubernetes deployments)
- **Rollback:** Declarative rollbacks via Git

**Justification:**
- Git as single source of truth
- Automated deployments on merge to main
- Easy rollbacks (revert commit)
- Audit trail in Git history

---

### Blockchain Node Deployment (Stateful Workloads)

**Challenge:** Blockchain nodes require persistent state (blocks, chain data) and cannot be treated as stateless containers.

**Storage Strategy:**
```yaml
StatefulSet Configuration:
  - Kind: StatefulSet (not Deployment)
  - Replicas: 3 (validator nodes)
  - Volume: Persistent Volume Claims (PVCs)
  - Storage Class: gp3 (AWS EBS)
  - Reclaim Policy: Retain (prevent data loss)

Persistent Volumes:
  - Size: 500GB per node (grows with chain)
  - Type: EBS gp3 (high IOPS, cost-effective)
  - Snapshots: Daily automated backups
  - Expansion: Dynamic volume resize (no downtime)

Data Locality:
  - Pod affinity: Node in same AZ as EBS volume
  - Topology: Spread nodes across 3 AZs
  - Anti-affinity: One validator per physical host
```

**Node Recovery Procedure:**
```yaml
Scenario 1: Pod Crash (StatefulSet auto-recovery)
  1. Kubernetes detects pod failure
  2. New pod scheduled on same node (preserves volume)
  3. Pod mounts existing PVC (chain data intact)
  4. Node resumes from last block
  - RTO: 5 minutes
  - RPO: 0 (no data loss)

Scenario 2: EBS Volume Failure (restore from snapshot)
  1. Detect volume failure (health check)
  2. Create new volume from latest snapshot
  3. Update PVC to point to new volume
  4. Restart pod with restored volume
  5. Node syncs missing blocks from peers
  - RTO: 30 minutes
  - RPO: 1 hour (snapshot frequency)

Scenario 3: Complete AZ Failure (multi-AZ recovery)
  1. Kubernetes reschedules pod to healthy AZ
  2. Create new EBS volume from cross-AZ snapshot
  3. Pod mounts new volume
  4. Node syncs from peers
  - RTO: 1 hour
  - RPO: 1 hour
```

**Performance Considerations:**
```yaml
IOPS Requirements:
  - Block production: 3000 IOPS (write-heavy)
  - Block sync: 6000 IOPS (read-heavy during initial sync)
  - Storage type: gp3 (16000 IOPS baseline, burstable)

Network Requirements:
  - P2P networking: Persistent IPs (StatefulSet stable network IDs)
  - Peer discovery: DNS-based (chaing-0.chaing.production.svc.cluster.local)
  - Port forwarding: NodePort/LoadBalancer for external peers

Resource Limits:
  - CPU: 4 cores (guaranteed)
  - Memory: 16GB (guaranteed)
  - Storage: 500GB (expandable to 2TB)
```

**Backup & Disaster Recovery:**
```yaml
Chain Data Backups:
  - Frequency: Every 6 hours (EBS snapshots)
  - Retention: 7 days (rolling window)
  - Cross-region: Copy to secondary region (daily)
  - Verification: Automated restore tests (weekly)

State Export:
  - Format: RocksDB export (native format)
  - Frequency: Daily (off-peak hours)
  - Storage: S3 (compressed, encrypted)
  - Use case: Fast bootstrap for new nodes
```

---

### Environment Strategy

**Development (Local):**
```yaml
Services: Docker Compose
Database: PostgreSQL container (port 5432)
Redis: Redis container (port 6379)
Frontend: http://localhost:5000
Backend: http://localhost:4000
Cost: $0/month
```

**Staging (AWS):**
```yaml
Cluster: EKS (t3.medium nodes x2)
Database: RDS PostgreSQL (db.t3.micro)
Cache: ElastiCache Redis (cache.t3.micro)
Storage: S3 (minimal usage)
Monitoring: Prometheus + Grafana (self-hosted)
Cost: ~$150-200/month
```

**Production (AWS):**
```yaml
Cluster: EKS (t3.large nodes x3, auto-scaling to 6)
Database: RDS PostgreSQL (db.r5.large, Multi-AZ)
Cache: ElastiCache Redis (cache.r5.large, Multi-AZ)
Storage: S3 (with CloudFront CDN)
Monitoring: Prometheus + Grafana + PagerDuty
Cost: ~$800-1200/month (scales with usage)
```

---

### Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS Cloud                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────── VPC ──────────────────────┐          │
│  │                                               │          │
│  │  ┌──────────── EKS Cluster ───────────┐      │          │
│  │  │                                     │      │          │
│  │  │  Frontend     Backend Services     │      │          │
│  │  │  ├─ Web       ├─ API Gateway       │      │          │
│  │  │  └─ Admin     ├─ Indexer           │      │          │
│  │  │              ├─ RPC Orchestrator   │      │          │
│  │  │              └─ AI Engine          │      │          │
│  │  │                                     │      │          │
│  │  │  Blockchain Nodes                   │      │          │
│  │  │  └─ ChainGhost Node x3              │      │          │
│  │  │                                     │      │          │
│  │  │  Monitoring                         │      │          │
│  │  │  ├─ Prometheus                      │      │          │
│  │  │  └─ Grafana                         │      │          │
│  │  └─────────────────────────────────────┘      │          │
│  │                                               │          │
│  │  ┌─────── Data Layer ──────┐                 │          │
│  │  │                          │                 │          │
│  │  │  RDS PostgreSQL          │                 │          │
│  │  │  (Multi-AZ)              │                 │          │
│  │  │                          │                 │          │
│  │  │  ElastiCache Redis       │                 │          │
│  │  │  (Multi-AZ)              │                 │          │
│  │  └──────────────────────────┘                 │          │
│  │                                               │          │
│  └───────────────────────────────────────────────┘          │
│                                                             │
│  ┌───────────── External Services ──────────────┐          │
│  │  S3 (Storage) + CloudFront (CDN)             │          │
│  │  Secrets Manager (Secrets)                   │          │
│  │  Route 53 (DNS)                              │          │
│  │  ALB (Load Balancer)                         │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘

                        │
                        ▼
              
          GitHub Actions CI/CD
                │
                ▼
        ArgoCD (GitOps Deployment)
```

---

### Positive Consequences

- **Scalability:** Kubernetes auto-scaling handles traffic spikes
- **Reliability:** Multi-AZ deployment, auto-healing, rolling updates
- **Cost-Effective:** Start with small instances, scale as needed
- **Developer Experience:** Consistent environments (dev → staging → prod)
- **Observability:** Complete visibility with Prometheus + Grafana
- **Security:** Network isolation, secrets management, audit trails
- **Multi-Cloud Ready:** Terraform modules portable to GCP/Azure
- **GitOps:** Declarative deployments, easy rollbacks

### Negative Consequences

- **Complexity:** Kubernetes learning curve for team
  - **Mitigation:** Provide training, documentation, runbooks
- **Cost:** AWS costs can escalate without monitoring
  - **Mitigation:** Set billing alerts, optimize instance sizes
- **Vendor Lock-in:** AWS-specific services (RDS, Secrets Manager)
  - **Mitigation:** Use Terraform, abstract cloud-specific services
- **Operational Overhead:** Monitoring, upgrades, security patches
  - **Mitigation:** Managed services (EKS, RDS), automation

## Pros and Cons of the Options

### Cloud Provider: AWS vs GCP vs Azure

#### AWS
**Pros:**
- Most mature ecosystem for blockchain/Web3
- Excellent support for Kubernetes (EKS)
- Best RDS PostgreSQL performance
- Largest marketplace (AMIs, services)
- Generous free tier for development

**Cons:**
- Vendor lock-in risk
- Complex pricing structure
- Some services more expensive than competitors

#### GCP
**Pros:**
- Best Kubernetes (GKE invented Kubernetes)
- Excellent data analytics (BigQuery)
- Simpler pricing
- Good performance

**Cons:**
- Smaller ecosystem for blockchain
- Fewer managed services
- Less mature than AWS

#### Azure
**Pros:**
- Best for .NET workloads
- Good hybrid cloud support
- Enterprise integrations

**Cons:**
- Smallest blockchain ecosystem
- More expensive for our use case
- Less developer-friendly

**Why AWS:** Best balance of maturity, ecosystem, and cost for Web3 workloads.

---

### Orchestration: Kubernetes vs ECS vs Cloud Run

#### Kubernetes (EKS)
**Pros:**
- Industry standard, portable across clouds
- Auto-scaling, self-healing
- Rich ecosystem (Helm, Operators)
- Declarative configuration

**Cons:**
- Steeper learning curve
- More complex than ECS/Cloud Run

#### AWS ECS/Fargate
**Pros:**
- Simpler than Kubernetes
- Serverless option (Fargate)
- Native AWS integration

**Cons:**
- AWS lock-in
- Less portable
- Limited ecosystem

#### Google Cloud Run
**Pros:**
- Simplest (serverless containers)
- Auto-scaling
- Low cost

**Cons:**
- GCP lock-in
- Limited control
- Not suitable for stateful workloads (blockchain nodes)

**Why Kubernetes:** Portability + ecosystem + control for our complex microservices.

---

### IaC: Terraform vs Pulumi vs CloudFormation

#### Terraform
**Pros:**
- Declarative, cloud-agnostic
- Mature ecosystem
- State management
- Easy collaboration

**Cons:**
- HCL syntax (not programming language)
- State management complexity

#### Pulumi
**Pros:**
- Use real programming languages (TypeScript, Python)
- Better for complex logic
- Cloud-agnostic

**Cons:**
- Smaller ecosystem than Terraform
- State management similar complexity

#### CloudFormation
**Pros:**
- Native AWS, no extra tools
- Free

**Cons:**
- AWS lock-in
- YAML verbosity
- Limited to AWS

**Why Terraform:** Cloud-agnostic + mature ecosystem + team familiarity.

---

### Monitoring: Prometheus vs Datadog vs New Relic

#### Prometheus + Grafana + Loki
**Pros:**
- Open-source, self-hosted (cost-effective)
- Kubernetes-native
- Rich ecosystem
- No vendor lock-in

**Cons:**
- Self-managed (operational overhead)
- Requires expertise

#### Datadog
**Pros:**
- All-in-one (metrics, logs, APM)
- Excellent UX
- Managed service

**Cons:**
- Expensive ($15-31/host/month)
- Vendor lock-in

#### New Relic
**Pros:**
- Comprehensive observability
- Good APM

**Cons:**
- Very expensive
- Complex pricing

**Why Prometheus:** Cost-effective + Kubernetes-native + no lock-in.

---

## Links

- [Related ADRs]
  - ADR-001: Tech Stack Selection
  - ADR-003: CI/CD Pipeline Design
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/setup/best-practices/)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Prometheus Operator](https://prometheus-operator.dev/)

## Notes

### Implementation Plan (Phase 0.4)

**Week 1-2: Terraform Modules**
- VPC module (networking, subnets, security groups)
- Compute module (EKS cluster, node groups)
- Database module (RDS PostgreSQL, parameter groups)
- Storage module (S3 buckets, CloudFront)

**Week 2-3: Kubernetes Manifests**
- Base configurations (namespaces, RBAC)
- Service deployments (frontend, backend services)
- ConfigMaps and Secrets (environment config)
- Ingress (ALB configuration)
- Resource limits and health checks

**Week 3-4: Monitoring Setup**
- Prometheus installation (Helm chart)
- Grafana dashboards (service health, performance)
- Loki for log aggregation
- AlertManager + PagerDuty integration
- Custom metrics exporters

**Week 4: Runbooks**
- Node recovery procedure
- Database restore procedure
- Incident response playbook
- Rollback procedure
- Disaster recovery plan

### Cost Estimates

**Development (Docker Compose):**
- Cost: $0/month (fully local)

**Staging (AWS):**
```yaml
Compute:
  - EKS Control Plane: $73/month (fixed cost, per cluster)
  - Worker Nodes: $30/month (t3.medium x2 @ $0.0416/hr)
Database:
  - RDS PostgreSQL: $15/month (db.t3.micro single-AZ)
Cache:
  - ElastiCache Redis: $12/month (cache.t3.micro single-AZ)
Storage:
  - S3: $5/month (minimal usage)
  - EBS: $10/month (gp3 volumes for nodes)
Networking:
  - Data transfer: $10/month (intra-region)
  - NAT Gateway: $32/month (per AZ)
Monitoring:
  - Self-hosted: $0 (Prometheus/Grafana on EKS)
Total: ~$187/month
```

**Production (AWS) - Estimated:**
```yaml
Compute:
  - EKS Control Plane: $73/month (fixed cost)
  - Worker Nodes: $360/month (t3.large x3-6 auto-scaling @ $0.0832/hr avg 5 nodes)
  - Blockchain Nodes: $150/month (dedicated c5.2xlarge x2 @ $0.34/hr)
Database:
  - RDS PostgreSQL: $280/month (db.r5.large Multi-AZ)
  - Read Replicas: $140/month (db.r5.large x1)
Cache:
  - ElastiCache Redis: $120/month (cache.r5.large Multi-AZ)
Storage:
  - S3: $50/month (application data, backups)
  - EBS: $150/month (gp3 volumes, blockchain node storage 500GB x3)
  - Snapshots: $30/month (EBS snapshot storage)
Networking:
  - Data transfer: $80/month (egress traffic)
  - NAT Gateway: $96/month (3 AZs @ $32/month each)
  - ALB: $25/month (Application Load Balancer)
Monitoring:
  - Self-hosted: $0 (Prometheus/Grafana on EKS)
  - CloudWatch: $20/month (logs, alarms)
Disaster Recovery:
  - Cross-region backups: $40/month (S3 replication, RDS snapshots)
Total: ~$1,614/month (base), scales with traffic

Scaling Estimate (10x traffic):
  - Worker nodes: ~$600/month (auto-scale to 12 nodes)
  - Data transfer: ~$300/month
  - Total: ~$2,500/month
```

**Cost Breakdown Notes:**
- **EKS Control Plane:** $73/month is fixed per cluster (HA across 3 AZs)
- **NAT Gateway:** $32/month per AZ (required for private subnet egress)
- **Multi-AZ Overhead:** ~40% cost premium for high availability
- **Blockchain Storage:** Grows ~10GB/month, plan for expansion

### Migration Path

**Phase 0-1:** Local development only (Docker Compose)
**Phase 1-2:** Deploy staging to AWS (validate infrastructure)
**Phase 2-3:** Production deployment (with load testing)
**Phase 4+:** Multi-cloud expansion (if needed)

### Disaster Recovery & Business Continuity

**Recovery Objectives:**
```yaml
Service Tier SLAs:
  Critical Services (API Gateway, Blockchain Nodes):
    - RTO: 15 minutes
    - RPO: 5 minutes
    - Availability: 99.95%
  
  Core Services (Indexer, RPC Orchestrator):
    - RTO: 30 minutes
    - RPO: 15 minutes
    - Availability: 99.9%
  
  Supporting Services (AI Engine, Admin):
    - RTO: 1 hour
    - RPO: 1 hour
    - Availability: 99.5%
```

**Multi-Region Disaster Recovery Architecture:**
```yaml
Primary Region: us-east-1 (N. Virginia)
  - Full production stack
  - All services active
  - Serving 100% traffic

Secondary Region: us-west-2 (Oregon)
  - Standby infrastructure (warm standby)
  - Database read replicas
  - Cross-region S3 replication
  - Serves traffic only during failover

Tertiary Region: eu-west-1 (Ireland) - Future
  - Geographic redundancy
  - EU data residency (GDPR compliance)
```

**Backup Strategy (Layered Approach):**

**Layer 1: Continuous Replication (RPO: 0-5 minutes)**
```yaml
RDS PostgreSQL:
  - Primary: us-east-1 (Multi-AZ within region)
  - Read Replica: us-west-2 (cross-region async replication)
  - Replication Lag: <30 seconds (monitored)
  - Automatic failover: Yes (via Route 53 health checks)

ElastiCache Redis:
  - Primary: us-east-1 (Multi-AZ with auto-failover)
  - Backup: Daily snapshots to S3
  - Cross-region: Manual restore from S3 (RTO: 30 min)

S3 Storage:
  - Versioning: Enabled (accidental deletion protection)
  - Cross-Region Replication: us-east-1 → us-west-2
  - Replication: Real-time (asynchronous)
  - Lifecycle: Transition to Glacier after 90 days
```

**Layer 2: Point-in-Time Snapshots (RPO: 1 hour)**
```yaml
RDS Automated Backups:
  - Frequency: Every 1 hour (continuous)
  - Retention: 35 days
  - Cross-region copy: Daily (us-east-1 → us-west-2)
  - Encryption: KMS-encrypted

EBS Snapshots (Blockchain Nodes):
  - Frequency: Every 6 hours
  - Retention: 7 days (rolling window)
  - Cross-region copy: Daily
  - Incremental: Only changed blocks

EKS etcd Backup:
  - Frequency: Every 1 hour
  - Storage: S3 (encrypted)
  - Retention: 7 days
  - Automated: Via Velero (Kubernetes backup tool)
```

**Layer 3: Logical Exports (RPO: 24 hours)**
```yaml
PostgreSQL Logical Backup:
  - Tool: pgdump (full database export)
  - Frequency: Daily (2 AM UTC, off-peak)
  - Compression: gzip (reduce storage cost)
  - Encryption: GPG-encrypted before upload
  - Storage: S3 (versioned, cross-region replicated)
  - Retention: 90 days
  - Verification: Weekly restore test to staging

Application Data Export:
  - Format: JSON (portable, human-readable)
  - Frequency: Weekly
  - Use case: Migration, audit, compliance
  - Storage: S3 (encrypted, immutable)
```

**Disaster Scenarios & Response Procedures:**

**Scenario 1: Availability Zone Failure**
```yaml
Impact: Single AZ outage (1/3 of resources)
Response:
  1. Kubernetes auto-reschedules pods to healthy AZs (5 min)
  2. RDS/ElastiCache auto-failover to standby (1-2 min)
  3. EBS volumes re-attached in new AZ (5 min)
Actual RTO: 5-10 minutes
Actual RPO: 0 (no data loss)
Manual Action: None (fully automated)
```

**Scenario 2: Region Failure (Primary Region Down)**
```yaml
Impact: Complete loss of us-east-1
Response:
  1. Detect failure (Route 53 health checks, PagerDuty alert)
  2. Promote us-west-2 read replica to primary (manual approval)
  3. Update Route 53 DNS to point to us-west-2 (TTL: 60 sec)
  4. Scale up us-west-2 infrastructure (Terraform apply)
  5. Verify application functionality (smoke tests)
  6. Monitor replication lag (ensure data consistency)
Actual RTO: 30-45 minutes
Actual RPO: 30 seconds (replication lag)
Manual Action: Approval required (runbook-driven)

Post-Failover:
  - us-west-2 becomes new primary
  - us-east-1 restored when available
  - Reverse replication (us-west-2 → us-east-1)
  - Planned cutover back to us-east-1 (when safe)
```

**Scenario 3: Data Corruption / Ransomware Attack**
```yaml
Impact: Database corruption or malicious deletion
Response:
  1. Identify point of corruption (audit logs, alerts)
  2. Stop application writes (prevent further damage)
  3. Restore RDS from snapshot (before corruption)
  4. Restore S3 objects (versioning + object lock)
  5. Replay transactions (from corruption point to current)
  6. Verify data integrity (checksums, business logic)
  7. Resume application
Actual RTO: 1-2 hours
Actual RPO: 1 hour (snapshot granularity)
Manual Action: Incident response team

Prevention:
  - S3 Object Lock (WORM - Write Once Read Many)
  - MFA Delete for critical buckets
  - Immutable backups (cannot be deleted/modified)
  - Regular restore drills (test recovery procedures)
```

**Scenario 4: Complete Account Compromise**
```yaml
Impact: AWS account takeover
Response:
  1. Revoke all credentials (IAM, access keys)
  2. Enable MFA on root account (if not already)
  3. Provision new AWS account (clean slate)
  4. Restore infrastructure via Terraform (IaC)
  5. Restore data from cross-account backups
  6. Update DNS to new account
Actual RTO: 4-8 hours
Actual RPO: 24 hours (daily logical backups)
Manual Action: Security incident response

Prevention:
  - Cross-account backup replication (separate AWS account)
  - AWS Organizations + SCPs (Service Control Policies)
  - CloudTrail + GuardDuty (detect anomalies)
  - Regular security audits (penetration testing)
```

**Failover Automation:**
```yaml
Automated Failover (No Human Intervention):
  - AZ failure: Kubernetes + RDS auto-failover
  - Pod crash: Kubernetes liveness probes
  - Node failure: EKS node auto-replacement

Semi-Automated Failover (Human Approval Required):
  - Region failure: Runbook-driven (Terraform + scripts)
  - Database failover: Manual promotion (data validation)
  - DNS cutover: Manual Route 53 update (approval gate)

Manual Failover (Incident Response):
  - Data corruption: Point-in-time restore
  - Security incident: Full account recovery
  - Ransomware: Immutable backup restore
```

**Backup Verification & Testing:**
```yaml
Daily:
  - Automated backup completion checks (CloudWatch alarms)
  - Replication lag monitoring (RDS, S3)

Weekly:
  - Restore test to staging (pgdump restore)
  - Data integrity verification (checksums)

Monthly:
  - Full disaster recovery drill (failover to us-west-2)
  - Cross-region restore test
  - Runbook validation (update procedures)

Quarterly:
  - Chaos engineering (simulate failures)
  - Security incident simulation (ransomware drill)
  - Business continuity plan review
```

**Data Retention Policy:**
```yaml
Hot Data (Immediate Access):
  - Application database: 90 days
  - Application logs: 30 days
  - Metrics: 30 days

Warm Data (Infrequent Access):
  - Database snapshots: 35 days
  - EBS snapshots: 7 days
  - Audit logs: 90 days

Cold Data (Archive):
  - Logical backups: 1 year (S3 Glacier)
  - Compliance logs: 7 years (S3 Glacier Deep Archive)
  - Historical metrics: 1 year (S3 Intelligent-Tiering)
```

---

**Review Date:** 2025-12-15  
**Next Review:** After Phase 1 completion or if infrastructure costs exceed $1500/month
