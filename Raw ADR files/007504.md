# ADR-016 – Managed Identity & RBAC Strategy: Secure Azure Service Authentication

**Status:** Accepted  
**Date:** 2025-12-01  
**Author:** Niklas Häll

---

## Context

The ticketing system integrates with multiple Azure services (App Configuration, Service Bus, Cosmos DB, Key Vault, Application Insights) that require secure authentication. Traditional approaches using connection strings or access keys present security risks:

- **Connection strings in configuration** - Exposed in code, configuration files, or environment variables
- **Access keys in Key Vault** - Still require managing and rotating secrets
- **Shared access signatures (SAS)** - Time-limited but still require secret management
- **Security vulnerabilities** - Secrets can be leaked through logs, source control, or compromised environments

**The Requirement:**
- Eliminate connection strings and access keys from code and configuration
- Use Azure-native authentication mechanisms
- Follow principle of least privilege for service access
- Enable secure, auditable access to Azure resources
- Support both local development and cloud deployment

---

## Decision

The system uses **Azure Managed Identity** with **Role-Based Access Control (RBAC)** for all Azure service authentication. No connection strings or access keys are stored in code or configuration files.

**Implementation:**

1. **Managed Identity Configuration:**
   - **App Service:** System-assigned managed identity enabled (`identity.type: 'SystemAssigned'`)
   - **Function App:** System-assigned managed identity enabled (`identity.type: 'SystemAssigned'`)
   - Both services automatically receive Azure AD service principals that can be granted RBAC roles

2. **RBAC Role Assignments:**

   **App Service Roles:**
   - **App Configuration Data Reader** - Read feature flags and configuration values
   - **App Configuration Data Owner** - Toggle feature flags (write access)
   - **Azure Service Bus Data Owner** - Publish events to Service Bus queues
   - **Application Insights Reader** - Query Application Insights logs (manually assigned)

   **Function App Roles:**
   - **Azure Service Bus Data Receiver** - Consume events from Service Bus queues
   - **DocumentDB Account Contributor** - Access Cosmos DB for event data and outbox storage

   **Key Vault:**
   - **RBAC Authorization Enabled** - Key Vault uses RBAC instead of access policies
   - App Service managed identity granted appropriate roles for secret access (via Azure Portal or Bicep)

3. **Code Implementation:**
   - **`DefaultAzureCredential`** - Used for all Azure SDK client authentication
   - Automatically discovers and uses managed identity in Azure environments
   - Falls back to Azure CLI, Visual Studio, or environment variables for local development
   - No connection strings or keys required in application code

4. **Infrastructure as Code:**
   - All RBAC role assignments defined in Bicep templates
   - Role assignments created automatically during infrastructure deployment
   - Principal IDs passed between modules to establish dependencies

---

## Consequences

**Advantages:**
- **No Secrets in Code** - Eliminates risk of connection strings or keys being exposed in source control, logs, or configuration files
- **Automatic Credential Management** - Azure manages service principal lifecycle, no manual key rotation required
- **Principle of Least Privilege** - Each service receives only the minimum permissions needed (Reader vs Owner roles)
- **Auditable Access** - All access attempts logged in Azure AD audit logs
- **Simplified Configuration** - No need to manage connection strings in Key Vault or environment variables
- **Secure by Default** - Managed identity tokens are short-lived and automatically rotated
- **Local Development Support** - `DefaultAzureCredential` supports multiple authentication methods for local development

**Disadvantages:**
- **Azure-Only Authentication** - Managed identity only works within Azure infrastructure (not for external services)
- **Role Assignment Complexity** - Requires understanding of Azure RBAC roles and proper role assignment
- **Propagation Delay** - Role assignments can take 1-2 minutes to propagate, requiring patience during setup
- **Local Development Setup** - Developers must configure Azure CLI or Visual Studio credentials for local testing
- **Bicep Deployment Dependencies** - Role assignments require principal IDs, creating deployment order dependencies

---

## Risks / Mitigations

- **Risk:** Role assignments fail during deployment if principal ID not yet available.  
  **Mitigation:** Bicep modules use conditional role assignments (`if (!empty(principalId))`) and proper `dependsOn` clauses. Function App roles use `functionApp.identity.principalId` directly (available after resource creation).

- **Risk:** Insufficient permissions cause runtime authentication failures.  
  **Mitigation:** Comprehensive role assignments defined in Bicep. Document required roles in deployment guides. Application logs authentication errors clearly. For manual assignments (e.g., Application Insights Reader), document in setup guides.

- **Risk:** Role assignment propagation delay causes temporary access failures.  
  **Mitigation:** Document expected propagation time (1-2 minutes). Implement retry logic in application code for transient authentication failures. Use polling UX (as in feature flag toggle) to indicate when permissions are ready.

- **Risk:** Local development requires Azure credentials, creating friction.  
  **Mitigation:** `DefaultAzureCredential` supports multiple fallback methods (Azure CLI, Visual Studio, environment variables). Document local setup in developer guides. Consider connection string fallback for local-only scenarios (not committed to source control).

- **Risk:** Overly permissive roles (e.g., Owner) granted for simplicity.  
  **Mitigation:** Use least-privilege roles (Reader, Data Receiver, Data Owner) as appropriate. Review role assignments in code reviews. Document why each role is necessary.

---

## Alternatives

- **Alternative 1: Connection Strings in Key Vault** - Store connection strings in Key Vault, retrieve via managed identity.  
  **Rejected:** Still requires managing connection strings. Keys can expire or be rotated, requiring application updates. Managed identity with RBAC eliminates secret management entirely.

- **Alternative 2: Access Policies (Key Vault)** - Use Key Vault access policies instead of RBAC.  
  **Rejected:** Access policies are legacy approach. RBAC provides better integration with Azure AD, centralized management, and auditability. RBAC is the recommended approach for new deployments.

- **Alternative 3: Service Principals with Client Secrets** - Create Azure AD service principals with client secrets stored in Key Vault.  
  **Rejected:** Requires managing and rotating client secrets. Managed identity eliminates secret management and provides automatic credential rotation.

- **Alternative 4: Shared Access Signatures (SAS)** - Use SAS tokens for Service Bus and Storage access.  
  **Rejected:** SAS tokens have expiration dates requiring renewal logic. Managed identity provides seamless, automatic authentication without token management.

- **Alternative 5: Hybrid Approach** - Use managed identity for some services, connection strings for others.  
  **Rejected:** Inconsistent approach increases complexity and security risk. Uniform managed identity approach simplifies architecture and improves security posture.

---

## Implementation Details

### Bicep Role Assignment Pattern

```bicep
// Example: App Service to App Configuration
resource appConfigDataReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = 
  if (!empty(appServicePrincipalId)) {
    name: guid(appConfiguration.id, appServicePrincipalId, 'App Configuration Data Reader')
    scope: appConfiguration
    properties: {
      roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 
        '516239f1-63e1-4d78-a4de-a74fb236a071')
      principalId: appServicePrincipalId
      principalType: 'ServicePrincipal'
    }
  }
```

### Code Authentication Pattern

```csharp
// Service Bus client using managed identity
services.AddSingleton<ServiceBusClient>(sp => new ServiceBusClient(
    fullyQualifiedNamespace,
    new DefaultAzureCredential()));
```

### Role Assignment Summary

| Service      | Resource            | Role                              | Purpose               |
|--------------|---------------------|-----------------------------------|-----------------------|
| App Service  | App Configuration   | Data Reader                       | Read feature flags    |
| App Service  | App Configuration   | Data Owner                        | Toggle feature flags  |
| App Service  | Service Bus         | Data Owner                        | Publish events        |
| App Service  | Application Insights| Reader                            | Query telemetry       |
| Function App | Service Bus         | Data Receiver                     | Consume events        |
| Function App | Cosmos DB           | DocumentDB Account Contributor    | Access database       |

### Local Development

For local development, `DefaultAzureCredential` attempts authentication in this order:
1. Environment variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`)
2. Managed Identity (if running in Azure)
3. Azure CLI (`az login`)
4. Visual Studio credentials
5. Azure PowerShell

Developers should use `az login` for seamless local development experience.

---

## References
- [ADR-002 - Authentication](./ADR-002-authentication.md) - User authentication strategy
- [ADR-005 - Azure Services](./ADR-005-azureservices.md) - Azure service selection and managed identity overview
- [Microsoft Docs – Managed Identity](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview)
- [Microsoft Docs – RBAC](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)
- [Microsoft Docs – DefaultAzureCredential](https://learn.microsoft.com/en-us/dotnet/api/azure.identity.defaultazurecredential)
- [Microsoft Docs – App Configuration RBAC](https://learn.microsoft.com/en-us/azure/azure-app-configuration/concept-enable-rbac)
- [Microsoft Docs – Service Bus RBAC](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-role-based-access-control)

