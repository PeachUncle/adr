# ADR-004: Azure Container Apps Production Deployment

**Status:** Active  
**Date:** 2025-08-09  
**Authors:** AI Development Partner  
**Supersedes:** N/A  

## Context

Following successful completion of the RESTRUCTURE-PLAN.md and achievement of production-ready Discord Publish Bot functionality, we need to deploy the system to a production environment. The system currently runs successfully in development with:

- ✅ Modern `discord_publish_bot` package structure
- ✅ Comprehensive test suite (76 tests, 15/15 core passing)
- ✅ Security isolation (4/4 security tests passing)
- ✅ Clean entry points and CLI interfaces
- ✅ All 4 post types functional with branch/PR workflow

The original specifications mentioned Fly.io deployment, but research indicates Azure Container Apps provides superior integration with the target ecosystem and better operational capabilities.

## Decision

We will deploy the Discord Publish Bot to **Azure Container Apps** for production hosting.

### Technology Stack
- **Container Platform:** Azure Container Apps
- **Base Image:** Python 3.11-slim with multi-stage build
- **Orchestration:** Azure Container Apps Environment
- **Monitoring:** Azure Application Insights + Log Analytics
- **Secrets Management:** Azure Container Apps secrets + Key Vault
- **CI/CD:** GitHub Actions with Azure deployment

### Architecture
```
Discord Platform
       ↓ HTTP Interactions (webhook)
Azure Application Gateway
       ↓ HTTPS/SSL termination  
Azure Container Apps Environment
       ├── Container App (discord-publish-bot)
       ├── Log Analytics Workspace
       └── Application Insights
       ↓ GitHub API calls
GitHub Repository
       ↓ Static site generation
Production Website
```

## Rationale

### Why Azure Container Apps over Fly.io

**✅ Advantages of Azure Container Apps:**
1. **Native Azure Integration:** Better integration with Azure ecosystem (Key Vault, Application Insights, Log Analytics)
2. **Scaling Capabilities:** Built-in auto-scaling with detailed configuration options
3. **Security:** Integrated security features, managed identities, secure secrets management
4. **Monitoring:** First-class observability with Application Insights and Azure Monitor
5. **Cost Optimization:** Pay-per-use pricing model, automatic scale-to-zero
6. **Enterprise Ready:** Better compliance, SLA guarantees, enterprise security features

**⚠️ Trade-offs:**
1. **Complexity:** Slightly more complex initial setup compared to Fly.io
2. **Learning Curve:** Requires Azure-specific knowledge
3. **Vendor Lock-in:** Tighter coupling to Azure ecosystem

### Architecture Decisions

**Container Strategy:**
- Multi-stage Docker build for optimized production images
- Non-root user for security
- Health check endpoints for Azure probes
- Minimal base image for security and performance

**Environment Configuration:**
- Azure Container Apps secrets for sensitive data (Discord tokens, GitHub tokens)
- Environment-specific configuration through Azure App Configuration
- Managed identity for secure Azure service access

**Monitoring and Observability:**
- Application Insights for application performance monitoring
- Log Analytics for centralized logging and alerting
- Custom metrics for Discord interactions and GitHub publishing success rates
- Health check endpoints for Azure health probes

**Security:**
- Azure Key Vault for secret storage
- Container Apps secrets for runtime secret injection  
- Network security groups for traffic control
- HTTPS-only communication with proper TLS configuration

## Implementation Plan

### Phase 1: Container Optimization (Day 1)
- Enhance Dockerfile for production use
- Create production environment configuration
- Implement Azure-specific health checks

### Phase 2: Azure Resource Setup (Day 1-2)  
- Create Container Apps Environment
- Configure Log Analytics and Application Insights
- Set up Key Vault for secrets management
- Create Container App with proper configuration

### Phase 3: CI/CD Pipeline (Day 2-3)
- GitHub Actions workflow for automated deployment
- Azure service principal configuration
- Infrastructure as Code using Azure Bicep
- Deployment validation and testing

### Phase 4: Production Validation (Day 3-4)
- End-to-end testing with production Discord application
- GitHub integration validation
- Performance and load testing
- Security validation and penetration testing

### Phase 5: Operations (Day 4-5)
- Monitoring dashboards and alerting
- Operational runbooks and procedures
- Backup and disaster recovery procedures
- Documentation and handoff

## Consequences

### Positive
- ✅ **Scalability:** Auto-scaling based on demand with scale-to-zero capabilities
- ✅ **Reliability:** Azure SLA guarantees and built-in redundancy
- ✅ **Security:** Enterprise-grade security with managed identities and Key Vault integration
- ✅ **Observability:** Comprehensive monitoring with Application Insights and Azure Monitor
- ✅ **Cost Efficiency:** Pay-per-use pricing model, no idle costs
- ✅ **Integration:** Native Azure ecosystem integration for future enhancements
- ✅ **Maintenance:** Managed platform reduces operational overhead

### Negative
- ⚠️ **Complexity:** More complex setup process compared to simpler platforms
- ⚠️ **Learning Curve:** Requires Azure-specific knowledge and best practices
- ⚠️ **Vendor Lock-in:** Increased coupling to Azure ecosystem
- ⚠️ **Cost Monitoring:** Need to monitor Azure costs across multiple services

### Risk Mitigation
- **Knowledge Gap:** Comprehensive documentation and runbook creation
- **Cost Control:** Implement cost monitoring and alerts
- **Vendor Lock-in:** Design for portability with containerized approach
- **Complexity:** Use Infrastructure as Code for reproducible deployments

## Follow-up Actions

1. **Immediate (Day 1):**
   - Enhance Dockerfile for Azure Container Apps
   - Research Azure Container Apps best practices and limitations
   - Create environment configuration templates

2. **Short-term (Week 1):**
   - Deploy to Azure Container Apps environment
   - Configure monitoring and alerting
   - Validate end-to-end functionality

3. **Medium-term (Month 1):**
   - Optimize performance and cost
   - Implement advanced monitoring and dashboards
   - Create comprehensive operational procedures

4. **Long-term (Quarter 1):**
   - Evaluate scaling patterns and optimization opportunities
   - Consider advanced Azure features (Application Gateway, CDN)
   - Plan for disaster recovery and multi-region deployment

## Success Metrics

- ✅ **Deployment Success:** Application successfully deployed and accessible
- ✅ **Functional Validation:** All Discord interactions and GitHub publishing working
- ✅ **Performance:** <2 second response time for Discord interactions
- ✅ **Reliability:** 99.9% uptime over first month
- ✅ **Security:** No security incidents or credential exposure
- ✅ **Cost Efficiency:** Monthly costs under target budget
- ✅ **Monitoring:** Complete observability with alerting and dashboards

## Related Documents

- **Deployment Plan:** `projects/active/azure-container-apps-deployment.md`
- **Technical Specification:** `specs/technical/discord-publish-bot-technical-spec.md`
- **Security Guidelines:** `docs/team/security-guidelines.md`
- **Project Completion:** `projects/archive/discord-publish-bot-COMPLETED-2025-08-08.md`

---

*This ADR captures the decision to use Azure Container Apps for production deployment, including rationale, implementation plan, and success criteria.*
