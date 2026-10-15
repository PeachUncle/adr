# ADR-019: Choice of Single Repository Strategy for Azure POC

**Date:** 2025-10-09

**Status:** Accepted

## Context

The PlumbingPOC project requires an Azure migration proof-of-concept (POC) to validate the technical feasibility and cost benefits of moving from the current Netlify/Supabase architecture to Azure cloud services. The codebase consists of approximately 80-90% shared code (React components, business logic, API controllers, tests) with only 10-20% being platform-specific (database connections, authentication, real-time services).

Initial planning considered a separate repository approach for the Azure POC, but this would create synchronization challenges for the large shared codebase. The single repository strategy offers better code management while maintaining clear separation between environments.

## Decision

We will use a **single repository with environment-specific configurations** for the Azure POC. This approach includes:

1. **Single Git Repository**: Maintain all code in the existing `PlumbingPOC` repository
2. **Branch-Based Development**: Use `azure-poc` branch for Azure-specific development
3. **Environment-Specific Configurations**: Separate config files for Netlify vs Azure deployments
4. **Build Script Separation**: Different build and deployment scripts for each platform
5. **Shared Code Synchronization**: Automatic sync of 80-90% shared codebase

## Implementation Details

### Repository Structure

```
PlumbingPOC/ (single repository)
├── packages/
│   ├── frontend/
│   │   ├── src/           # Shared React components (80-90%)
│   │   ├── config/        # Environment-specific configs
│   │   │   ├── netlify/   # Netlify build configs
│   │   │   └── azure/     # Azure build configs
│   │   └── build-scripts/ # Platform-specific build scripts
│   └── backend/
│       ├── api/           # Shared API logic (80-90%)
│       ├── config/        # Environment-specific configs
│       │   ├── supabase/  # Supabase database/auth configs
│       │   └── azure/     # Azure database/auth configs
│       └── deploy/        # Platform deployment scripts
├── environments/
│   ├── netlify.env         # Netlify environment variables
│   └── azure.env           # Azure environment variables
├── .github/workflows/
│   ├── netlify-deploy.yml  # Netlify CI/CD
│   └── azure-deploy.yml    # Azure CI/CD
└── scripts/
    ├── build-netlify.sh    # Netlify build script
    └── build-azure.sh      # Azure build script
```

### Branch Strategy

- **`main`**: Production Netlify/Supabase deployment
- **`azure-poc`**: Azure migration development and testing
- **Feature branches**: Created from appropriate base branch

### Configuration Management

**Environment-Specific Files:**
- Database connection strings
- Authentication service configurations
- Real-time service endpoints
- Build and deployment configurations
- Environment variables

**Shared Files (80-90%):**
- React components and hooks
- Business logic and API controllers
- Test suites and documentation
- Utility functions and helpers

### Build Process (Updated with Adapter Pattern)

**Environment Variable Selection (Recommended):**
```bash
# Netlify Build
VITE_PLATFORM=netlify npm run build

# Azure Build
VITE_PLATFORM=azure npm run build
```

**Legacy File Copy Approach (Alternative):**
```bash
# Copy Netlify-specific configs
cp packages/frontend/config/netlify/vite.config.js packages/frontend/
cp packages/backend/config/supabase/database.js packages/backend/api/config/

# Build for Netlify
npm run build:netlify

# Copy Azure-specific configs
cp packages/frontend/config/azure/vite.config.js packages/frontend/
cp packages/backend/config/azure/database.js packages/backend/api/config/

# Build for Azure
npm run build:azure
```

## Consequences

### Positive

*   **Code Synchronization**: Eliminates sync issues for 80-90% shared codebase
*   **Simplified Development**: Single repository reduces management overhead
*   **Unified Testing**: Test both environments from same codebase
*   **Shared Git History**: Easy to track changes across environments
*   **Easier Collaboration**: No confusion about which repository to use
*   **Unified Documentation**: Single source for all environment docs
*   **Adapter Pattern Benefits**: Clean separation of platform-specific logic through interfaces and implementations

### Negative

*   **Build Complexity**: Requires different build scripts for each platform (mitigated by environment variables)
*   **Configuration Management**: Need to maintain environment-specific files
*   **Git History Clarity**: Mixed commits may be harder to categorize
*   **Risk Management**: Azure changes could potentially affect production branch
*   **Testing Complexity**: Must ensure proper environment isolation
*   **Platform Sprawl Risk**: Potential for platform-specific logic to leak into shared code (mitigated by Adapter Pattern)

### Mitigation Strategies

**Build Complexity:**
- Environment variable selection over file copying (recommended)
- Clear naming conventions for build scripts
- Documentation for each environment's build process
- Automated build validation

**Configuration Management:**
- Environment-specific config directories
- Clear naming conventions (netlify/ vs azure/)
- Version control for all configuration files
- Adapter Pattern for platform abstraction

**Risk Management:**
- Use feature flags for Azure-specific functionality
- Regular code reviews for azure-poc branch changes
- Clear commit message conventions ("Azure: ..." prefix)
- Branch protection rules for main branch

**Platform Sprawl Prevention:**
- Adapter Pattern for all platform-dependent services
- Interface definitions for platform abstractions
- Environment variable selection of implementations
- Strict code review for platform-specific logic in shared code

**Testing:**
- Environment-specific test configurations
- Parallel testing of both environments
- Automated validation of environment isolation
- Integration tests for adapter implementations

## Alternatives Considered

### Separate Repository Approach

**Pros:**
- Complete isolation between environments
- No risk of cross-contamination
- Clear separation of concerns

**Cons:**
- Code synchronization challenges for 80-90% shared code
- Dual repository management overhead
- More complex development workflow
- Harder to maintain shared components

**Decision:** Rejected due to synchronization overhead with large shared codebase

### Git Worktree Approach

**Pros:**
- Shared git history with separate working directories
- Independent development branches
- Easy to sync shared changes

**Cons:**
- More complex git workflow
- Requires understanding of worktree concepts
- Still requires manual synchronization

**Decision:** Considered but single repo with branches is simpler for POC

## Related Decisions

- ADR-015: Choice of Monorepo Structure
- ADR-016: Choice of E2E Testing Architecture
- ADR-018: Choice of SEO Implementation Strategy

## Success Metrics

### Technical Metrics
- [ ] Both environments build and deploy successfully
- [ ] Shared components work identically across platforms
- [ ] Environment-specific configurations are properly isolated
- [ ] Build scripts execute without manual intervention

### Process Metrics
- [ ] Development workflow remains efficient
- [ ] Code reviews can easily distinguish environment changes
- [ ] Testing covers both environments adequately
- [ ] Documentation clearly explains environment differences

### Quality Metrics
- [ ] No cross-contamination between environments
- [ ] Clear separation of shared vs environment-specific code
- [ ] Easy to maintain and extend configurations
- [ ] Rollback procedures are well-defined

## Adapter Pattern Implementation Guide

### Interface Definitions

**Create platform-agnostic interfaces in shared code:**

```typescript
// packages/backend/api/services/realtimeService.ts
export interface IRealtimeService {
  notifyRequestUpdate(requestId: string, data: any): Promise<void>;
  notifyNewQuote(quoteId: string, data: any): Promise<void>;
  notifyQuoteAccepted(requestId: string, data: any): Promise<void>;
}

// packages/backend/api/services/authService.ts
export interface IAuthService {
  getCurrentUser(): Promise<User | null>;
  validateToken(token: string): Promise<boolean>;
  getUserRoles(userId: string): Promise<string[]>;
}

// packages/backend/api/services/databaseService.ts
export interface IDatabaseService {
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  executeQuery(query: string, params?: any[]): Promise<any>;
}
```

### Platform-Specific Implementations

**Supabase Implementation:**
```typescript
// packages/backend/config/supabase/supabaseRealtimeService.ts
import { IRealtimeService } from '../../api/services/realtimeService';

export class SupabaseRealtimeService implements IRealtimeService {
  async notifyRequestUpdate(requestId: string, data: any): Promise<void> {
    // Supabase handles this automatically via database triggers
    logger.log("Supabase Realtime: automatic notification for", requestId);
    return Promise.resolve();
  }

  async notifyNewQuote(quoteId: string, data: any): Promise<void> {
    // Automatic via Supabase
    return Promise.resolve();
  }

  async notifyQuoteAccepted(requestId: string, data: any): Promise<void> {
    // Automatic via Supabase
    return Promise.resolve();
  }
}
```

**Azure Implementation:**
```typescript
// packages/backend/config/azure/azureSignalRService.ts
import { IRealtimeService } from '../../api/services/realtimeService';

export class AzureSignalRService implements IRealtimeService {
  private signalRClient: any; // Azure SignalR client

  async notifyRequestUpdate(requestId: string, data: any): Promise<void> {
    await this.signalRClient.sendToAll('request_updated', { requestId, data });
  }

  async notifyNewQuote(quoteId: string, data: any): Promise<void> {
    await this.signalRClient.sendToAll('quote_created', { quoteId, data });
  }

  async notifyQuoteAccepted(requestId: string, data: any): Promise<void> {
    await this.signalRClient.sendToAll('quote_accepted', { requestId, data });
  }
}
```

### Configuration Barrel File

**Environment-based service selection:**
```typescript
// packages/backend/api/config/index.ts
import { IRealtimeService } from '../services/realtimeService';
import { IAuthService } from '../services/authService';
import { IDatabaseService } from '../services/databaseService';

import { SupabaseRealtimeService } from './supabase/supabaseRealtimeService';
import { AzureSignalRService } from './azure/azureSignalRService';
import { SupabaseAuthService } from './supabase/supabaseAuthService';
import { AzureADAuthService } from './azure/azureADAuthService';
import { SupabaseDatabaseService } from './supabase/supabaseDatabaseService';
import { AzureDatabaseService } from './azure/azureDatabaseService';

// Environment-based service instantiation
const platform = process.env.VITE_PLATFORM || 'netlify';

export const realtimeService: IRealtimeService = platform === 'azure'
  ? new AzureSignalRService()
  : new SupabaseRealtimeService();

export const authService: IAuthService = platform === 'azure'
  ? new AzureADAuthService()
  : new SupabaseAuthService();

export const databaseService: IDatabaseService = platform === 'azure'
  ? new AzureDatabaseService()
  : new SupabaseDatabaseService();
```

### Shared Code Usage

**Platform-agnostic controller:**
```typescript
// packages/backend/api/controllers/requestController.js
import { realtimeService, databaseService } from '../config';

export async function updateRequest(requestId, updates) {
  // Update database (works for both platforms)
  const updatedRequest = await databaseService.executeQuery(
    'UPDATE requests SET ... WHERE id = $1',
    [requestId, ...updates]
  );

  // Notify clients (automatic for Supabase, manual for Azure)
  await realtimeService.notifyRequestUpdate(requestId, updatedRequest);

  return updatedRequest;
}
```

## Future Considerations

**Post-POC Evaluation:**
- If Azure POC proves successful, consider maintaining dual deployments from single repo
- If separate repositories prove necessary, can split at that time
- Consider infrastructure-as-code for environment management

**Scaling Considerations:**
- For multiple developers, may need stricter branch protection rules
- Consider automated testing across both environments
- May need more sophisticated configuration management
- Adapter Pattern scales well as new platforms are added

---

**Note:** This ADR reflects the decision to use a single repository strategy specifically for the Azure POC phase. The approach may be re-evaluated based on POC results and long-term maintenance requirements.
