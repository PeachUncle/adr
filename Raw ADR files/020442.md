# ADR-004: GraphQL API Architecture

## Status

Accepted

## Date

2025-12-02

## Context

The Workflow Manager API needs to:

1. **Support Multiple Clients**:
   - Admin UI (Market Operations dashboard)
   - Future: Participant portal
   - Future: Mobile applications
   - Future: Third-party integrations

2. **Flexible Data Fetching**:
   - Workflows with nested tenant/user data
   - Selective field retrieval
   - Batch loading for performance
   - Real-time updates (nice-to-have)

3. **Type Safety**:
   - Strong typing across frontend/backend
   - Auto-generated TypeScript types
   - Schema-first or code-first approach

4. **Multi-Tenancy**:
   - Tenant isolation at API level
   - Row-level security enforcement
   - Cross-tenant queries for Market Ops

5. **Performance**:
   - N+1 query problem mitigation
   - Efficient database queries
   - Caching strategy

6. **Developer Experience**:
   - GraphQL Playground for development
   - Auto-complete in IDEs
   - Good error messages

## Decision

We will implement a **GraphQL API** using:

- **Fastify** as HTTP server
- **Mercurius** as GraphQL server
- **Code-first** approach with TypeScript
- **DataLoader** for batching and caching
- **GraphQL Codegen** for type generation

### Why GraphQL over REST?

| Requirement          | GraphQL                    | REST                      |
| -------------------- | -------------------------- | ------------------------- |
| Flexible queries     | ✅ Client specifies fields | ❌ Fixed endpoints        |
| Type safety          | ✅ Schema + codegen        | ⚠️ Manual typing          |
| Avoid over-fetching  | ✅ Request only needed     | ❌ Return full objects    |
| Avoid under-fetching | ✅ Single request          | ❌ Multiple requests      |
| Real-time            | ✅ Subscriptions           | ❌ Need WebSocket         |
| Nested data          | ✅ Natural                 | ❌ N+1 or denormalization |

### Architecture Overview

```
┌─────────────┐
│   Client    │
│  (SvelteKit)│
└──────┬──────┘
       │ GraphQL Query/Mutation
       ▼
┌─────────────────────────────────┐
│      Fastify Server             │
│  ┌───────────────────────────┐  │
│  │   Mercurius (GraphQL)     │  │
│  │  ┌─────────────────────┐  │  │
│  │  │   GraphQL Schema    │  │  │
│  │  └─────────────────────┘  │  │
│  │  ┌─────────────────────┐  │  │
│  │  │     Resolvers       │  │  │
│  │  │  ┌───────────────┐  │  │  │
│  │  │  │  DataLoaders  │  │  │  │
│  │  │  └───────────────┘  │  │  │
│  │  └─────────────────────┘  │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │      Middleware           │  │
│  │  • Authentication         │  │
│  │  • Tenant Context         │  │
│  │  • Logging                │  │
│  └───────────────────────────┘  │
└─────────────┬───────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   Workflow Engine   │
    │   Database Layer    │
    └─────────────────────┘
```

### GraphQL Schema

```graphql
# apps/api/src/graphql/schema.graphql

# ============================================
# Scalars
# ============================================

scalar DateTime
scalar JSON

# ============================================
# Enums
# ============================================

enum MarketRole {
  BRP
  BSP
  GRID_USER
  ACH
  CRM
  ESP
  DSO
  SA
  OPA
  VSP
}

enum WorkflowStatus {
  DRAFT
  IN_PROGRESS
  PAUSED
  AWAITING_VALIDATION
  SUBMITTED
  COMPLETED
  FAILED
  ROLLED_BACK
}

enum StepStatus {
  PENDING
  IN_PROGRESS
  COMPLETED
  PAUSED
  FAILED
  SKIPPED
}

# ============================================
# Types
# ============================================

type Tenant {
  id: ID!
  companyName: String!
  vatNumber: String!
  status: String!
  marketRoles: [TenantMarketRole!]!
  workflows(status: WorkflowStatus, limit: Int, offset: Int): [WorkflowInstance!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type TenantMarketRole {
  id: ID!
  tenant: Tenant!
  role: MarketRole!
  status: String!
  onboardedAt: DateTime
  contractReference: String
}

type User {
  id: ID!
  tenant: Tenant!
  email: String!
  name: String!
  role: String!
  createdAt: DateTime!
}

type WorkflowTemplate {
  id: ID!
  name: String!
  description: String
  applicableRoles: [MarketRole!]!
  version: Int!
  definition: JSON!
  createdAt: DateTime!
}

type WorkflowInstance {
  id: ID!
  tenant: Tenant!
  marketRole: MarketRole!
  template: WorkflowTemplate!
  status: WorkflowStatus!
  currentStep: WorkflowStep
  state: WorkflowState!
  events: [WorkflowEvent!]!
  createdBy: User
  createdAt: DateTime!
  updatedAt: DateTime!
}

type WorkflowState {
  currentStepId: String!
  stepStates: [StepState!]!
  metadata: JSON
}

type StepState {
  stepId: String!
  status: StepStatus!
  data: JSON
  validationErrors: [ValidationError!]
  startedAt: DateTime
  completedAt: DateTime
  pausedAt: DateTime
}

type WorkflowStep {
  id: String!
  type: String!
  title: String!
  config: JSON!
  next: JSON!
}

type WorkflowEvent {
  id: ID!
  workflowInstance: WorkflowInstance!
  eventType: String!
  stepId: String
  eventData: JSON!
  performedBy: User
  occurredAt: DateTime!
}

type ValidationError {
  field: String!
  message: String!
}

# ============================================
# Inputs
# ============================================

input CreateWorkflowInput {
  tenantId: ID!
  marketRole: MarketRole!
  templateId: ID!
}

input ExecuteStepInput {
  workflowId: ID!
  stepId: String!
  data: JSON!
}

input TenantFilterInput {
  status: String
  marketRole: MarketRole
  search: String
}

input WorkflowFilterInput {
  tenantId: ID
  status: WorkflowStatus
  marketRole: MarketRole
  createdAfter: DateTime
  createdBefore: DateTime
}

# ============================================
# Queries
# ============================================

type Query {
  # Tenant queries
  tenant(id: ID!): Tenant
  tenants(filter: TenantFilterInput, limit: Int, offset: Int): [Tenant!]!

  # Workflow queries
  workflow(id: ID!): WorkflowInstance
  workflows(filter: WorkflowFilterInput, limit: Int, offset: Int): [WorkflowInstance!]!

  # Template queries
  template(id: ID!): WorkflowTemplate
  templates(marketRole: MarketRole): [WorkflowTemplate!]!

  # Current user
  me: User!
}

# ============================================
# Mutations
# ============================================

type Mutation {
  # Workflow lifecycle
  createWorkflow(input: CreateWorkflowInput!): WorkflowInstance!
  executeStep(input: ExecuteStepInput!): StepResult!
  pauseWorkflow(workflowId: ID!): WorkflowInstance!
  resumeWorkflow(workflowId: ID!): WorkflowInstance!
  rollbackWorkflow(workflowId: ID!, toStepId: String!): WorkflowInstance!
  validateWorkflow(workflowId: ID!): ValidationResult!
  submitWorkflow(workflowId: ID!): WorkflowInstance!

  # Tenant management (Market Ops only)
  createTenant(input: CreateTenantInput!): Tenant!
  updateTenant(id: ID!, input: UpdateTenantInput!): Tenant!
}

# ============================================
# Mutation Results
# ============================================

type StepResult {
  success: Boolean!
  workflow: WorkflowInstance!
  errors: [ValidationError!]
}

type ValidationResult {
  valid: Boolean!
  errors: [ValidationError!]!
}

# ============================================
# Subscriptions (Future)
# ============================================

type Subscription {
  workflowUpdated(workflowId: ID!): WorkflowInstance!
}
```

### Resolver Implementation

```typescript
// apps/api/src/graphql/resolvers/workflow.resolver.ts

import { WorkflowEngine } from '@workflow-manager/workflow-engine';
import { WorkflowRepository } from '@workflow-manager/database';

export const workflowResolvers = {
  Query: {
    workflow: async (_parent: any, args: { id: string }, context: GraphQLContext) => {
      // Tenant isolation enforced via context
      return await context.loaders.workflow.load(args.id);
    },

    workflows: async (
      _parent: any,
      args: { filter?: WorkflowFilterInput; limit?: number; offset?: number },
      context: GraphQLContext
    ) => {
      const filter = {
        ...args.filter,
        // Enforce tenant isolation for non-Market Ops users
        ...(context.user.role !== 'market_ops' && {
          tenantId: context.user.tenantId,
        }),
      };

      return await context.repositories.workflow.find(filter, {
        limit: args.limit || 50,
        offset: args.offset || 0,
      });
    },
  },

  Mutation: {
    createWorkflow: async (_parent: any, args: { input: CreateWorkflowInput }, context: GraphQLContext) => {
      // Validate user has access to tenant
      if (context.user.tenantId !== args.input.tenantId && context.user.role !== 'market_ops') {
        throw new ForbiddenError('Cannot create workflow for different tenant');
      }

      const workflowId = await context.services.workflowEngine.create({
        tenantId: args.input.tenantId,
        marketRole: args.input.marketRole,
        templateId: args.input.templateId,
        createdBy: context.user.id,
      });

      return await context.loaders.workflow.load(workflowId);
    },

    executeStep: async (_parent: any, args: { input: ExecuteStepInput }, context: GraphQLContext) => {
      const workflow = await context.loaders.workflow.load(args.input.workflowId);

      // Validate access
      if (workflow.tenantId !== context.user.tenantId && context.user.role !== 'market_ops') {
        throw new ForbiddenError('Cannot execute step for different tenant');
      }

      try {
        const result = await context.services.workflowEngine.executeStep(
          args.input.workflowId,
          args.input.stepId,
          args.input.data,
          {
            tenantId: workflow.tenantId,
            userId: context.user.id,
          }
        );

        // Clear loader cache
        context.loaders.workflow.clear(args.input.workflowId);

        return {
          success: result.success,
          workflow: await context.loaders.workflow.load(args.input.workflowId),
          errors: result.errors || [],
        };
      } catch (error) {
        return {
          success: false,
          workflow,
          errors: [{ field: 'general', message: error.message }],
        };
      }
    },

    pauseWorkflow: async (_parent: any, args: { workflowId: string }, context: GraphQLContext) => {
      await context.services.workflowEngine.pause(args.workflowId, {
        userId: context.user.id,
        tenantId: context.user.tenantId,
      });

      context.loaders.workflow.clear(args.workflowId);
      return await context.loaders.workflow.load(args.workflowId);
    },

    resumeWorkflow: async (_parent: any, args: { workflowId: string }, context: GraphQLContext) => {
      await context.services.workflowEngine.resume(args.workflowId, {
        userId: context.user.id,
        tenantId: context.user.tenantId,
      });

      context.loaders.workflow.clear(args.workflowId);
      return await context.loaders.workflow.load(args.workflowId);
    },

    rollbackWorkflow: async (_parent: any, args: { workflowId: string; toStepId: string }, context: GraphQLContext) => {
      await context.services.workflowEngine.rollback(args.workflowId, args.toStepId, {
        userId: context.user.id,
        tenantId: context.user.tenantId,
      });

      context.loaders.workflow.clear(args.workflowId);
      return await context.loaders.workflow.load(args.workflowId);
    },
  },

  WorkflowInstance: {
    tenant: async (parent: WorkflowInstance, _args: any, context: GraphQLContext) => {
      return await context.loaders.tenant.load(parent.tenantId);
    },

    template: async (parent: WorkflowInstance, _args: any, context: GraphQLContext) => {
      return await context.loaders.template.load(parent.templateId);
    },

    createdBy: async (parent: WorkflowInstance, _args: any, context: GraphQLContext) => {
      if (!parent.createdBy) return null;
      return await context.loaders.user.load(parent.createdBy);
    },

    events: async (parent: WorkflowInstance, _args: any, context: GraphQLContext) => {
      return await context.repositories.event.findByWorkflowId(parent.id);
    },
  },
};
```

### DataLoader Implementation

```typescript
// apps/api/src/graphql/context.ts

import DataLoader from 'dataloader';

export interface GraphQLContext {
  user: AuthenticatedUser;
  loaders: {
    workflow: DataLoader<string, WorkflowInstance>;
    tenant: DataLoader<string, Tenant>;
    user: DataLoader<string, User>;
    template: DataLoader<string, WorkflowTemplate>;
  };
  repositories: {
    workflow: WorkflowRepository;
    tenant: TenantRepository;
    user: UserRepository;
    template: TemplateRepository;
    event: EventRepository;
  };
  services: {
    workflowEngine: WorkflowEngine;
  };
}

export function createContext(request: FastifyRequest): GraphQLContext {
  const user = request.user; // Set by auth middleware

  // Create DataLoaders for batching
  const loaders = {
    workflow: new DataLoader(async (ids: readonly string[]) => {
      const workflows = await workflowRepository.findByIds(ids);
      return ids.map(id => workflows.find(w => w.id === id));
    }),

    tenant: new DataLoader(async (ids: readonly string[]) => {
      const tenants = await tenantRepository.findByIds(ids);
      return ids.map(id => tenants.find(t => t.id === id));
    }),

    user: new DataLoader(async (ids: readonly string[]) => {
      const users = await userRepository.findByIds(ids);
      return ids.map(id => users.find(u => u.id === id));
    }),

    template: new DataLoader(async (ids: readonly string[]) => {
      const templates = await templateRepository.findByIds(ids);
      return ids.map(id => templates.find(t => t.id === id));
    }),
  };

  return {
    user,
    loaders,
    repositories: {
      workflow: workflowRepository,
      tenant: tenantRepository,
      user: userRepository,
      template: templateRepository,
      event: eventRepository,
    },
    services: {
      workflowEngine: new WorkflowEngine(/* ... */),
    },
  };
}
```

### Server Setup

```typescript
// apps/api/src/server.ts

import Fastify from 'fastify';
import mercurius from 'mercurius';
import { loadSchemaFiles } from '@mercuriusjs/load-files';

const app = Fastify({ logger: true });

// Authentication middleware
app.addHook('onRequest', async (request, reply) => {
  // Extract JWT from Authorization header
  const token = request.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    reply.code(401).send({ error: 'Unauthorized' });
    return;
  }

  // Verify and decode token
  const user = await verifyToken(token);
  request.user = user;
});

// Tenant context middleware
app.addHook('onRequest', async (request, reply) => {
  if (request.user) {
    // Set PostgreSQL session variable for RLS
    await db.query('SET LOCAL app.current_tenant = $1', [request.user.tenantId]);
  }
});

// Register Mercurius GraphQL
app.register(mercurius, {
  schema: loadSchemaFiles('src/graphql/schema.graphql'),
  resolvers: {
    ...workflowResolvers,
    ...tenantResolvers,
    ...userResolvers,
  },
  context: createContext,
  graphiql: process.env.NODE_ENV === 'development',
  playground: process.env.NODE_ENV === 'development',
});

app.listen({ port: 4000 });
```

### Type Generation

```yaml
# codegen.yml

schema: 'apps/api/src/graphql/schema.graphql'
generates:
  # Backend types
  apps/api/src/graphql/generated/types.ts:
    plugins:
      - typescript
      - typescript-resolvers
    config:
      useIndexSignature: true
      contextType: '../context#GraphQLContext'

  # Frontend types
  apps/admin-ui/src/lib/graphql/generated/types.ts:
    plugins:
      - typescript
      - typescript-operations
      - typescript-urql
    config:
      withHooks: true
```

### Client Usage (SvelteKit)

```typescript
// apps/admin-ui/src/lib/api/client.ts

import { createClient } from '@urql/svelte';

export const client = createClient({
  url: 'http://localhost:4000/graphql',
  fetchOptions: () => ({
    headers: {
      authorization: `Bearer ${getToken()}`,
    },
  }),
});

// apps/admin-ui/src/routes/workflows/[id]/+page.ts

import { gql } from '@urql/svelte';

const WORKFLOW_QUERY = gql`
  query GetWorkflow($id: ID!) {
    workflow(id: $id) {
      id
      status
      currentStep {
        id
        title
      }
      tenant {
        companyName
      }
      state {
        stepStates {
          stepId
          status
          data
        }
      }
    }
  }
`;

export async function load({ params, parent }) {
  const { client } = await parent();
  const result = await client.query(WORKFLOW_QUERY, { id: params.id });

  return {
    workflow: result.data?.workflow,
  };
}
```

## Consequences

### Positive

1. **Flexible Queries**
   - Clients request exactly what they need
   - No over-fetching or under-fetching
   - Nested data in single request

2. **Type Safety**
   - Auto-generated TypeScript types
   - Compile-time type checking
   - IDE autocomplete

3. **Performance**
   - DataLoader batches queries
   - Solves N+1 problem
   - Efficient database queries

4. **Developer Experience**
   - GraphQL Playground
   - Schema introspection
   - Good error messages

5. **Versioning**
   - No API versioning needed
   - Add fields without breaking
   - Deprecation warnings

6. **Multi-Tenancy**
   - Context enforces isolation
   - RLS at database level
   - Clear access control

### Negative

1. **Learning Curve**
   - GraphQL concepts
   - Resolver patterns
   - DataLoader usage

2. **Complexity**
   - More setup than REST
   - Schema + resolvers + types
   - DataLoader management

3. **Query Complexity**
   - Deep nested queries can be expensive
   - Need query complexity limits
   - Caching more complex

4. **Tooling**
   - Need code generation
   - GraphQL-specific tools
   - Debugging can be harder

### Mitigation Strategies

1. **Query Complexity Limits**
   - Mercurius query depth plugin
   - Cost analysis for queries
   - Rate limiting

2. **Documentation**
   - Schema documentation
   - Resolver patterns guide
   - Client usage examples

3. **Monitoring**
   - Query performance tracking
   - Error rate monitoring
   - Resolver timing

4. **Caching**
   - DataLoader per-request cache
   - Redis for longer cache
   - CDN for public queries

## Alternatives Considered

### Alternative 1: REST API

- **Pros**: Simple, well-known, less tooling
- **Cons**: Over-fetching, multiple requests, no type generation
- **Rejected**: GraphQL better for flexible frontend needs

### Alternative 2: tRPC

- **Pros**: Type-safe, simpler than GraphQL, no schema
- **Cons**: TypeScript-only, less flexible than GraphQL
- **Rejected**: GraphQL more future-proof for non-TS clients

### Alternative 3: GraphQL + Apollo Server

- **Pros**: Popular, many plugins, good docs
- **Cons**: Heavier than Mercurius, slower
- **Rejected**: Mercurius faster and integrates with Fastify

## Related ADRs

- ADR-002: Hybrid Modular Monorepo Structure
- ADR-003: Workflow Engine Design
- ADR-005: Authentication & Authorization [Pending]

## References

- [Mercurius Documentation](https://mercurius.dev/)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [DataLoader](https://github.com/graphql/dataloader)
- [GraphQL Codegen](https://the-guild.dev/graphql/codegen)
