# ADR-0008: Internal Service Catalog Strategy

## Status
Accepted

## Context
While our system is designed to integrate with external service catalogs (Port, Backstage, etc.), many users may not have an existing service catalog solution. However, we still need reliable service metadata to:
- Track ownership of services
- Manage deployment configurations
- Handle service dependencies
- Store environment-specific settings
- Maintain deployment history

We need to balance providing essential service metadata management without attempting to replicate full-featured service catalogs.

## Decision
We will implement a lightweight internal service catalog with the following characteristics:

### Core Features
1. **Essential Service Metadata**
   - Service name and description
   - Repository information
   - Team ownership
   - Basic dependencies
   - Deployment configurations
   - Environment settings

2. **Minimal Schema**
   ```yaml
   service:
     name: string
     description: string
     repository:
       url: string
       type: "github" # Initially only supporting GitHub
       branch: string
     owner:
       team: string
       slack: string? # Optional
       email: string
     dependencies:
       services: string[] # Names of other services
       external: # External dependencies
         - name: string
           type: string # e.g., "database", "cache", "queue"
     deployment:
       strategy: string
       environments:
         - name: string
           config: object
   ```

3. **Storage Strategy**
   - Git-based storage (in the service's repository)
   - Service manifests stored as YAML
   - Version controlled with the application code
   - Support for environment-specific overrides

### Integration Capabilities
1. **External Catalog Sync**
   - Export internal catalog data
   - Import from external catalogs
   - Bidirectional sync where needed
   - Conflict resolution strategies

2. **API Access**
   - Read service metadata
   - Update deployment configs
   - Query service relationships
   - Track deployment history

## Rationale

### Why an Internal Catalog?
1. **Reduced Friction**
   - No external dependencies required
   - Simpler initial setup
   - Lower barrier to entry

2. **GitOps Alignment**
   - Metadata lives with code
   - Version controlled changes
   - Review process for updates
   - Audit trail built-in

3. **Migration Path**
   - Start simple
   - Grow with needs
   - Easy export to external systems
   - No lock-in to our implementation

### Scope Limitations
1. **What We Won't Do**
   - UI for service exploration
   - Rich documentation features
   - Team management
   - Asset management
   - API documentation
   - Infrastructure catalog

2. **What We Will Do**
   - Track essential metadata
   - Manage deployment configs
   - Store environment settings
   - Track dependencies
   - Maintain deployment history

## Consequences

### Positive
- Lower barrier to entry
- No external dependencies
- GitOps-friendly approach
- Clear upgrade path
- Focused feature set

### Negative
- Limited compared to full catalogs
- Another metadata format to maintain
- Potential sync complexity
- May need migration tools

## Implementation Impact

### Architecture Changes
1. **New Components**
   - Service metadata parser
   - Git-based metadata store
   - Catalog API endpoints
   - Sync controllers for external catalogs

2. **Modified Components**
   - Deployment workflow to use catalog
   - Configuration management
   - Status reporting

### Feature Implications
1. **Enhanced**
   - Self-service deployments
   - Configuration management
   - Dependency tracking
   - Deployment history

2. **Limited**
   - Service discovery
   - Documentation
   - Team management
   - Asset tracking

## Migration Strategy
1. **Starting Fresh**
   - Use internal catalog
   - Define service manifests
   - Start tracking deployments

2. **External Catalog Exists**
   - Import existing metadata
   - Map to internal schema
   - Set up sync if needed
   - Validate consistency

## Compliance
- Service manifests must be version controlled
- Changes must follow GitOps workflow
- Sensitive data must be secured
- External sync must be configurable
- Schema changes require migration plan 