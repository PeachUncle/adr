# ADR-022: Runtime FQDN Detection for Connection Strings

**Status:** ✅ Accepted  
**Date:** October 20, 2025  
**Context:** Azure Container Apps Internal Networking

## Context

Azure Container Apps use internal FQDNs for service-to-service communication:

- `postgres.internal.kindsea-395ab1c0.eastus.azurecontainerapps.io`
- `cache.internal.kindsea-395ab1c0.eastus.azurecontainerapps.io`

Initial approach tried using azd template variables to inject the environment domain:

```yaml
env:
  - name: AZURE_CONTAINER_APPS_ENVIRONMENT_DEFAULT_DOMAIN
    value: {{ .Env.AZURE_CONTAINER_APPS_ENVIRONMENT_DEFAULT_DOMAIN }}
```

**Problems encountered:**

1. Invalid template syntax (spaces in `{ { .Env.VAR } }`)
2. azd not populating the variable reliably
3. Timing issues (template processed before Bicep outputs available)
4. Connection strings using short hostnames (`postgres`, `cache`) instead of FQDNs

**Result**: Health checks failing with 503 Unhealthy due to DNS resolution failures.

## Decision

Detect Azure Container Apps domain **at runtime** using built-in environment variables instead of template injection.

## Rationale

1. **Azure Provides It**: `CONTAINER_APP_HOSTNAME` is automatically injected
2. **Reliable**: Based on actual running environment, not deployment config
3. **No Template Dependency**: Works regardless of azd issues
4. **Backwards Compatible**: Checks for template variable first, then fallback
5. **Simple**: Extract domain from hostname that's always present

## Consequences

### Positive

- **Works reliably**: No azd template processing issues
- **Zero configuration**: Azure provides the values automatically
- **Self-documenting**: Logs show detected domain
- **Testable**: Can override via environment variable in tests
- **Portable**: Same logic works in any Azure Container Apps environment

### Negative

- **Azure-specific**: Code has Azure Container Apps knowledge
- **Runtime overhead**: Small cost to parse hostname on startup
- **Fallback complexity**: Multiple detection methods (template var, hostname, hardcoded)

### Risks Mitigated

- Extensive logging shows detection process
- Multiple fallback strategies (template var → hostname → local)
- Health checks verify connection string patching worked
- Integration tests validate FQDN patching logic

## Implementation

**Detection Logic** (src/AcademicAssessment.Web/Program.cs):

```csharp
// Step 1: Check for template-injected variable (preferred)
var azureContainerAppsDomain = builder.Configuration["AZURE_CONTAINER_APPS_ENVIRONMENT_DEFAULT_DOMAIN"];

// Step 2: If not found, detect from CONTAINER_APP_HOSTNAME
if (string.IsNullOrEmpty(azureContainerAppsDomain))
{
    var containerAppHostname = Environment.GetEnvironmentVariable("CONTAINER_APP_HOSTNAME");
    
    if (!string.IsNullOrEmpty(containerAppHostname) && 
        containerAppHostname.Contains(".azurecontainerapps.io"))
    {
        // Example: webapi.kindsea-395ab1c0.eastus.azurecontainerapps.io
        // Extract: kindsea-395ab1c0.eastus.azurecontainerapps.io
        var parts = containerAppHostname.Split('.');
        if (parts.Length >= 4)
        {
            azureContainerAppsDomain = string.Join(".", parts.Skip(1));
            Log.Information("Detected Azure Container Apps domain from hostname: {Domain}", 
                azureContainerAppsDomain);
        }
    }
}

Log.Information("Azure Container Apps Domain: {Domain}", 
    azureContainerAppsDomain ?? "(not set - using local development)");
```

**Connection String Patching**:

```csharp
// PostgreSQL FQDN patching
if (!string.IsNullOrEmpty(azureContainerAppsDomain))
{
    var postgresConnectionString = builder.Configuration.GetConnectionString("edumind");
    
    if (!string.IsNullOrEmpty(postgresConnectionString) && 
        postgresConnectionString.Contains("Host=postgres;"))
    {
        // Patch: postgres → postgres.internal.{domain}
        postgresConnectionString = postgresConnectionString.Replace(
            "Host=postgres;",
            $"Host=postgres.internal.{azureContainerAppsDomain};"
        );
        
        builder.Configuration["ConnectionStrings:edumind"] = postgresConnectionString;
        
        Log.Information("✅ Patched PostgreSQL hostname to use Azure Container Apps internal FQDN: {Host}",
            $"postgres.internal.{azureContainerAppsDomain}");
    }
}

// Redis FQDN patching (similar logic)
```

## Expected Logs (Success)

```
[INFO] Azure Container Apps Domain: (not set)
[INFO] Detected Azure Container Apps domain from hostname: kindsea-395ab1c0.eastus.azurecontainerapps.io
[INFO] Azure Container Apps Domain: kindsea-395ab1c0.eastus.azurecontainerapps.io
[INFO] Checking PostgreSQL connection string for hostname patching...
[INFO] ✅ Patched PostgreSQL hostname to use Azure Container Apps internal FQDN: postgres.internal.kindsea-395ab1c0.eastus.azurecontainerapps.io
[INFO] Checking Redis connection string for hostname patching...
[INFO] ✅ Patched Redis hostname to use Azure Container Apps internal FQDN: cache.internal.kindsea-395ab1c0.eastus.azurecontainerapps.io
[INFO] PostgreSQL Host: postgres.internal.kindsea-395ab1c0.eastus.azurecontainerapps.io
[INFO] Redis Host: cache.internal.kindsea-395ab1c0.eastus.azurecontainerapps.io
```

## Why Template Variables Failed

**Attempt 1**: Invalid syntax

```yaml
# ❌ Spaces break Go template parsing
value: { { .Env.AZURE_CONTAINER_APPS_ENVIRONMENT_DEFAULT_DOMAIN } }
```

**Attempt 2**: Variable not populated

```yaml
# ❌ azd doesn't inject the value (timing issue)
value: {{ .Env.AZURE_CONTAINER_APPS_ENVIRONMENT_DEFAULT_DOMAIN }}
```

**Attempt 3**: Quoted syntax

```yaml
# ❌ May work but uncertain due to azd quirks
value: "{{ .Env.AZURE_CONTAINER_APPS_ENVIRONMENT_DEFAULT_DOMAIN }}"
```

**Solution**: Use runtime detection (works 100% of the time)

## Environment Variables Azure Provides

Azure Container Apps automatically injects:

- `CONTAINER_APP_NAME` - App name (e.g., "webapi")
- `CONTAINER_APP_HOSTNAME` - Full FQDN (e.g., "webapi.kindsea-395ab1c0.eastus.azurecontainerapps.io")
- `CONTAINER_APP_REVISION` - Revision name
- `CONTAINER_APP_REPLICA_NAME` - Replica identifier

We use `CONTAINER_APP_HOSTNAME` to extract the environment domain.

## Local Development Behavior

In local development (Aspire):

- `CONTAINER_APP_HOSTNAME` is not set
- Detection logs: "Azure Container Apps Domain: (not set - using local development)"
- Connection strings use short names: `Host=postgres;` (works via Aspire service discovery)
- No patching occurs (not needed locally)

## Alternative Considered: Hardcode Domain

**Rejected because:**

- Different domains per environment (dev, staging, prod)
- Would break multi-environment deployments
- Manual updates required for each deployment
- Prone to configuration errors

## Related Decisions

- ADR-020: Azure Container Apps for Hosting
- ADR-021: Azure Database for PostgreSQL (FQDN needed)
- ADR-006: Redis for Caching Layer (FQDN needed)
- ADR-007: .NET Aspire for Local Orchestration (service discovery)

## References

- `src/AcademicAssessment.Web/Program.cs` - FQDN detection and patching logic
- `src/infra/webapi.tmpl.yaml` - Template variable attempts
- Commit: `e030b25` - "Workaround: Detect Azure Container Apps domain from CONTAINER_APP_HOSTNAME"
- Commit: `a09f85b` - "Fix: Add AZURE_CONTAINER_APPS_ENVIRONMENT_DEFAULT_DOMAIN env var"
- docs/deployment/RUNTIME_DOMAIN_DETECTION.md
- docs/deployment/FQDN_PATCHING_FIX.md
