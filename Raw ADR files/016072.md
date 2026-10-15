---
id: 001
status: "proposed"
supersedes: null
superseded_by: null
---

# Decision Record 001: Game Platform Implementation Approach

## Context

We need to implement a game platform to host game servers, starting with Minecraft as the initial test case. The platform needs to be reliable, maintainable, and cost-effective while supporting our goal of hosting playable game servers.

This is part of a developer course where students will be the primary implementers, with instructor backing. The work will be done during weekly social time, so the approach should balance learning value with fun factor. Students should be able to put this experience on their CVs and include it in their portfolios, making the technical depth and real-world applicability important considerations.

## Decision

We need to choose between four implementation approaches:

### 1. Pay for existing game host provider

This approach uses commercial game hosting services like Apex Hosting, Shockbyte, or similar providers. The team would simply pay for hosting and configure game servers through web interfaces.

**Note:** Not viable due to zero learning opportunities. While it would work for hosting games, it provides no technical depth or modern infrastructure experience for the team.

**Pros:**

- Zero setup time and maintenance overhead
- Professional support and reliability
- No infrastructure knowledge required
- Predictable costs

**Cons:**

- Limited customization and control
- Ongoing subscription costs
- Vendor lock-in
- **No modern infrastructure learning** - lacks IaC, GitOps, automation
- **Limited portfolio value** - no technical depth to showcase
- **No developer workflow experience** - missing CI/CD, version control practices

### 2. Manual server management

This approach involves requisitioning servers (e.g., from Hetzner, DigitalOcean) and manually configuring them via SSH. The team would install game servers, manage updates, and handle maintenance through direct server access.

**Note:** Possibly useful for exploration of how servers work and networking configuration. Could serve as a learning exercise for understanding server fundamentals, but limited long-term value.

**Pros:**

- Full control over configuration
- No vendor lock-in
- Direct SSH access for troubleshooting
- Simple to understand and debug

**Cons:**

- High manual maintenance overhead
- No infrastructure as code
- Difficult to reproduce environments
- Scaling requires manual work
- **No modern DevOps practices** - missing automation, IaC, GitOps
- **Limited scalability learning** - manual processes don't scale
- **No industry-standard tooling** - missing Terraform, Kubernetes, etc.

### 3. IaC/GitOps-lite (OpenTofu/Terraform)

This approach uses Infrastructure as Code for fully reproducible setups. The team would define infrastructure in OpenTofu, use CloudInit for server configuration, and Docker Compose for application orchestration. SSH would only be used as a debug escape hatch, not for regular operations.

**Note:** Recommended first implementation due to simplicity and reproducibility. Provides good balance of learning value and practical skills while being achievable within the course timeframe.

**Pros:**

- **Good learning progression** - builds on OpenTofu knowledge
- **Balanced complexity** - not too simple, not overwhelming
- **Portfolio value** - modern IaC practices, infrastructure automation
- **Practical skills** - directly applicable to real-world scenarios
- **Manageable scope** - can be implemented and understood within course timeframe
- **Fully reproducible** - complete infrastructure and application setup as code
- **Docker Compose orchestration** - containerized game servers with service management
- **CloudInit automation** - servers self-configure on boot

**Cons:**

- **No feedback loops** - systems don't self-correct or adapt to changes
- **Manual intervention required** - updates, monitoring, scaling all need human action
- **Push-based deployment model** - not fully GitOps reconciliation
- **State management complexity** - OpenTofu state handling
- **Scaling challenges** - manual scaling decisions and server management

### 4. Full GitOps (Kubernetes)

This approach uses Kubernetes for cybernetic control with full GitOps reconciliation. The team would use a single management plane node for control and dedicated game server instances (number depending on how many game servers we want to support) with sidecars for extensions (monitoring, logging, etc.). Everything is containerized and defined declaratively with operators for continuous observation, feedback loops, and self-healing.

**Note:** Advised for long-term projects, highly extensible and advanced, modern, operations approach that provides maximum learning value and industry-relevant skills, but may be complex for initial implementation.

**Pros:**

- **Maximum learning value** - Kubernetes, operators, GitOps patterns
- **Industry standard** - highly valuable for portfolios and CVs
- **Advanced skills** - what students will need for senior roles
- **Future-proof** - scales to any complexity level
- **Continuous feedback loops** - systems observe, adapt, and self-correct automatically
- **Self-healing capabilities** - automatic recovery and management
- **Excellent day 2 operations** - automated updates, monitoring, logging, scaling
- **Easy extensibility** - IAM, observability, message buses integrate seamlessly
- **Scalable architecture** - single management plane + dedicated game server instances (scales based on needs)
- **Sidecar pattern** - extensions (monitoring, logging) as sidecars, not main containers
- **Declarative management** - everything as code, true GitOps workflow

**Cons:**

- **Steep learning curve** - Kubernetes complexity
- **Operational complexity** - more moving parts to manage
- **Risk of overwhelming** - might be too advanced for the scope and timeframe
- **Resource overhead** - Kubernetes itself requires resources (but manageable on single node)
