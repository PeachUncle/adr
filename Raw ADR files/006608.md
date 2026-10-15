# ADR 0001 — Use Auto Scaling Group (ASG) with EC2 instead of ECS/EKS

## 📖 Context

We need to run a containerized backend service in our AWS High Availability Web App project.There are multiple compute options in AWS:

- **Amazon ECS (Fargate or EC2 launch type):**
  - Serverless container orchestrator managed by AWS.
  - Reduces ops overhead for scaling and scheduling.
- **Amazon EKS (Kubernetes):**
  - Fully managed Kubernetes control plane.
  - Rich ecosystem, advanced scaling and service mesh options.
- **EC2 Auto Scaling Group (ASG) with user data:**
  - Launches VM instances directly.
  - User data boots Docker, pulls image from ECR, and runs the container.

We are prioritizing **clarity, portfolio demonstration, and learning core AWS primitives** over advanced orchestration.

## ✅ Decision

We will use an **EC2 Auto Scaling Group (ASG)** to run the backend service.Each EC2 instance will:

- Run in private subnets across 2 AZs.
- Bootstrap via `user_data` to install Docker, log in to ECR, and run the app container.
- Be part of the ALB Target Group for load balancing.

## 🎯 Consequences

**Pros:**

- Simple to reason about: ALB → ASG → RDS matches many AWS reference architectures.
- Demonstrates raw AWS building blocks (networking, security groups, IAM, scaling).
- Easier for portfolio storytelling and teaching HA concepts.
- No extra managed service learning curve (ECS/EKS control plane).

**Cons:**

- Less efficient scaling vs ECS/EKS (entire VM vs container tasks).
- Higher ops burden (patching AMIs, handling Docker runtime).
- Less portable: tightly coupled to EC2 implementation.
- Not “cloud native” in the strictest sense (missing service mesh, task placement).

## 🔄 Alternatives Considered

1. **ECS (Fargate)**

   - + No server management, true pay-for-use.
   - – Less visibility into networking/security primitives for learning.
   - – Adds complexity with task definitions and service discovery.
2. **EKS (Kubernetes)**

   - + Rich ecosystem, industry standard orchestration.
   - – High operational complexity, especially for a single demo service.
   - – Overkill for learning HA basics; more moving parts to explain.
3. **Run directly on EC2 (no ASG)**

   - + Simplest possible.
   - – No automatic failover or scaling; not HA.
