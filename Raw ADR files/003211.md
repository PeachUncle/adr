# ADR-020: Choice of Azure Static Web Apps for Frontend Hosting

**Date:** 2025-10-09

**Status:** Accepted

## Context

The PlumbingPOC application requires a hosting solution for its React/Vite frontend that provides global CDN distribution, automatic SSL certificates, custom domain support, and seamless CI/CD integration. The current Netlify hosting provides these features but at a higher cost for low-traffic applications.

## Decision

We will use **Azure Static Web Apps** as the primary hosting solution for the PlumbingPOC frontend. This service provides:

1. **Global CDN**: Automatic content distribution worldwide
2. **SSL Certificates**: Free managed certificates for custom domains
3. **Git Integration**: Direct GitHub repository integration with automatic deployments
4. **API Integration**: Built-in support for Azure Functions as backend APIs
5. **Authentication**: Optional integration with Azure AD B2C
6. **Free Tier**: Generous free tier suitable for low-traffic applications

## Implementation Details

### Service Configuration

**Azure Static Web Apps Setup:**
```json
{
  "name": "plumbingpoc-app",
  "location": "East US",
  "resourceGroup": "plumbingpoc-azure-prod",
  "sku": {
    "name": "Free",
    "tier": "Free"
  },
  "buildConfig": {
    "appBuildCommand": "npm install --include=dev && npx vitest run && npm --workspace=@plumbingpoc/frontend run build",
    "outputLocation": "packages/frontend/dist",
    "appLocation": "/"
  }
}
```

### CI/CD Integration

**GitHub Actions Workflow:**
```yaml
name: Azure Static Web Apps CI/CD

on:
  push:
    branches:
      - main
      - azure-poc
  pull_request:
    types: [opened, synchronize, reopened, closed]
    branches:
      - main
      - azure-poc

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build And Deploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "/"
          api_location: "packages/backend/netlify/functions"
          output_location: "packages/frontend/dist"
```

### Custom Domain Configuration

**DNS Setup:**
```bash
# Azure DNS Zone
az network dns zone create \
  --resource-group plumbingpoc-azure-prod \
  --name plumbingpoc.com

# CNAME record for custom domain
az network dns record-set cname create \
  --resource-group plumbingpoc-azure-prod \
  --zone-name plumbingpoc.com \
  --name www \
  --ttl 3600 \
  --cname-target plumbingpoc-app.azurestaticapps.net
```

## Consequences

### Positive

*   **Cost Effective**: Free tier covers low-traffic applications completely
*   **Global Performance**: Built-in CDN ensures fast content delivery worldwide
*   **Developer Experience**: Seamless GitHub integration with preview deployments
*   **Security**: Automatic SSL certificate management and renewal
*   **Scalability**: Automatic scaling based on traffic without configuration
*   **API Integration**: Native support for Azure Functions as backend

### Negative

*   **Vendor Lock-in**: Tightly integrated with Azure ecosystem
*   **Limited Customization**: Less control over CDN configuration compared to Azure Front Door
*   **Preview Limitations**: Staging environment limitations for complex applications
*   **Cold Start**: Initial load may be slower for infrequently accessed applications

### Mitigation Strategies

**Performance Optimization:**
- Implement proper caching headers in application
- Use Azure CDN as additional layer if needed
- Optimize bundle size and loading strategies

**Development Workflow:**
- Use staging environments for testing
- Implement proper branch protection rules
- Set up automated testing in CI/CD pipeline

## Alternatives Considered

### Azure App Service

**Pros:**
- More control over runtime environment
- Support for multiple frameworks and runtimes
- Advanced scaling and deployment options

**Cons:**
- Higher cost for low-traffic applications
- More complex configuration and management
- No built-in CDN functionality

**Decision:** Rejected due to cost and complexity for this use case

### Azure Front Door + Storage

**Pros:**
- Maximum control over CDN and routing
- Advanced security features
- Global distribution with custom rules

**Cons:**
- Significantly more complex setup
- Higher cost for small applications
- Requires multiple Azure services coordination

**Decision:** Rejected due to overkill for current scale and traffic

### Vercel

**Pros:**
- Similar feature set to Netlify
- Excellent developer experience
- Good performance and reliability

**Cons:**
- Not Azure native (vendor diversification goal)
- Similar pricing structure to Netlify

**Decision:** Rejected to maintain Azure ecosystem consistency

## Related Decisions

- ADR-004: Choice of Frontend Framework (React/TypeScript/Vite)
- ADR-005: Choice of Hosting and Deployment Platform (Netlify → Azure)
- ADR-019: Choice of Single Repository Strategy for Azure POC

## Success Metrics

### Technical Metrics
- [ ] Application deploys successfully via GitHub Actions
- [ ] Custom domain configured with SSL certificate
- [ ] Global CDN performance meets or exceeds Netlify
- [ ] API integration with Azure Functions works correctly

### Performance Metrics
- [ ] First Contentful Paint < 2 seconds
- [ ] Time to Interactive < 3 seconds
- [ ] Lighthouse performance score > 90
- [ ] Global load times consistent across regions

### Cost Metrics
- [ ] Monthly hosting cost remains under $5
- [ ] No unexpected charges from scaling
- [ ] Bandwidth costs within free tier limits

## Future Considerations

**Scaling Up:**
- If traffic exceeds free tier limits, consider Azure Front Door
- For advanced security, implement Azure Application Gateway
- Consider Azure CDN for additional performance optimization

**Advanced Features:**
- Implement Azure Front Door for advanced routing rules
- Add Azure Web Application Firewall for enhanced security
- Consider Azure API Management for API gateway functionality

---

**Note:** Azure Static Web Apps is ideal for modern SPAs with low to medium traffic. For high-traffic enterprise applications, consider Azure Front Door + Azure App Service combination.
