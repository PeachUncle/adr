# ADR-020: API Design Standards and Versioning Strategy

## Status

Proposed

## Decision Drivers

- Need consistent API design across all platform services
- Support for API evolution without breaking clients
- CQRS and event sourcing integration requirements from ADR-006
- Frontend framework needs from ADR-013
- Authentication and authorization requirements from ADR-003

## Context

The personal portfolio platform needs well-designed APIs for:

- Frontend application communication (from ADR-013)
- Potential external integrations (future collaboration features)
- Administrative operations and monitoring
- Mobile applications (future consideration)

We need consistent API design standards that support CQRS patterns, proper versioning, and align with our event-sourced architecture.

## Decision

### API Architecture Pattern: CQRS-Aligned REST + GraphQL Hybrid

**Command APIs (REST):**

- Use for state-changing operations (commands)
- POST/PUT/DELETE operations
- Return command execution status, not data
- Integrate with command handlers from CQRS pattern

**Query APIs (GraphQL):**

- Use for data retrieval (queries)
- Single endpoint with flexible data fetching
- Powered by projection read models from ADR-012
- Support for real-time subscriptions via WebSocket

### URL Structure and Conventions

**Command APIs:**

```
POST /api/v1/commands/projects/create
PUT /api/v1/commands/projects/{id}/update
POST /api/v1/commands/projects/{id}/grant-access
DELETE /api/v1/commands/projects/{id}/revoke-access

POST /api/v1/commands/contacts/submit
PUT /api/v1/commands/contacts/{id}/process

POST /api/v1/commands/users/register
PUT /api/v1/commands/users/{id}/update-profile
```

**Query APIs:**

```
POST /api/v1/graphql
GET /api/v1/query/health  # Simple health checks
GET /api/v1/query/schemas # API documentation
```

### Request/Response Patterns

#### Command API Patterns

```typescript
// Command Request Structure
interface CommandRequest {
  commandId: string; // Idempotency key
  commandType: string; // e.g., "CreateProject"
  aggregateId?: string; // Target aggregate
  data: Record<string, any>; // Command payload
  metadata: {
    userId: string;
    correlationId?: string;
    causationId?: string;
  };
}

// Command Response Structure
interface CommandResponse {
  commandId: string;
  status: 'accepted' | 'rejected' | 'failed';
  aggregateId?: string; // Created/modified aggregate ID
  aggregateVersion?: number; // New version after command
  errors?: CommandError[];
  timestamp: string;
}

interface CommandError {
  code: string; // Error code for client handling
  message: string; // Human-readable message
  field?: string; // Specific field if validation error
  details?: Record<string, any>;
}
```

#### GraphQL Query Patterns

```graphql
# Schema aligned with domain aggregates from ADR-005
type User {
  id: ID!
  email: String!
  profile: UserProfile!
  projects: [Project!]!
  createdAt: DateTime!
}

type Project {
  id: ID!
  title: String!
  description: String!
  content: String!
  visibility: ProjectVisibility!
  owner: User!
  accessGrants: [AccessGrant!]!
  tags: [String!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type ContactRequest {
  id: ID!
  fromEmail: String!
  subject: String!
  message: String!
  status: ContactStatus!
  submittedAt: DateTime!
  processedAt: DateTime
  response: String
}

# Query examples
type Query {
  me: User
  project(id: ID!): Project
  projects(filter: ProjectFilter, pagination: Pagination): ProjectConnection
  contactRequests(
    filter: ContactFilter
    pagination: Pagination
  ): ContactRequestConnection
}

# Real-time subscriptions for live updates
type Subscription {
  projectUpdated(projectId: ID!): Project
  contactRequestSubmitted: ContactRequest
}
```

### API Versioning Strategy

#### Version Scheme: Semantic Versioning

```
/api/v{MAJOR}/...
```

**Major Version Changes (v1 → v2):**

- Breaking changes to request/response structure
- Removal of fields or endpoints
- Changed behavior of existing endpoints

**Minor/Patch Changes (Backward Compatible):**

- New optional fields
- New endpoints
- Additional query capabilities
- Performance improvements

#### Version Support Policy

```typescript
interface APIVersionPolicy {
  currentVersion: string; // "v1"
  supportedVersions: string[]; // ["v1", "v2"]
  deprecatedVersions: {
    version: string;
    deprecationDate: string;
    sunsetDate: string;
  }[];
}

// Example: Version lifecycle
// v1.0 Released: 2025-09-01
// v2.0 Released: 2025-12-01 (v1 enters maintenance)
// v1 Deprecated: 2026-03-01 (6 months after v2)
// v1 Sunset: 2026-09-01 (12 months after v2)
```

### Authentication and Authorization Integration

```typescript
// Integration with ADR-003 authentication strategy
interface AuthenticatedRequest {
  headers: {
    Authorization: 'Bearer <jwt-token>';
    'X-Correlation-ID'?: string;
    'X-Request-ID'?: string;
  };
}

// Authorization middleware integration
interface APIEndpoint {
  path: string;
  method: HTTPMethod;
  auth: {
    required: boolean;
    roles?: string[]; // From ADR-003
    permissions?: string[]; // Fine-grained permissions
  };
  rateLimit?: {
    requests: number;
    windowMs: number;
  };
}
```

### Error Handling Standards

```typescript
// Standardized error response
interface APIError {
  error: {
    code: string; // Machine-readable error code
    message: string; // Human-readable description
    details?: any; // Additional error context
    timestamp: string; // ISO 8601 timestamp
    requestId: string; // For tracing
    path: string; // API endpoint that errored
  };
}

// Standard HTTP status codes usage
const HTTP_STATUS_USAGE = {
  200: 'Successful query or command execution',
  201: 'Resource created successfully',
  400: 'Invalid request syntax or validation errors',
  401: 'Authentication required or invalid',
  403: 'Insufficient permissions',
  404: 'Resource not found',
  409: 'Conflict (e.g., aggregate concurrency)',
  422: 'Business rule validation failed',
  429: 'Rate limit exceeded',
  500: 'Internal server error',
  503: 'Service temporarily unavailable',
};
```

### Performance and Caching Standards

```typescript
// Caching headers for query responses
interface CacheHeaders {
  'Cache-Control': string; // e.g., "public, max-age=300"
  ETag: string; // Based on aggregate version
  'Last-Modified': string; // From projection timestamp
  Vary: string; // e.g., "Authorization, Accept-Language"
}

// GraphQL query complexity limits
interface GraphQLLimits {
  maxQueryDepth: 10;
  maxQueryComplexity: 1000;
  maxResultSize: 1000; // Items per connection
  timeoutMs: 30000; // 30 second timeout
}
```

## Rationale

### CQRS Alignment

- **Commands via REST**: Natural fit for imperative operations
- **Queries via GraphQL**: Flexible data fetching matches projection read models
- **Clear separation**: Commands change state, queries read state

### API Versioning Benefits

- **Semantic versioning**: Clear compatibility expectations
- **URL-based versioning**: Simple for clients to understand and implement
- **Gradual migration**: Support multiple versions during transitions

### Error Handling Rationale

- **Consistent structure**: Predictable error format for all clients
- **Machine-readable codes**: Enable proper client error handling
- **Detailed context**: Support debugging and monitoring

## Implementation Guidance

### Prerequisites

- ADR-003 (Authentication) must be implemented for protected endpoints
- ADR-005 (Domain Model) defines the aggregate structure for APIs
- ADR-006 (Event Sourcing) provides command handling patterns
- ADR-012 (Projection Strategy) provides query data sources

### Implementation Steps

1. **Define API contracts**: Create OpenAPI specs for REST endpoints
2. **Implement command handlers**: Connect REST commands to CQRS command handlers
3. **Create GraphQL schema**: Map projections to GraphQL types
4. **Add authentication middleware**: Integrate with ADR-003 auth strategy
5. **Implement error handling**: Standardize error responses across all endpoints
6. **Add monitoring**: Track API performance and usage metrics

### Code Generation

```typescript
// Generate TypeScript clients from OpenAPI specs
interface ProjectCommands {
  createProject(request: CreateProjectRequest): Promise<CommandResponse>;
  updateProject(
    id: string,
    request: UpdateProjectRequest
  ): Promise<CommandResponse>;
  grantAccess(
    id: string,
    request: GrantAccessRequest
  ): Promise<CommandResponse>;
}

// Generate GraphQL clients
const GET_PROJECTS = gql`
  query GetProjects($filter: ProjectFilter) {
    projects(filter: $filter) {
      nodes {
        id
        title
        description
        visibility
        createdAt
      }
    }
  }
`;
```

### Validation Criteria

- All command APIs return consistent response structure
- GraphQL schema matches domain model from ADR-005
- Authentication integration works with ADR-003
- Error responses follow standard format
- API documentation is complete and accurate

## Consequences

### Positive

- Consistent API experience across all platform services
- Clear separation between commands and queries
- Flexible data fetching with GraphQL
- Proper versioning strategy for API evolution
- Integration with CQRS and event sourcing patterns

### Negative

- Additional complexity with dual API approach (REST + GraphQL)
- Learning curve for GraphQL if team is unfamiliar
- More complex testing with multiple API styles
- Version management overhead

### Neutral

- GraphQL adds query flexibility but requires schema management
- Command/Query separation requires careful endpoint design

## Alternatives Considered

### Alternative 1: Pure REST API

- **Description**: Traditional REST for all operations
- **Pros**: Simple, widely understood, good tooling
- **Cons**: Over-fetching/under-fetching issues, doesn't align well with CQRS
- **Why rejected**: GraphQL better matches projection-based queries

### Alternative 2: Pure GraphQL API

- **Description**: GraphQL for both queries and mutations
- **Pros**: Single API technology, flexible for all operations
- **Cons**: Mutations don't map well to command semantics, caching complexity
- **Why rejected**: Commands better served by REST's imperative nature

### Alternative 3: Header-Based Versioning

- **Description**: Use Accept/Content-Type headers for versioning
- **Pros**: Clean URLs, RESTful approach
- **Cons**: Less discoverable, harder for clients to implement
- **Why rejected**: URL-based versioning is more practical for this scale

## Related ADRs

### Dependencies

- **Requires**: ADR-003 (Authentication Strategy) - For protected endpoints
- **Requires**: ADR-005 (Domain Model) - Defines aggregate structure
- **Requires**: ADR-006 (Event Sourcing) - Command handling patterns
- **Requires**: ADR-012 (Projection Strategy) - Query data sources

### Influences

- **Influences**: ADR-013 (Frontend Framework) - Client-side API consumption
- **Influences**: ADR-010 (Observability) - API monitoring and metrics

### Conflicts

- **None identified** - Designed to integrate with existing ADRs

## AI Agent Guidance

### Implementation Priority

**High** - Required for frontend integration and external access

### Code Generation Patterns

```typescript
// Always generate TypeScript interfaces from OpenAPI specs
interface APIClient {
  commands: CommandAPI;
  queries: GraphQLClient;
  auth: AuthenticationClient;
}

// Follow consistent naming conventions
// Commands: /api/v1/commands/{aggregate}/{action}
// Queries: GraphQL with aggregate-based schema
```

### Common Pitfalls

- **Mixing concerns**: Don't put queries in command endpoints or vice versa
- **Missing authentication**: All protected endpoints must verify tokens
- **Inconsistent errors**: Always use standard error response format
- **Version sprawl**: Don't create new API versions unnecessarily

### Integration Points

- Commands must trigger domain events (ADR-006)
- Queries must use projection data (ADR-012)
- Authentication must follow JWT patterns (ADR-003)
- Errors must be observable (ADR-010)

## Technical Debt Introduced

- **API versioning overhead**: Must maintain multiple versions during transitions
- **GraphQL complexity**: Schema evolution and query optimization requirements
- **Documentation maintenance**: Must keep OpenAPI specs and GraphQL schema current

## Evolution Path

- **Review trigger**: When client feedback indicates API limitations
- **Planned evolution**: Add real-time subscriptions, improve caching
- **Migration strategy**: New major versions with gradual client migration

---

_Last Updated: September 10, 2025_
