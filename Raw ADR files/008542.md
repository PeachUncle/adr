# ADR-002: Azure OpenAI Integration with Entra ID Authentication

**Date**: 2025-12-31  
**Updated**: 2026-01-01 (Added API Key support for development)  
**Status**: Accepted (Amended)  
**Decision Makers**: Architecture Team, Security Team  
**Technical Story**: Secure Azure OpenAI Integration

## Context

CV Checker requires integration with Azure OpenAI Service to power its AI agents with the gpt-4.1 model. The application needs:

- Secure authentication to Azure OpenAI endpoints
- Support for multiple environments (dev, staging, production)
- Compliance with enterprise security policies
- No hardcoded API keys in source code
- Easy local development experience
- Support for CI/CD pipelines

Azure OpenAI Service supports two authentication methods:

1. **API Key Authentication**: Simple but requires key management and rotation
2. **Entra ID (Azure AD) OAuth**: Role-based access control with managed identities

## Decision

We will use **Azure OpenAI gpt-4.1 model** with flexible authentication supporting **both API Key and Entra ID OAuth** via **DefaultAzureCredential**.

### Amendment (2026-01-01): API Key Support Added

**Original Decision:** Entra ID only  
**Updated Decision:** Support both authentication methods with preference order:

1. **API Key** (if `AZURE_OPENAI_API_KEY` environment variable is set) - Used for development and simple deployments
2. **Entra ID** (via `DefaultAzureCredential`) - Used for production with managed identities

**Rationale for Amendment:**

- Developer experience: API keys from Azure Portal are simpler than Entra ID setup for local development
- Flexibility: Organizations can choose based on security requirements
- Pragmatism: Tenant mismatch errors blocked development; API keys unblock immediately
- Security maintained: Production can still use Entra ID; development uses time-limited keys

**Implementation:** Client initialization checks for API key first, falls back to DefaultAzureCredential if not present.

### Configuration Management

- Model deployment name, endpoint, and API version configured via environment variables
- No secrets in source code or configuration files
- Use Azure Key Vault for sensitive configuration in production
- Support for multiple credential sources through DefaultAzureCredential chain

### Why Entra ID Over API Keys

**API Key authentication rejected** because:

- Requires manual key rotation and management
- Keys can be accidentally committed to source control
- No granular permission control
- Difficult to audit access
- Non-compliant with zero-trust security model

**Entra ID authentication chosen** because:

- Leverages managed identities in Azure environments
- Supports role-based access control (RBAC)
- Automatic credential rotation
- Full audit trail in Azure AD logs
- Works seamlessly with DefaultAzureCredential for local dev
- Aligns with enterprise security standards
- No secrets management overhead

### Why gpt-4.1

- Latest GPT-4 model with improved reasoning
- Better structured output generation
- Optimized for JSON mode
- Enhanced instruction following for agent tasks
- Cost-effective balance of performance and price

## Implementation

(Updated 2026-01-01)

```python
import os
from azure.identity import DefaultAzureCredential
from agent_framework.azure import AzureOpenAIChatClient
from typing import Optional

class AzureOpenAIConfig:
    """Azure OpenAI configuration manager."""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4-1")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")  # Optional
        
        if not self.endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable not set")
    
    def create_client(self) -> AzureOpenAIChatClient:
        """
        Create Azure OpenAI client with flexible authentication.
        
        Authentication options (in priority order):
        1. API Key: If AZURE_OPENAI_API_KEY is set, uses key-based authentication
        2. Entra ID: Uses DefaultAzureCredential which tries in order:
           - Environment variables (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
           - Managed Identity (for Azure-hosted apps)
           - Azure CLI (az login)
           - Visual Studio Code Azure extension
        
        Returns:
            AzureOpenAIChatClient from Microsoft Agent Framework
        """
        # Check if API key is available
        if self.api_key:
            logger.info("Creating Azure OpenAI client with API key")
            client = AzureOpenAIChatClient(
                api_key=self.api_key,
                endpoint=self.endpoint,
                deployment_name=self.deployment,
                api_version=self.api_version,
            )
        else:
            logger.info("Creating Azure OpenAI client with DefaultAzureCredential")
            # Create credential for Entra ID authentication
            credential = DefaultAzureCredential()
            client = AzureOpenAIChatClient(
                credential=credential,
                endpoint=self.endpoint,
                deployment_name=self.deployment,
                api_version=self.api_version,
            )
        
        logger.info("Azure OpenAI client created successfully")# Create token provider for Cognitive Services scope
        token_provider = get_bearer_token_provider(
            credential,
            "https://cognitiveservices.azure.com/.default"
        )
        
        client = AzureOpenAIChatCompletionClient(
            azure_deployment=self.deployment,
            azure_endpoint=self.endpoint,
            api_version=self.api_version,
            azure_ad_token_provider=token_provider,
            # Optional: customize timeout and retry settings
            timeout=60.0,
            max_retries=3
        )
        
        return client

# Usage in application
config = AzureOpenAIConfig()
openai_client = config.create_client()
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from functools import lru_cache

app = FastAPI(title="CV Checker API")

@lru_cache()
def get_openai_config() -> AzureOpenAIConfig:
    """Cached configuration instance."""
    return AzureOpenAIConfig()

@lru_cache()
def get_openai_client(
    config: AzureOpenAIConfig = Depends(get_openai_config)
) -> AzureOpenAIChatCompletionClient:
    """Cached OpenAI client instance."""
    return config.create_client()

@app.get("/health")
async def health_check(
    client: AzureOpenAIChatCompletionClient = Depends(get_openai_client)
):
    """Health check endpoint that verifies Azure OpenAI connectivity."""
    try:
        # Simple test to verify authentication and connectivity
        return {
            "status": "healthy",
            "azure_openai": "connected",
            "model": get_openai_config().deployment
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

### Azure RBAC Setup

```bash
# Assign Cognitive Services OpenAI User role to managed identity
az role assignment create \
  --role "Cognitive Services OpenAI User" \
  --assignee <managed-identity-or-user-principal-id> \
  --scope /subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/Microsoft.CognitiveServices/accounts/<openai-resource-name>

# For local development with Azure CLI
az role assignment create \
  --role "Cognitive Services OpenAI User" \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --scope /subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/Microsoft.CognitiveServices/accounts/<openai-resource-name>
```

### Docker Compose for Local Development

```yaml
version: '3.8'
services:
  cv-checker:
    build: .
    environment:
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_DEPLOYMENT=${AZURE_OPENAI_DEPLOYMENT}
      - AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION}
      # For local dev with service principal
      - AZURE_TENANT_ID=${AZURE_TENANT_ID}
      - AZURE_CLIENT_ID=${AZURE_CLIENT_ID}
      - AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET}
    ports:
      - "8000:8000"
```

## Consequences

### Positive

- **Security**: No API keys to manage or rotate
- **Compliance**: Meets enterprise zero-trust requirements
- **Auditability**: All access logged in Azure AD
- **Developer Experience**: Works seamlessly with Azure CLI and VS Code
- **Production Ready**: Managed identities in Azure App Service/Container Apps
- **Cost Optimization**: Fine-grained RBAC prevents unauthorized usage
- **Simplified Secrets Management**: No secrets in environment variables (production)

### Negative

- **Initial Setup Complexity**: Requires Azure RBAC configuration
- **Local Development**: Developers need Azure CLI or service principal setup
- **Troubleshooting**: Credential chain can be harder to debug than API keys
- **Network Dependencies**: Requires connectivity to Azure AD endpoints

### Mitigation Strategies

- **Documentation**: Comprehensive setup guide for local development
- **Error Handling**: Clear error messages for authentication failures
- **Fallback**: Development environment supports service principal credentials
- **Monitoring**: Azure Application Insights tracks authentication issues
- **Testing**: Mock credentials for unit tests

### Migration Path from API Keys

If currently using API keys:

1. Add Entra ID authentication alongside existing API key auth
2. Test in development environment
3. Deploy to staging with Entra ID only
4. Validate production deployment
5. Remove API key support
6. Rotate and delete old API keys

## Related Decisions

- ADR-001: Microsoft Agent Framework Sequential Orchestration
- ADR-003: Hybrid Scoring Algorithm

## References

- [Azure OpenAI Authentication](https://learn.microsoft.com/azure/ai-services/openai/how-to/managed-identity)
- [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential)
- [Azure RBAC for Cognitive Services](https://learn.microsoft.com/azure/ai-services/openai/how-to/role-based-access-control)
- [Microsoft Agent Framework Azure Integration](https://microsoft.github.io/autogen/docs/installation/)
