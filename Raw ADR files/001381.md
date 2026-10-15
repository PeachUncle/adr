# ADR: Containerization, Image Tagging by Commit SHA, and Database Choice

- **Date**: 2025-09-22  
- **Status**: Accepted  

---

## Context

The project requires strong **traceability** between the source code and the deployed runtime.  
We also need a relational database for persistence, ensuring compatibility with AWS managed services and developer familiarity.  

Two key architectural areas were addressed in this decision record:  
1. **How to containerize and tag application images** for reproducibility.  
2. **Which relational database engine to use** for long-term maintainability.  

---

## Decision

### Containerization & Image Tagging
- All services will be packaged as **Docker images**.  
- Each image built in CI will be tagged with the **Git commit SHA** that produced it.  
  - Example: `ghcr.io/<owner>/<repo>:abc1234`.  
- Images are published initially to **GitHub Container Registry (GHCR)**.  
- For Continuous Deployment (CD), images will also be published to **Amazon Elastic Container Registry (ECR)**.  

This guarantees a **1:1 relationship** between code, Docker image, and deployed service.  

### Database Choice
- Instead of PostgreSQL, the project will use **MySQL** as the primary relational database engine.  
- MySQL is fully managed by AWS via **Amazon RDS** and widely supported in the .NET ecosystem.  
- Service schemas will be separated logically (e.g., `auth`, `catalog`, `cart`) within MySQL.  

---

## Alternatives Considered

### Image Tagging
1. **Semantic version tags** (`v1.2.3`)  
   - ✅ Human-readable, easy to reference in release notes.  
   - ❌ Risk of drift or human error if tags are not consistently applied.  

2. **Branch-based tags** (`feature-login:latest`)  
   - ✅ Provides visibility into branch builds.  
   - ❌ Not uniquely traceable; multiple commits per branch may override the same tag.  

**Chosen:** Commit SHA tagging (with optional semantic tags for readability).  

### Database Engine
1. **PostgreSQL**  
   - ✅ Rich feature set (JSONB, advanced indexes).  
   - ❌ Slightly heavier learning curve for developers more familiar with MySQL.  
   - ❌ Team consensus preferred MySQL for simplicity.  

2. **MySQL**  
   - ✅ Broad adoption, strong AWS RDS support, developer familiarity.  
   - ✅ Meets functional requirements without over-engineering.  
   - ❌ Fewer advanced features compared to PostgreSQL.  

**Chosen:** MySQL.  

---

## Consequences

### Image Tagging
- ✅ Easy auditing: commit ↔ image ↔ deployment is always clear.  
- ✅ Rollbacks are simple: redeploy by SHA.  
- ❌ Tags are not human-friendly by default (mitigation: add **additional semantic or branch tags** if needed).  

### Database Choice
- ✅ Simplified onboarding due to MySQL familiarity.  
- ✅ Native AWS RDS integration.  
- ✅ Well-supported ORM integrations in .NET (e.g., EF Core).  
- ❌ Some advanced features (e.g., PostgreSQL JSONB) are not available. The design must remain mindful of MySQL’s constraints.  

---  
