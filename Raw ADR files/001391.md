## ADR 011: Database Hosting — Amazon RDS for PostgreSQL

### Context
Our previous approach **self-hosted PostgreSQL in Docker on an EC2 instance**. While this unified our stack and reduced short-term cost, it also led to recurring **connection instability**, **manual maintenance overhead** (backups, upgrades, failover), and **operational complexity** as usage grew.  
These issues began to affect development velocity and reliability for user-facing features.

### Decision
We decided to **migrate the PostgreSQL database to Amazon RDS (PostgreSQL)**.  
RDS offers a managed control plane with automated backups, patching, and simpler vertical scaling, improving stability and reducing day-to-day ops work.

### Status
**Accepted — Implemented**

### Rationale for Change
- **Operational Stability:** Managed patching, failover options (Multi-AZ), and health monitoring reduce on-call burden and production incidents.  
- **Automated Backups & Point-in-Time Restore:** Out-of-the-box snapshots and PITR simplify recovery planning.  
- **Easier Scaling:** Instance class and storage can be adjusted without re-architecting our deployment pipeline.  
- **Reduced Maintenance Load:** No more hand-rolled backup scripts, manual upgrades, or container/volume babysitting.  
- **Security & Access Controls:** Security groups, parameter groups, and optional IAM authentication provide clear guardrails.

### Consequences

**Positive:**
1. **Higher reliability** (managed service, optional Multi-AZ) and fewer connection/maintenance incidents.  
2. **Built-in backups and PITR**, simplifying disaster recovery.  
3. **Faster environment changes** (instance/storage scaling, parameter tuning via parameter groups).  
4. **Cleaner CI/CD** for the app—database lifecycle is decoupled from app containers.  

**Negative / Risks:**
1. **Higher monthly cost** than self-hosting at low scale.  
2. **Reduced superuser control** (cannot use `postgres` superuser; some extensions/settings are restricted).  
3. **Vendor lock-in & limits** around custom runtime configuration.  
4. **Network considerations:** Must ensure proper VPC/Subnet/Security Group setup; slight latency versus localhost container networking.  

### Future Considerations
- **Enable Multi-AZ** and/or **read replicas** as traffic grows; consider **RDS Proxy** for connection pooling from serverless/auto-scaled clients.  
- Monitor cost with **budgets/alerts**; revisit sizing or **Aurora PostgreSQL** if we need better autoscaling or read scalability.  
- Formalize **maintenance windows** and **upgrade cadence**; validate PITR regularly with restore drills.  
- Harden security posture (least-privilege DB roles, rotation policy; consider **IAM auth** if it fits our stack).
