# ADR-033: Client-Secret Authentication over OIDC

**Status:** ✅ Accepted  
**Date:** October 2025  
**Context:** GitHub Actions Azure Authentication

## Context

GitHub Actions required authentication to Azure for deployment automation. Two options:

1. **OIDC (OpenID Connect)**: Federated identity, no secrets stored
2. **Client Secret (Service Principal)**: Traditional client ID + secret

Initial implementation used OIDC, but deployment failed:

```
Error: AADSTS50158: External security challenge not satisfied. 
Conditional Access policy requires stronger authentication.
```

**Root cause**: Organization Conditional Access Policy blocks OIDC token exchange from GitHub.

## Decision

Switched to **Client-Secret authentication** using Azure Service Principal with stored GitHub secret.

## Rationale

1. **Unblocked by Conditional Access**: Client secrets bypass CA policies
2. **Immediate deployment**: No need to reconfigure organization CA policies
3. **Azure CLI support**: Works with `azd auth login --client-secret`
4. **Stable**: No dependency on OIDC token exchange
5. **Pragmatic**: Deployment automation more important than "best practice" OIDC

## Consequences

### Positive

- **Deployments work**: No CA policy blockers
- **Simple setup**: One-time service principal creation
- **Stable**: No token exchange failures
- **Compatible**: Works with azd CLI

### Negative

- **Secret management**: Must rotate client secret every 6-12 months
- **Security risk**: Stored secret in GitHub (though encrypted)
- **Less secure than OIDC**: Secret could be compromised
- **Not "best practice"**: OIDC preferred for zero-trust

### Risks Mitigated

- Secret stored as GitHub encrypted secret (not in code)
- Service principal has minimal permissions (Contributor + User Access Administrator on resource group only)
- Secret rotation reminder in calendar (6 months)
- Audit logs track service principal usage

## Implementation

**Azure Service Principal Creation**:

```bash
# Create service principal
az ad sp create-for-rbac --name "edumind-github-deploy" \
  --role Contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/rg-edumind-dev

# Output:
{
  "clientId": "abc123...",
  "clientSecret": "xyz789...",
  "tenantId": "def456...",
  "subscriptionId": "..."
}
```

**Add User Access Administrator Role**:

```bash
# Required for azd to create role assignments
az role assignment create \
  --assignee {clientId} \
  --role "User Access Administrator" \
  --scope /subscriptions/{subscription-id}/resourceGroups/rg-edumind-dev
```

**GitHub Secrets** (Settings → Secrets and variables → Actions):

- `AZURE_CLIENT_ID` - Service principal client ID
- `AZURE_CLIENT_SECRET` - Service principal secret
- `AZURE_TENANT_ID` - Azure AD tenant ID
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID

**GitHub Actions Workflow** (.github/workflows/deploy.yml):

```yaml
- name: Azure Login
  run: |
    azd auth login \
      --client-id "${{ secrets.AZURE_CLIENT_ID }}" \
      --client-secret "${{ secrets.AZURE_CLIENT_SECRET }}" \
      --tenant-id "${{ secrets.AZURE_TENANT_ID }}"

- name: Deploy to Azure
  run: azd deploy --environment production
  env:
    AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

## OIDC Attempt (Failed)

**Previous configuration** (doesn't work with CA policies):

```yaml
permissions:
  id-token: write
  contents: read

- name: Azure Login
  uses: azure/login@v1
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

**Error received**:

```
AADSTS50158: External security challenge not satisfied. 
User account 'azd-deploy-principal' is from directory 'contoso.onmicrosoft.com'. 
The conditional access policy requires stronger authentication.
```

## Service Principal Permissions

**Minimum required roles**:

1. **Contributor**: Deploy resources (Container Apps, PostgreSQL, Redis, etc.)
2. **User Access Administrator**: Create role assignments for managed identities

**Scoped to resource group only** (not subscription-wide).

## Secret Rotation Process

**Every 6 months**:

1. Create new client secret in Azure Portal (max 24 months validity)
2. Update `AZURE_CLIENT_SECRET` in GitHub secrets
3. Test deployment with new secret
4. Delete old client secret
5. Update calendar reminder for next rotation

## Alternative Considered: Request CA Policy Exception

**Rejected because:**

- Requires organization security policy changes
- Long approval process (weeks)
- May be denied for security reasons
- Blocks immediate deployment needs
- Client secret acceptable security trade-off

## When to Revisit

Consider switching to OIDC if:

- Organization CA policies relaxed for GitHub Actions
- Security team mandates OIDC only
- Service principal secret compromised
- Azure improves OIDC CA policy integration

## Related Decisions

- ADR-040: Reusable GitHub Actions Workflows
- ADR-041: Semantic Commit Messages (triggers deployments)
- ADR-042: Dev Container for Development

## References

- `.github/workflows/deploy.yml` - Deployment workflow
- `.github/workflows/aspire-deployment.yml` - Aspire deployment
- Commit: `80b74b6` - "Use client-secret auth - OIDC now blocked by Conditional Access policy"
- Commit: `79fb0e6` - "Switch to client-secret auth to bypass Conditional Access policy"
- Commit: `f1a6616` - "Remove azure/login, use only azd auth with client-secret"
- docs/deployment/AUTHENTICATION_SETUP.md
