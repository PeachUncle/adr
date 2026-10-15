# Architecture Decision Record (ADR)

**ADR #:** 001  
**Title:** Infrastructure Stack and Deployment Strategy for Course Management Tool  
**Date:** 2025-11-04  
**Status:** Proposed  

---

## 1. Context

Large software engineering courses require tools to reduce administrative overhead—specifically, automating attendance tracking, communication, group contribution tracking, and fair evaluation.  

The project must be developed and deployed within **5 weeks** with **limited team availability**, so infrastructure choices must prioritize:
- **Fast setup and low maintenance**
- **Ease of deployment and rollback**
- **Scalability for course-size loads**
- **Developer onboarding simplicity**
- **Cost efficiency**, ideally staying within the **AWS/Azure free tier** for initial deployment

The backend is built on **Node.js v24.11.0 (LTS)** and **Express 5.1.0**, with **PostgreSQL** as the database. The team needs a consistent development environment and a reliable, cloud-based production deployment.

---

## 2. Decision

We will:
- **Containerize** the entire backend service using **Docker** for environment consistency across developers and production.  
- **Deploy** the Dockerized application to an **AWS EC2** (or Azure equivalent) instance for managed hosting and scalability.  
- Use **Docker Compose** for local development to orchestrate Node.js + PostgreSQL services.  
- Implement a **simple CI/CD pipeline** that automatically builds Docker images and deploys to the EC2 instance when changes are merged into the main branch.  

This approach balances speed, reliability, cost-effectiveness, and maintainability while staying within project constraints.

---

## 3. Alternatives Considered (with Cost Implications)

### **Option 1: AWS Lambda (Serverless)**
-  Pros: Scales automatically, no server management, good for low-traffic workloads.  
-  Cons: Requires code restructuring, complex setup for Express-based apps, potential cold-start latency.  
-  **Cost Implications:** Within AWS free tier for limited traffic (1M free requests/month + 400,000 GB-seconds). Beyond that, cost grows per request—affordable for classroom scale but could rise for large student cohorts.

---

### **Option 2: Kubernetes (EKS / AKS)**
-  Pros: Highly scalable, production-grade orchestration.  
-  Cons: Overkill for 5-week project; significant setup and maintenance complexity.  
-  **Cost Implications:** Not feasible under free tier. EKS control plane costs ~$74/month (AWS) plus node instances. Azure AKS has a free control plane but VM costs still apply. High long-term cost unless heavy automation is needed.

---

### **Option 3: Traditional VM without Docker**
-  Pros: Simple to deploy, minimal setup.  
-  Cons: Environment inconsistencies, manual dependency management, harder CI/CD integration.  
-  **Cost Implications:** Could use free-tier EC2/Azure VM for basic hosting (t2.micro or B1s). Cost increases if higher-tier instances or data transfer spikes occur. Minimal storage (EBS) and bandwidth charges possible after free limits.

---

### **Option 4: EC2 + Docker (Chosen Option)**
-  Pros: Reproducible environments, simple Docker-based deployments, works well with CI/CD.  
-  Cons: Requires instance management and monitoring.  
-  **Cost Implications:** Fits comfortably within AWS/Azure free tier for moderate student usage.  
  - **Example AWS Free Tier Estimate:**  
    - EC2 t2.micro (750 hours/month) — free  
    - 30GB EBS storage — free  
    - RDS (PostgreSQL) 750 hours — free  
    - Total projected cost: **$0–$5/month** (depending on data transfer and storage growth).  
  - **Long-Term:** Scales to ~$10–20/month for persistent, moderate usage outside free limits.

**Chosen Option:** EC2 + Docker — best balance between cost, speed, and maintainability.

---

## 4. Consequences

### Positive Outcomes
- Consistent dev → prod environments using Docker images.  
- Easier onboarding for new team members (one Docker command setup).  
- Straightforward deployment pipeline compatible with GitHub Actions.  
- Cloud-hosted and accessible for course staff and students.  
- Low or zero hosting cost within free tier during early deployment.

### Negative Outcomes / Trade-offs
- Slightly higher EC2 maintenance overhead (monitoring, security updates).  
- Manual scaling if load increases substantially.  
- CI/CD requires secure handling of secrets (AWS credentials, DB connection).  
- Possible minimal cost once usage exceeds free-tier limits.

---

## 5. Implementation Notes

- **Environment:**  
  - `Dockerfile` for Node.js backend  
  - `docker-compose.yml` for local stack (backend + PostgreSQL)  

- **Deployment Flow:**  
  - Push to `backend/main` → GitHub Actions builds Docker image → Push to registry → Deploy to EC2 via SSH or ECS.  
  - PostgreSQL hosted either via RDS (recommended) or on same EC2 instance initially.  

- **Security & Monitoring:**  
  - Use `.env` files with secrets injected via CI/CD.  
  - Configure HTTPS using Nginx reverse proxy + Certbot (if time allows).  
  - Use CloudWatch or Azure Monitor for basic uptime metrics.  

- **Scalability Path (Future ADRs):**  
  - Option to migrate EC2 → ECS or EKS if user base grows.  
  - Add load balancer and auto-scaling group when multi-section classes onboard.

---

## 6. References
- [Node.js 24.11.0 LTS Docs](https://nodejs.org/en/blog/release/v24.11.0)  
- [Express 5.1.0 Documentation](https://expressjs.com/en/5x/api.html)  
- [Docker Docs](https://docs.docker.com/)  
- [AWS EC2 Deployment Guide](https://docs.aws.amazon.com/ec2/)  
- [AWS Free Tier Pricing](https://aws.amazon.com/free/)  
- [Azure Free Services](https://azure.microsoft.com/en-us/free/)  
- [GitHub Actions for Node.js + Docker CI/CD](https://docs.github.com/en/actions/publishing-packages/publishing-docker-images)
