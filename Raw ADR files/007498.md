# ADR-008 – Deployment Strategy: Docker Containers via GHCR & CI/CD Pipeline

**Status:** Accepted  
**Date:** 2025-11-13  
**Author:** Niklas Häll  
**Updated:** 2025-12-01 (Added CI/CD Pipeline Strategy section)

---

## Context

The project initially attempted to deploy the Blazor Server application to Azure App Service using **zip-deploy** with Oryx build system. The deployment process involved:
- Building the application in CI workflow
- Publishing as a framework-dependent .NET 8 application
- Deploying via zip to App Service
- Relying on Oryx auto-detection to identify and run the .NET application

**Critical Problem Encountered:**  
Despite explicit configuration in Bicep (`linuxFxVersion: 'DOTNET|8.0'`, `appCommandLine: 'dotnet Ticketing.Web.dll'`), Oryx consistently auto-detected PHP as the runtime, even when:
- `wwwroot` contained .NET DLL files
- App settings explicitly set `WEBSITE_STACK='DOTNET'`
- `SCM_DO_BUILD_DURING_DEPLOYMENT='false'` was configured
- `oryx-manifest.toml` was manually created

Oryx's auto-detection runs when the container starts, and if `wwwroot` is empty or doesn't match Oryx's expectations, it defaults to PHP. This behavior persisted across multiple attempts, including:
- Recreating the App Service
- Stopping/starting the service
- Clearing `wwwroot` and redeploying
- Adding explicit manifest files

The root cause appears to be Oryx's detection logic running before files are fully deployed, or cached container image choices that override explicit configuration.

---

## Decision

We switch to **Docker container deployment via GitHub Container Registry (GHCR)** for the Blazor Server application. This approach:
- **Bypasses Oryx entirely** – Docker containers have the runtime pre-installed
- **Provides full control** over the runtime environment
- **Ensures reproducibility** – same image = same behavior
- **Eliminates auto-detection issues** – no ambiguity about runtime stack

The deployment process now:
1. Builds a Docker image in CI workflow (multi-stage build with .NET 8 SDK and runtime)
2. Pushes image to GHCR with tags: `web:latest` and `web:<git-sha>`
3. Updates App Service to use the Docker container image
4. App Service pulls and runs the container directly

**Key Implementation Details:**
- Dockerfile uses multi-stage build (SDK for build, ASP.NET runtime for final image)
- CI workflow builds and pushes to GHCR using GitHub Actions
- CD workflow updates App Service `linuxFxVersion` to point to the container image
- No authentication needed for public GHCR images (repo is public)
- Container includes only compiled application code (no secrets or sensitive data)

---

## Consequences

**Advantages:**  
- **Reliable runtime detection** – Docker container explicitly defines .NET 8 runtime
- **No Oryx interference** – complete bypass of auto-detection logic
- **Reproducible deployments** – same image behaves identically across environments
- **Faster troubleshooting** – container logs show actual .NET startup, not Oryx detection
- **Production-ready approach** – containers are industry standard for cloud deployments
- **No additional costs** – GHCR is free for public images
- **Simpler configuration** – no need for complex Oryx manifest files or app settings

**Disadvantages:**  
- **Longer CI time** – Docker build adds ~2-3 minutes to CI workflow (acceptable trade-off)
- **Requires Docker knowledge** – team needs basic Docker understanding (minimal requirement)
- **Image size** – Docker images are larger than zip deployments (acceptable for reliability)
- **If private images:** Would require GitHub Personal Access Token (not needed for public repo)

---

## Risks / Mitigations

- **Risk:** Docker build failures could block deployments.  
  **Mitigation:** Dockerfile is simple and follows Microsoft's official .NET 8 patterns. Build errors are clear and easy to debug.

- **Risk:** GHCR rate limits for public images.  
  **Mitigation:** GitHub provides generous limits for public images. For this project's scale, limits are not a concern.

- **Risk:** Container image contains sensitive data.  
  **Mitigation:** Dockerfile only copies compiled code. No secrets, connection strings, or appsettings files are included. `.gitignore` ensures sensitive files are excluded.

- **Risk:** Team unfamiliarity with Docker.  
  **Mitigation:** Dockerfile is minimal and well-documented. Standard .NET 8 patterns are used, making it easy to understand and maintain.

---

## Alternatives

- **Continue with Oryx/zip-deploy:** Attempted extensively but failed due to persistent PHP detection. Multiple workarounds (manifest files, app settings, container restarts) were unsuccessful. Rejected due to unreliability.

- **Azure Container Apps:** Alternative Azure service designed for containers. Rejected because App Service is already provisioned and meets requirements. Migration would add unnecessary complexity.

- **Azure Container Instances (ACI):** Lower-level container service. Rejected – App Service provides better integration with existing infrastructure (custom domains, SSL, scaling).

- **Self-hosted container registry:** Using Azure Container Registry (ACR) instead of GHCR. Rejected – GHCR is free, integrated with GitHub, and sufficient for project needs. ACR would add cost and complexity.

- **Keep trying Oryx fixes:** Multiple attempts over several days with various configurations. Rejected – time investment exceeded value. Docker solution works immediately and is more reliable long-term.

---

## Technical Implementation Guide

### Architecture Overview

```
CI Workflow:
  └─ Build Docker image (multi-stage)
  └─ Push to GHCR (ghcr.io/owner/repo/web:latest + :sha)

CD Workflow:
  └─ Get container image tag from CI
  └─ Update App Service linuxFxVersion
  └─ Restart App Service
```

### Dockerfile Structure

Located at: `src/web/Ticketing.Web/Dockerfile`

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["src/web/Ticketing.Web/Ticketing.Web.csproj", "src/web/Ticketing.Web/"]
COPY ["src/shared/Ticketing.Contracts/Ticketing.Contracts.csproj", "src/shared/Ticketing.Contracts/"]
RUN dotnet restore "src/web/Ticketing.Web/Ticketing.Web.csproj"
COPY . .
WORKDIR "/src/src/web/Ticketing.Web"
RUN dotnet build "Ticketing.Web.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "Ticketing.Web.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Ticketing.Web.dll"]
```

**Key Points:**
- Multi-stage build minimizes final image size
- Uses official Microsoft .NET 8 images
- Only compiled application code in final image
- No secrets or configuration files included

### CI Workflow Changes

**Removed:**
- `.NET build/publish` steps (Docker handles this)
- Artifact upload/download (not needed)
- Oryx manifest file creation
- Version file creation

**Added:**
- Docker login to GHCR
- Docker build and push with version tags

**Workflow Time:** ~43 seconds (acceptable for reliability)

### CD Workflow Changes

**Removed:**
- Artifact download
- Zip deployment
- Oryx configuration steps
- App settings for Oryx

**Added:**
- Container image tag extraction from CI workflow
- App Service `linuxFxVersion` update to Docker image
- App Service restart

**Workflow Time:** ~44 seconds (fast and reliable)

### Bicep Configuration

**App Service Configuration:**
```bicep
siteConfig: {
  linuxFxVersion: 'DOCKER|ghcr.io/mymh13/clo24-nikhal78-examwork/web:latest'
  appSettings: [
    {
      name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
      value: 'false'
    }
    {
      name: 'DOCKER_REGISTRY_SERVER_URL'
      value: 'https://ghcr.io'
    }
    {
      name: 'DOCKER_REGISTRY_SERVER_USERNAME'
      value: 'mymh13'
    }
    {
      name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
      value: ''  // Not needed for public images
    }
  ]
}
```

**Note:** For public GHCR images, no password is required. If images were private, a GitHub Personal Access Token would be needed.

### Verification

After deployment, verify the container is running correctly:

1. **Check App Service logs:**
   ```bash
   az webapp log tail --name examwork-web-dev --resource-group rg-examwork-dev
   ```
   Should show .NET startup messages, not PHP.

2. **Verify container image:**
   ```bash
   az webapp config show --name examwork-web-dev --resource-group rg-examwork-dev --query linuxFxVersion
   ```
   Should show: `DOCKER|ghcr.io/...`

3. **Check application:**
   Visit `https://ticket.mymh.dev` and verify the Blazor application loads correctly.

### Troubleshooting

**Issue: Container fails to start**
- Check Dockerfile syntax
- Verify .NET 8 runtime is correct
- Check App Service logs for container errors

**Issue: Image not found**
- Verify image exists in GHCR: https://github.com/owner/repo/packages
- Check image tag matches what's configured in App Service
- Ensure image is public (or token is configured if private)

**Issue: Slow deployments**
- Docker build time is ~2-3 minutes (acceptable trade-off)
- Consider Docker layer caching if needed (removed for simplicity)

---

## Lessons Learned

**Oryx Auto-Detection Issues:**
- Oryx's auto-detection can override explicit configuration
- Empty `wwwroot` at container startup triggers default PHP selection
- Container image choice may be cached, preventing runtime changes
- Multiple configuration attempts (app settings, manifests, restarts) were unsuccessful

**Docker Solution Benefits:**
- Immediate resolution of runtime detection issues
- Clear, predictable behavior
- Industry-standard approach for cloud deployments
- Better alignment with modern DevOps practices

**Key Takeaway:**  
When platform auto-detection fails despite explicit configuration, switching to explicit container definitions provides reliability and control that outweighs the slight increase in build complexity.

---

## CI/CD Pipeline Strategy

### Why GitHub Actions

The project uses **GitHub Actions** as the CI/CD platform for the following reasons:

**Advantages:**
- **Native GitHub Integration** - Built into GitHub, no external service setup required
- **Free for Public Repositories** - No cost for public repos with generous free tier
- **YAML-Based Configuration** - Version-controlled workflows alongside code
- **Rich Marketplace** - Extensive ecosystem of pre-built actions (Docker, Azure, .NET)
- **OIDC Authentication** - Secure Azure authentication without storing credentials
- **Workflow Triggers** - Flexible triggers (push, PR, manual, workflow_run)
- **Environment Protection** - Environment-level secrets and approval gates

**Alternatives Considered:**
- **Azure DevOps Pipelines** - Rejected: Requires separate Azure DevOps organization, adds complexity
- **Jenkins** - Rejected: Requires self-hosting infrastructure, maintenance overhead
- **GitLab CI/CD** - Rejected: Project uses GitHub, migration unnecessary
- **Azure Pipelines (GitHub Integration)** - Rejected: GitHub Actions provides sufficient functionality without external dependency

### Pipeline Architecture

The CI/CD pipeline follows a **separated CI/CD pattern** with distinct workflows:

```
┌─────────────────────────────────────────────────────────────┐
│ CI Workflow (ci-build.yaml)                                 │
│ - Triggered on: push to main, PR, manual                    │
│ - Builds: Docker image for Web App                          │
│ - Outputs: Container image to GHCR (web:latest + :sha)      │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ (workflow_run trigger)
                          ▼
        ┌─────────────────────────────────────┐
        │ CD Workflows (triggered by CI)     │
        ├─────────────────────────────────────┤
        │ cd-web-dev.yaml                    │
        │ - Deploys Web App to Azure         │
        │ - Updates App Service settings     │
        │                                     │
        │ cd-functions-dev.yaml              │
        │ - Deploys Function App to Azure    │
        │ - Uses zip deploy (not Docker)     │
        └─────────────────────────────────────┘
```

**Key Design Decisions:**
1. **Separated CI and CD** - CI builds artifacts, CD deploys them (allows independent execution)
2. **Workflow Run Triggers** - CD workflows trigger on successful CI completion
3. **Environment-Based Deployment** - Uses GitHub Environments (`dev`) for environment-specific configuration
4. **Idempotent Deployments** - Deployments can be run multiple times safely
5. **Conditional Deployment** - CD workflows check if target resources exist before deploying

### Workflow Structure

**CI Workflow (`ci-build.yaml`):**
- **Triggers:** Push to `main`, Pull Requests, Manual dispatch
- **Path Filters:** Only runs on changes to `src/**`, `.github/workflows/**`, solution files, Dockerfiles
- **Concurrency:** Cancels in-progress runs for same branch
- **Steps:**
  1. Checkout code
  2. Extract Git SHA for versioning
  3. Login to GHCR
  4. Build and push Docker image with tags: `web:latest` and `web:<sha>`

**CD Workflows (`cd-web-dev.yaml`, `cd-functions-dev.yaml`):**
- **Triggers:** `workflow_run` - triggered when CI workflow completes successfully
- **Environment:** `dev` (GitHub Environment with protected secrets)
- **Authentication:** Azure OIDC (no stored credentials)
- **Steps:**
  1. Azure CLI login via OIDC
  2. Verify target resource exists (skip if not found)
  3. Deploy application (Docker for Web, zip for Functions)
  4. Update App Settings (Application Insights, subscription ID, etc.)
  5. Restart service

### Environment Management

**GitHub Environments:**
- **`dev`** - Development environment
  - Protected secrets: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`
  - Variables: `WEBAPP_NAME`, `WEBAPP_RG`, `FUNCTIONAPP_NAME`, `FUNCTIONAPP_RG`
  - Repository secrets: `APPLICATIONINSIGHTS_CONNECTION_STRING`

**Secret Management:**
- **Azure Credentials:** Stored as GitHub Environment secrets (OIDC client ID, tenant, subscription)
- **Application Secrets:** Stored as GitHub Repository secrets (Application Insights connection string)
- **No Secrets in Code:** All sensitive values injected at deployment time via Azure CLI

**Deployment Strategy:**
- **Automatic on Push:** CI runs on every push to `main`, CD runs after successful CI
- **Manual Trigger:** CI can be triggered manually via `workflow_dispatch`
- **Pull Request Validation:** CI runs on PRs to validate builds (no deployment)
- **Environment Isolation:** Single `dev` environment (production would be separate environment)

### Deployment Methods

**Web App (Docker):**
- Container image built in CI
- Pushed to GHCR with version tags
- CD workflow updates App Service `linuxFxVersion` to point to new image
- App Service pulls and runs container

**Function App (Zip Deploy):**
- .NET publish in CD workflow
- Zipped and deployed via `az functionapp deployment source config-zip`
- Faster than Docker for Functions (no container overhead needed)

### Security Considerations

- **OIDC Authentication:** No stored Azure credentials, uses federated identity
- **Least Privilege:** GitHub Actions service principal has minimal required permissions
- **Secret Rotation:** Secrets can be rotated in GitHub without code changes
- **Audit Trail:** All deployments logged in GitHub Actions and Azure Activity Log
- **No Secrets in Images:** Docker images contain no secrets or connection strings

## References

- [ADR-003 - Infrastructure as Code](./ADR-003-iac.md) - Bicep IaC tool choice
- [Microsoft Docs – Deploy ASP.NET Core to Azure App Service](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/azure-apps/)
- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure OIDC Authentication](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure)

