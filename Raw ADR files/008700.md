# ADR-009: Azure Container Apps Production Deployment

## Status
**ACCEPTED** - Implemented 2025-08-10

## Context

Following the successful completion of Phase 1 (container optimization and test infrastructure stabilization), we needed to deploy the Discord Publish Bot to Azure Container Apps for production use. This decision implements the deployment strategy outlined in ADR-004 with enhanced security and cost optimization.

## Decision

We will deploy the Discord Publish Bot to Azure Container Apps with the following production configuration:

### Infrastructure Architecture
- **Resource Group**: `rg-<project-name>-prod` (<Azure Region>)
- **Container Apps Environment**: `cae-<project-name>-prod` 
- **Container App**: `ca-<project-name>`
- **Log Analytics**: Auto-created workspace for monitoring

### Security Configuration
- **Secrets Management**: Azure Container Apps secrets for all sensitive data
- **Environment Variables**: Configured to reference secrets (no plaintext credentials)
- **Managed Identity**: System-assigned managed identity for Azure resource access
- **Container Security**: Non-root user (UID/GID 1000) following security best practices

### Cost Optimization
- **Scale-to-Zero**: Configured with 0 minimum replicas, 2 maximum replicas
- **Resource Allocation**: 0.5 CPU, 1GB memory for efficient cost management
- **Consumption Plan**: Workload profile optimized for intermittent Discord bot usage

### Deployment Process
1. **Azure CLI Authentication**: Using Azure subscription with appropriate permissions
2. **Secrets Setup**: Used `scripts/azure-secrets-setup.ps1` to securely configure secrets from `.env.production`
3. **Container Deployment**: Used `az containerapp up` with source-based deployment
4. **Environment Configuration**: Set environment variables to reference Azure secrets
5. **Health Validation**: Verified endpoints and production status

## Production Endpoints

### Live Endpoints (2025-08-10)
- **Status**: Production deployment successful with external ingress configured
- **Health Check**: `/health` endpoint - Returns comprehensive status including Discord/GitHub configuration
- **API Root**: `/` endpoint - Service information and available endpoints
- **Discord Interactions**: `/discord/interactions` endpoint - Ready for Discord webhook configuration
- **Publishing API**: `/api/publish` endpoint - Ready for GitHub integration

### Health Status Verification
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "environment": "production", 
  "discord_configured": true,
  "github_configured": true,
  "github_connectivity": null,
  "timestamp": "2025-08-10T19:51:53.216509"
}
```

## Implementation Details

### Azure Resources Created
```bash
# Resource Group
az group create --name rg-<project-name>-prod --location <azure-region>

# Container Apps Environment with Log Analytics
az containerapp env create \
  --name cae-<project-name>-prod \
  --resource-group rg-<project-name>-prod \
  --location <azure-region>

# Container App Deployment from Source
az containerapp up \
  --name ca-<project-name> \
  --resource-group rg-<project-name>-prod \
  --location <azure-region> \
  --environment cae-<project-name>-prod \
  --source . \
  --ingress external \
  --target-port 8000

# Scale-to-Zero Configuration
az containerapp update \
  --name ca-<project-name> \
  --resource-group rg-<project-name>-prod \
  --min-replicas 0 \
  --max-replicas 2
```

### Secrets Configuration
Using the secure setup script, the following secrets were configured:
- `discord-bot-token`: Discord bot authentication token
- `discord-application-id`: Discord application ID for interactions
- `discord-public-key`: Discord public key for webhook verification
- `discord-user-id`: Authorized Discord user ID
- `github-token`: GitHub personal access token for repository operations
- `github-repo`: Target GitHub repository for publishing
- `api-key`: Secure API key for authentication

### Environment Variables
```bash
DISCORD_BOT_TOKEN=secretref:discord-bot-token
DISCORD_APPLICATION_ID=secretref:discord-application-id  
DISCORD_PUBLIC_KEY=secretref:discord-public-key
DISCORD_USER_ID=secretref:discord-user-id
GITHUB_TOKEN=secretref:github-token
GITHUB_REPO=secretref:github-repo
API_KEY=secretref:api-key
ENVIRONMENT=production
```

## Consequences

### Positive
- **Production Ready**: Discord bot is live and responding to health checks
- **Security Compliant**: All secrets managed through Azure Container Apps secrets
- **Cost Optimized**: Scale-to-zero configuration minimizes charges during idle periods
- **Monitoring Enabled**: Log Analytics workspace provides comprehensive logging
- **Scalable Architecture**: Can handle increased load with automatic scaling
- **Research Validated**: Implementation follows Microsoft documentation best practices

### Considerations
- **Next Phase Required**: Discord webhook URL needs to be configured in Discord Developer Portal
- **CI/CD Pipeline**: Automated deployment pipeline needed for ongoing updates
- **Monitoring Setup**: Application Insights integration for advanced monitoring
- **Custom Domain**: May want to configure custom domain for production use

### Risks Mitigated
- **Container Registry**: Azure Container Registry automatically created and managed
- **Image Security**: Multi-stage Docker build with security hardening implemented
- **Secret Exposure**: No plaintext credentials in environment or logs
- **Resource Isolation**: Dedicated resource group for production resources

## Next Steps

### Phase 3: CI/CD Pipeline (Estimated 2-3 hours)
1. Create GitHub Actions workflow for automated deployment
2. Configure Azure service principal for GitHub Actions
3. Set up infrastructure as code with Bicep templates
4. Implement automated testing in deployment pipeline

### Phase 4: Production Integration (Estimated 1-2 hours)  
1. Update Discord application Interactions Endpoint URL
2. Configure Discord bot for production use
3. Test end-to-end Discord → Azure → GitHub workflow
4. Validate performance and response times

### Phase 5: Monitoring and Operations (Estimated 1 hour)
1. Configure Application Insights for detailed telemetry
2. Set up alerting for critical errors and performance issues
3. Create operational dashboard in Azure Portal
4. Document runbook for ongoing operations

## References

- [ADR-004: Azure Container Apps Deployment](./adr-004-azure-container-apps-deployment.md)
- [ADR-008: Test Infrastructure Stabilization](./adr-008-test-infrastructure-stabilization.md)
- [Azure Container Apps Documentation](https://docs.microsoft.com/azure/container-apps/)
- [Container Apps Scale-to-Zero](https://docs.microsoft.com/azure/container-apps/scale-app)
- [Container Apps Secrets Management](https://docs.microsoft.com/azure/container-apps/manage-secrets)

## Security Completion ✅

### Git History Security Cleanup
- **Date**: 2025-08-10
- **Status**: ✅ COMPLETED
- **Tool**: git-filter-repo v2.47.0
- **Actions**: 
  - All email addresses anonymized to generic developer accounts
  - All credential fragments and tokens completely removed
  - All Azure infrastructure details replaced with example names
  - All GitHub profile references replaced with example URLs
- **Verification**: 0 sensitive patterns found in entire Git history
- **Result**: Repository is **SAFE FOR PUBLIC GITHUB PUBLICATION**

### Documentation Security
- **ADR-009**: Infrastructure details sanitized ✅
- **Test Files**: All credential fragments replaced ✅  
- **Configuration**: All example values implemented ✅
- **Reports**: Comprehensive security documentation complete ✅

---
**Decision Date**: 2025-08-10
**Status**: Implemented, Validated, and Security Hardened ✅
**Security Status**: 🟢 PUBLICATION READY
**Next Review**: After Phase 3 CI/CD Pipeline Implementation
