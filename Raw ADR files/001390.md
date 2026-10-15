## ADR 009: Database Hosting — Dockerized PostgreSQL on EC2

### Context
Our initial approach used **Amazon RDS** to host the PostgreSQL database. While RDS provides a managed service with automatic backups, replication, and maintenance, it also introduces higher costs and less control over runtime configuration.  
As the team moved toward a fully containerized workflow, we found that keeping RDS separate from our Docker-based backend introduced unnecessary complexity in CI/CD and development environments.

### Decision
We decided to **containerize PostgreSQL within our Docker environment** and **host it directly on an Amazon EC2 instance** alongside our FastAPI backend.  
This change unifies our infrastructure into a single deployment pipeline and simplifies integration between services during development, testing, and production.

### Status
**Accepted — Implemented** for MVP and short-term production.

### Rationale for Change
- **Simplified CI/CD:** Running PostgreSQL as a Docker container enables identical configurations between local and cloud environments, eliminating deployment drift.  
- **Cost Efficiency:** Self-hosting the database on EC2 significantly reduces AWS billing compared to RDS, which is overkill for an MVP.  
- **Faster Iteration:** The Dockerized setup allows rapid re-deployment, rollback, and testing without managing RDS instances separately.  
- **Improved Integration:** The backend, database, and API services now live within one orchestrated environment, simplifying container networking and version control.

### Consequences

**Positive:**
1. Consistent development and production environments via Docker.
2. Reduced operational cost and simplified setup.
3. Easier CI/CD integration and faster deployment cycles.
4. Greater control over database configuration, versioning, and scaling strategy.

**Negative / Risks:**
1. Manual responsibility for backups, monitoring, and recovery.
2. Potential downtime risk without RDS’s built-in high availability.
3. Requires proper Docker volume management to ensure data persistence.

**Future Considerations:**
- As the application scales, we may **migrate back to Amazon RDS or Aurora** for managed reliability and automated backup capabilities.
- Implement database snapshot automation and external monitoring (CloudWatch + custom scripts) to mitigate operational risks.
