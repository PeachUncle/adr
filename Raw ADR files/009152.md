# ADR-002: Backend Architecture - Functions vs App Service

## Status
Accepted

## Context
We need to choose a backend architecture for the ESRI App Finder & Builder Assistant. The backend must:
- Handle AI chat requests to Azure OpenAI (GPT-4)
- Integrate with ArcGIS REST API for web map operations
- Search and retrieve Living Atlas datasets
- Configure and generate app URLs
- Handle 100+ concurrent users initially
- Scale elastically with demand
- Be cost-effective for v1 with no persistence layer
- Support rapid development and deployment

The backend is stateless (no database in v1), making it a good candidate for serverless architecture.

## Decision
We will use **Azure Functions (Node.js) with HTTP triggers** as the primary backend architecture, with **Azure Static Web Apps** providing the unified deployment model.

### Architecture
```
Frontend (React SPA) → Azure Static Web Apps → Azure Functions (API)
                                                    ↓
                                    ┌───────────────────────────┐
                                    │  External Services        │
                                    │  - Azure OpenAI           │
                                    │  - ArcGIS REST API        │
                                    │  - Living Atlas API       │
                                    └───────────────────────────┘
```

### Technology Stack
- **Azure Functions v4**: Serverless compute
- **Node.js 20 LTS**: Runtime
- **TypeScript**: Type safety
- **Express.js-like routing**: Using Azure Functions HTTP triggers
- **In-memory caching**: For temporary session data
- **Azure Static Web Apps**: Integrated deployment of frontend + functions

## Consequences

### Positive
1. **Cost Efficiency**: Pay-per-execution model means lower costs for v1 with moderate traffic
2. **Auto-scaling**: Automatically scales from 0 to hundreds of instances based on demand
3. **Zero Server Management**: No servers to maintain, patch, or monitor
4. **Integrated Deployment**: Azure Static Web Apps deploys frontend + backend together via GitHub Actions
5. **Fast Cold Starts**: Node.js cold starts are <1 second typically
6. **Built-in Monitoring**: Azure Monitor and Application Insights included
7. **Stateless Design**: Perfect for our v1 requirements (no database)
8. **Geographic Distribution**: Can deploy to multiple regions easily
9. **Rapid Development**: Quick iterations without infrastructure concerns
10. **Future Flexibility**: Easy to migrate to App Service or containers if needs change

### Negative
1. **Cold Start Latency**: Infrequent endpoints may have 1-2 second cold start delay
2. **Execution Time Limit**: 5-minute timeout on consumption plan (acceptable for our use case)
3. **Connection Limits**: Limited concurrent connections, but sufficient for our scale
4. **Debugging Complexity**: Serverless debugging is harder than traditional apps
5. **Vendor Lock-in**: Tightly coupled to Azure Functions runtime

## Alternatives Considered

### 1. **Azure App Service (Node.js)**
- **Pros**: 
  - Always-on (no cold starts)
  - More flexible for long-running operations
  - Traditional app model (easier debugging)
  - WebSocket support for real-time features (future)
- **Cons**: 
  - Higher base cost (always running)
  - Manual scaling configuration required
  - Over-provisioned for v1 traffic
  - More complex deployment
- **Why Rejected**: Over-engineered and more expensive for v1. Static Web Apps + Functions is simpler and cheaper.

### 2. **Azure Container Apps**
- **Pros**: 
  - Full container control
  - Scale to zero like Functions
  - Support any runtime/language
  - Good for microservices
- **Cons**: 
  - More complex deployment
  - Requires Docker knowledge
  - Overkill for simple REST API
  - Slower cold starts than Functions
- **Why Rejected**: Unnecessary complexity for our straightforward API needs.

### 3. **Azure Static Web Apps with Managed Functions (Chosen)**
- **Pros**: 
  - Integrated deployment (frontend + backend)
  - Automatic HTTPS and custom domains
  - Built-in CI/CD via GitHub Actions
  - Global CDN for frontend
  - Functions integrated seamlessly
  - Cost-effective
- **Cons**: 
  - Functions limited to HTTP triggers in SWA integration
  - Less flexibility than standalone Functions or App Service
- **Why Accepted**: Best balance of simplicity, cost, and features for v1.

### 4. **Express.js on Azure App Service**
- **Pros**: 
  - Familiar Express patterns
  - Full control over middleware
  - Easy local development
- **Cons**: 
  - Always-on costs
  - Manual scaling setup
  - More deployment complexity
- **Why Rejected**: Functions provide Express-like routing without always-on costs.

### 5. **Serverless Framework or Terraform**
- **Pros**: 
  - Infrastructure as code
  - Multi-cloud portability
- **Cons**: 
  - Additional tooling complexity
  - Learning curve
  - Not necessary for Azure-only deployment
- **Why Rejected**: Azure Static Web Apps + GitHub Actions is simpler and native to Azure.

## Implementation Details

### Function Structure
```
backend/
├── api/
│   ├── chat/
│   │   └── index.ts           # POST /api/chat
│   ├── recommend/
│   │   └── index.ts           # GET /api/recommend
│   ├── maps/
│   │   ├── create.ts          # POST /api/maps
│   │   └── get.ts             # GET /api/maps/:id
│   ├── living-atlas/
│   │   └── search.ts          # GET /api/living-atlas/search
│   └── health/
│       └── index.ts           # GET /api/health
├── shared/
│   ├── services/              # Shared service logic
│   ├── types/                 # TypeScript types
│   └── utils/                 # Utility functions
├── host.json                  # Functions runtime config
├── local.settings.json        # Local environment variables
└── package.json
```

### Function Configuration (`host.json`)
```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  },
  "functionTimeout": "00:05:00"
}
```

### Sample Function (HTTP Trigger)
```typescript
import { AzureFunction, Context, HttpRequest } from '@azure/functions';
import { chatService } from '../shared/services/chat.service';

const httpTrigger: AzureFunction = async (
  context: Context,
  req: HttpRequest
): Promise<void> => {
  try {
    const { message, sessionId, context: chatContext } = req.body;
    
    const response = await chatService.sendMessage({
      message,
      sessionId,
      context: chatContext
    });
    
    context.res = {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
      body: response
    };
  } catch (error) {
    context.log.error('Chat error:', error);
    context.res = {
      status: 500,
      body: { error: 'Internal server error' }
    };
  }
};

export default httpTrigger;
```

### Static Web Apps Configuration (`staticwebapp.config.json`)
```json
{
  "routes": [
    {
      "route": "/api/*",
      "allowedRoles": ["anonymous"]
    }
  ],
  "navigationFallback": {
    "rewrite": "/index.html"
  },
  "responseOverrides": {
    "404": {
      "rewrite": "/index.html"
    }
  }
}
```

### Deployment via GitHub Actions
```yaml
name: Azure Static Web Apps CI/CD

on:
  push:
    branches: [main]

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
          app_location: "/frontend"
          api_location: "/backend"
          output_location: "dist"
```

## Scaling Strategy

### Initial Setup (v1)
- **Plan**: Consumption (pay-per-execution)
- **Expected Load**: 100 concurrent users, ~1000 requests/hour
- **Cold Start Mitigation**: Keep-alive ping for critical functions (optional)

### Future Scaling (v2+)
- **Plan**: Premium Plan if cold starts become issue
- **Options**: 
  - Pre-warmed instances
  - VNet integration for private services
  - Durable Functions for workflows

## Monitoring

### Key Metrics
- Function execution time
- Cold start frequency
- Error rates
- Azure OpenAI API latency
- ESRI API latency

### Tools
- Azure Application Insights
- Azure Monitor
- Custom logging with Winston/Pino

## Cost Estimate (v1)

### Consumption Plan Pricing
- **First 1M executions/month**: Free
- **Memory**: 1.5 GB-s per execution
- **Execution time**: ~2 seconds average
- **Monthly estimate**: $10-20 for 100K requests/month

### Static Web Apps Pricing
- **Free tier**: 100 GB bandwidth, sufficient for v1
- **Custom domain**: Included
- **SSL**: Included

**Total estimated monthly cost**: $10-30 for moderate traffic

## Migration Path

If we outgrow Azure Functions, migration path:
1. **Azure App Service**: Lift-and-shift Functions code to Express app
2. **Azure Container Apps**: Containerize for more control
3. **AKS**: For true microservices at scale

Code structure is designed to support easy migration (service layer abstraction).

## References
- [Azure Functions Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Azure Static Web Apps](https://docs.microsoft.com/en-us/azure/static-web-apps/)
- [Functions Performance Best Practices](https://docs.microsoft.com/en-us/azure/azure-functions/functions-best-practices)

## Related ADRs
- [ADR-007: Azure Deployment Strategy](./007-deployment-strategy.md)

---
**Date**: 2025-11-05  
**Author**: Development Team  
**Status**: Accepted
