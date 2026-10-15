# ADR-006: Use Terraform for Infrastructure as Code

## Status

✅ **Accepted**

**Date:** 27. Oktober 2025

## Context

Die AI-Freelancer-Plattform benötigt Cloud-Infrastruktur für Deployment:

- **Compute:** AWS ECS Fargate (Container)
- **Database:** AWS RDS PostgreSQL
- **Storage:** AWS S3 (Files)
- **CDN:** CloudFront
- **Networking:** VPC, Security Groups, Load Balancer
- **DNS:** Route 53

**Herausforderung:** Wie verwalten wir diese Infrastruktur?

**Optionen:**

1. **Manual Provisioning** (AWS Console, Click-Ops)
2. **Infrastructure as Code** (Terraform, CloudFormation, Pulumi)

**Anforderungen:**

- Multiple Environments (dev, staging, production)
- Reproduzierbarkeit (Disaster Recovery)
- Version Control (Git)
- DSGVO-Compliance (EU Frankfurt)
- Solo-Developer friendly

## Decision

Wir verwenden **Terraform** für alle Infrastruktur-Provisionierung und -Verwaltung.

## Rationale

### Warum Terraform?

**1. Reproduzierbarkeit**

```bash
# Problem: Manuelle AWS Console Konfiguration
- Admin klickt in AWS Console → ECS Cluster erstellt
- Wochen später: "Wie war das nochmal konfiguriert?"
- Disaster: Alle Ressourcen gelöscht → Wie wiederherstellen?

# Lösung: Terraform
terraform apply
# → Komplette Infrastruktur wird aus Code erstellt
# → Exakt reproduzierbar in dev/staging/prod
```

**2. Version Control**

```bash
git log terraform/
# → Sehe alle Infrastruktur-Änderungen
# → Wer, wann, warum wurde ECS-Task-Size geändert?
# → Rollback möglich: git revert + terraform apply
```

**3. Multi-Environment Support**

```
terraform/
├── environments/
│   ├── dev/           # 1x ECS Task, db.t3.micro
│   ├── staging/       # 2x ECS Task, db.t3.small
│   └── production/    # 5x ECS Task, db.t3.medium, Multi-AZ
```

Gleicher Code, unterschiedliche Werte → Consistency!

**4. State Management**

```
Terraform weiß:
- Was ist deployed? (State)
- Was soll deployed sein? (Config)
- Was muss geändert werden? (Diff)

$ terraform plan
  + aws_ecs_service.app will be created
  ~ aws_rds_instance.db will be updated
```

**5. Collaboration & Review**

```bash
# Pull Request für Infrastruktur-Änderung:
git diff terraform/
# → Review: "Warum ändern wir RDS Instance Type?"
# → Approval → Merge → terraform apply in CI/CD
```

**6. Multi-Cloud (Future-Proof)**

```hcl
# Heute: AWS
provider "aws" { region = "eu-central-1" }

# Morgen: Zusätzlich GCP?
provider "google" { region = "europe-west3" }

# Terraform unterstützt 3000+ Providers
```

**7. Documentation as Code**

```hcl
# Terraform Config IST die Dokumentation
resource "aws_ecs_service" "app" {
  name            = "freelancer-service"
  cluster         = aws_ecs_cluster.main.id
  desired_count   = 3
  launch_type     = "FARGATE"
  # ...
}

# Keine separate Doku nötig → Code ist Truth
```

## Alternatives Considered

### Alternative 1: AWS CloudFormation

**Pros:**

- ✅ Native AWS (keine 3rd-party Tool)
- ✅ Gut integriert mit AWS Services
- ✅ Kostenlos

**Cons:**

- ❌ **AWS-only** (kein Multi-Cloud)
- ❌ **Verbose YAML** (100+ Zeilen für simple Ressource)
- ❌ Langsamer als Terraform (Stack-Updates dauern länger)
- ❌ Kleineres Ecosystem (weniger Modules)

**Beispiel-Vergleich:**

```yaml
# CloudFormation: ~50 Zeilen für ECS Service
Resources:
  ECSService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: freelancer-service
      Cluster: !Ref ECSCluster
      DesiredCount: 3
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets:
            - !Ref SubnetA
            - !Ref SubnetB
          SecurityGroups:
            - !Ref SecurityGroup
      # ... viele weitere Zeilen
```

```hcl
# Terraform: ~15 Zeilen für ECS Service
resource "aws_ecs_service" "app" {
  name            = "freelancer-service"
  cluster         = aws_ecs_cluster.main.id
  desired_count   = 3
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.app.id]
  }
}
```

**Warum nicht gewählt:**
Terraform ist prägnanter, Multi-Cloud-fähig, größeres Ecosystem.

### Alternative 2: Pulumi

**Pros:**

- ✅ Code in TypeScript/Python/Go (nicht HCL)
- ✅ Volle Programming Language Features (Loops, Functions)
- ✅ Type-safe (für TypeScript)

**Cons:**

- ❌ **Jüngeres Tool** (2018 vs. Terraform 2014)
- ❌ Kleinere Community
- ❌ Weniger Ressourcen/Tutorials
- ❌ Vendor Lock-in (Pulumi Cloud für State)

**Beispiel:**

```typescript
// Pulumi (TypeScript)
import * as aws from '@pulumi/aws';

const service = new aws.ecs.Service('app', {
  cluster: cluster.id,
  desiredCount: 3,
  launchType: 'FARGATE',
  // ...
});
```

**Warum nicht gewählt:**
Terraform ist etablierter, größere Community, mehr Solo-Dev-friendly. Pulumi ist gut, aber Terraform ist "safer choice".

### Alternative 3: Manual Provisioning (AWS Console)

**Pros:**

- ✅ Schneller Start (kein Terraform Setup)
- ✅ GUI-basiert (visuell)
- ✅ Kein Code zu maintainen

**Cons:**

- ❌ **Nicht reproduzierbar**
- ❌ **Kein Version Control** (keine History)
- ❌ **Fehleranfällig** (Click-Fehler)
- ❌ **Nicht skalierbar** (neue Environments = viel Arbeit)
- ❌ **Kein Rollback**

**Beispiel-Szenario:**

```
1. Admin erstellt ECS Cluster in AWS Console
2. 3 Monate später: Disaster, alles gelöscht
3. Problem: "Wie war das konfiguriert?"
   - Welche Security Group Rules?
   - Welche Subnets?
   - Welche IAM Roles?
4. Manuell rekonstruieren → Fehler garantiert
```

**Mit Terraform:**

```bash
terraform apply
# → Alles ist wieder da, exakt wie vorher
```

**Warum nicht gewählt:**
Für MVP wäre es schneller, aber für Production ist Reproduzierbarkeit kritischer. Manual ist "Technical Debt from Day 1".

## Implementation Strategy

### Phase 1: Terraform Setup (Phase 3, jetzt)

1. **Terraform Structure erstellen:**

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── production/
├── modules/
│   ├── ecs/              # ECS Cluster + Service
│   ├── rds/              # PostgreSQL Database
│   ├── s3/               # S3 Buckets
│   ├── networking/       # VPC, Subnets, Security Groups
│   └── monitoring/       # CloudWatch, Alarms
├── .gitignore            # *.tfstate, *.tfvars (secrets)
└── README.md             # Terraform Usage Guide
```

2. **S3 Backend für State:**

```hcl
# terraform/environments/production/main.tf
terraform {
  backend "s3" {
    bucket         = "freelancer-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "eu-central-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"  # State locking
  }
}
```

3. **Modules erstellen:**

```hcl
# terraform/modules/ecs/main.tf
resource "aws_ecs_cluster" "main" {
  name = var.cluster_name
}

resource "aws_ecs_service" "app" {
  name            = var.service_name
  cluster         = aws_ecs_cluster.main.id
  desired_count   = var.desired_count
  launch_type     = "FARGATE"
  # ...
}
```

### Phase 2: Infrastructure Deployment (Phase 3.6)

1. **Development Environment:**

```bash
cd terraform/environments/dev
terraform init
terraform plan
terraform apply
```

2. **Production Environment:**

```bash
cd terraform/environments/production
terraform plan  # Review changes
terraform apply # Deploy
```

### Phase 3: CI/CD Integration (Phase 3.6)

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  push:
    branches: [main]
    paths:
      - 'terraform/**'

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Terraform Init
        run: terraform init
        working-directory: terraform/environments/production

      - name: Terraform Plan
        run: terraform plan
        working-directory: terraform/environments/production

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve
        working-directory: terraform/environments/production
```

## Consequences

### Positive

1. **Reproduzierbarkeit**
   - Komplette Infrastruktur aus Code erstellbar
   - Disaster Recovery: `terraform apply`
   - Neue Environments: Copy-Paste + Vars ändern

2. **Version Control**
   - Alle Infrastruktur-Änderungen in Git
   - Code Review für Infrastruktur
   - Rollback möglich

3. **Consistency**
   - Dev = Staging = Production (unterschiedliche Größen)
   - Keine Drift (Terraform detektiert Manual-Changes)

4. **Documentation**
   - Code IST Dokumentation
   - Immer aktuell (Code = Reality)

5. **Collaboration**
   - Pull Requests für Infrastruktur
   - Team kann reviewen (später)

### Negative

1. **Learning Curve**
   - HCL Sprache neu lernen
   - Terraform Concepts (State, Providers, Modules)
   - Zeit-Investment: 1-2 Wochen
   - **Mitigation:** Schrittweise lernen, Start mit simplen Modules

2. **State Management Komplexität**
   - State muss in S3 gespeichert werden (Remote Backend)
   - State Locking mit DynamoDB (Race Conditions vermeiden)
   - State kann korrupt werden (bei Fehlern)
   - **Mitigation:** S3 Versioning, State Backups, Terraform Cloud (später)

3. **Initial Setup Overhead**
   - Terraform Setup: ~1-2 Tage
   - Module Design: ~2-3 Tage
   - Länger als Manual AWS Console
   - **Mitigation:** Invest now, save later. Manual würde bei Environment 2-3 schon länger dauern.

4. **State Drift Risk**
   - Wenn jemand Manual in AWS Console ändert → State Drift
   - Terraform `plan` zeigt Diff
   - **Mitigation:** Policy: "Alle Änderungen via Terraform", Read-Only AWS Console Access

5. **Debugging Schwieriger**
   - Terraform Errors können kryptisch sein
   - AWS API Errors nicht immer klar
   - **Mitigation:** Verbose Logging (`TF_LOG=DEBUG`), Community Support

### Mitigation Strategies

**1. Learning Curve:**

- Start simple: Nur ECS + RDS (Phase 3.6)
- Expand gradually: S3, CloudFront, etc. (später)
- Use existing Modules (Terraform Registry)
- Dokumentation in README.md

**2. State Management:**

- S3 Backend mit Versioning (Backups)
- DynamoDB für State Locking
- Separate States pro Environment (dev, staging, prod)
- Backup State regelmäßig

**3. State Drift:**

- Policy: "Alle Änderungen via Terraform"
- AWS IAM: Read-Only Console Access (nur Terraform kann schreiben)
- Regelmäßig `terraform plan` (CI/CD)

**4. Debugging:**

- `TF_LOG=DEBUG` für Verbose Output
- `terraform plan` vor `apply`
- Small Changes (nicht alles auf einmal)

## Cost Implications

**Terraform selbst:**

- ✅ **Open Source** (kostenlos)
- ✅ Terraform Cloud Free Tier (bis 5 Users)

**AWS Kosten (unverändert):**

- ECS, RDS, S3 kosten gleich viel (Terraform vs. Manual)
- Terraform verursacht keine zusätzlichen AWS-Kosten

**Time Investment:**

- Initial Setup: ~3-5 Tage
- Maintenance: ~1-2h/Monat
- **ROI:** Spart Wochen bei Environment 2-3, Disaster Recovery, Onboarding neuer Devs

## Security Considerations

✅ **State Security:**

- S3 Bucket encrypted (AES-256)
- S3 Versioning (Backup)
- IAM Roles (Principle of Least Privilege)

✅ **Secrets Management:**

- Keine Secrets in `.tf` Files (Git)
- Use `terraform.tfvars` (gitignored)
- Use AWS Parameter Store / Secrets Manager
- Use Environment Variables in CI/CD

✅ **Access Control:**

- Terraform State in S3 (restricted access)
- IAM Roles für Terraform (nicht root)
- Multi-Factor Auth für Production

## Monitoring & Validation

**Terraform Plan in CI/CD:**

```yaml
# Run terraform plan on every PR
on: pull_request
  - terraform plan
  - Post plan as PR comment
```

**Drift Detection:**

```bash
# Cron Job: Daily terraform plan
terraform plan -detailed-exitcode
# Exit code 2 = Drift detected → Alert
```

**Terraform Validate:**

```bash
terraform validate  # Syntax check
terraform fmt -check # Format check
tflint              # Linting
```

## Follow-up Actions

- [x] Entscheidung für Terraform getroffen
- [ ] Terraform Structure erstellen (`terraform/`)
- [ ] S3 Backend für State konfigurieren
- [ ] ECS Module erstellen (`terraform/modules/ecs/`)
- [ ] RDS Module erstellen (`terraform/modules/rds/`)
- [ ] Networking Module (`terraform/modules/networking/`)
- [ ] Development Environment (`terraform/environments/dev/`)
- [ ] CI/CD Integration (GitHub Actions)
- [ ] Dokumentation (`terraform/README.md`)

## References

- [Terraform Documentation](https://www.terraform.io/docs)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS ECS with Terraform](https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest)
- [Terraform State Management](https://www.terraform.io/docs/language/state/index.html)

---

## Example: ECS Service Module

```hcl
# terraform/modules/ecs/main.tf

variable "cluster_name" {
  description = "ECS Cluster Name"
  type        = string
}

variable "service_name" {
  description = "ECS Service Name"
  type        = string
}

variable "desired_count" {
  description = "Number of tasks"
  type        = number
  default     = 1
}

variable "container_image" {
  description = "Docker image URL"
  type        = string
}

variable "cpu" {
  description = "Task CPU (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 512
}

variable "memory" {
  description = "Task Memory in MB"
  type        = number
  default     = 1024
}

variable "subnets" {
  description = "Subnet IDs for ECS tasks"
  type        = list(string)
}

variable "security_groups" {
  description = "Security Group IDs"
  type        = list(string)
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = var.cluster_name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = var.service_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.cpu
  memory                   = var.memory

  container_definitions = jsonencode([{
    name  = var.service_name
    image = var.container_image

    portMappings = [{
      containerPort = 3000
      protocol      = "tcp"
    }]

    environment = [
      {
        name  = "NODE_ENV"
        value = "production"
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/${var.service_name}"
        "awslogs-region"        = "eu-central-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = var.service_name
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.subnets
    security_groups = var.security_groups
    assign_public_ip = false
  }

  lifecycle {
    ignore_changes = [desired_count] # Allow auto-scaling
  }
}

# Outputs
output "cluster_id" {
  value = aws_ecs_cluster.main.id
}

output "service_name" {
  value = aws_ecs_service.app.name
}
```

**Usage:**

```hcl
# terraform/environments/production/main.tf

module "ecs" {
  source = "../../modules/ecs"

  cluster_name     = "freelancer-cluster"
  service_name     = "freelancer-service"
  desired_count    = 3
  container_image  = "123456789.dkr.ecr.eu-central-1.amazonaws.com/freelancer-app:latest"
  cpu              = 1024
  memory           = 2048
  subnets          = module.networking.private_subnet_ids
  security_groups  = [module.networking.app_security_group_id]
}
```

---

**Author:** Max Mustermann
**Date:** 27. Oktober 2025
**Status:** Accepted
**Impact:** High (affects all infrastructure management)
