# ADR-002: Hybrid Modular Monorepo Structure

## Status

Accepted

## Date

2025-12-02

## Context

The Workflow Manager needs to support:

1. **Multiple market roles** with varying complexity:
   - Balance Responsible Party (BRP)
   - Balance Service Provider (BSP)
   - Grid User (GU)
   - Access Contract Holder (ACH)
   - Customer Relationship Management (CRM)
   - Energy Service Provider (ESP)
   - Distribution System Operator (DSO)
   - Scheduling Agent (SA)
   - Outage Planning Agent (OPA)
   - Voltage Service Provider (VSP)

2. **Workflow variety**:
   - Generic workflows (contract onboarding, portfolio management)
   - Market role-specific customizations
   - Future custom workflows from internal teams

3. **Technical requirements**:
   - Hybrid database architecture (PostgreSQL + MongoDB)
   - GraphQL API backend
   - SvelteKit frontend for Market Operations
   - Integration with Kong Dev Portal
   - Background job processing

4. **Future extensibility**:
   - New market roles without core changes
   - Custom step handlers for specialized workflows
   - Third-party integrations
   - Potential microservice extraction

5. **Team considerations**:
   - Internal development team (Elia)
   - Need for clear module ownership
   - Balance simplicity with growth potential

## Decision

We will adopt a **Hybrid Modular Monorepo** structure with five top-level concerns:

1. **apps/**: Deployable applications (runtime executables)
2. **libs/**: Core reusable libraries (infrastructure)
3. **modules/**: Business capabilities (pluggable features)
4. **extensions/**: Optional/custom functionality
5. **tools/**: Development utilities

### Complete Structure

```
workflow-manager/
├── apps/                                   # Deployable Applications
│   ├── api/                               # GraphQL API Server
│   │   ├── src/
│   │   │   ├── index.ts                   # Entry point
│   │   │   ├── server.ts                  # Fastify/Express setup
│   │   │   ├── graphql/
│   │   │   │   ├── schema.ts              # GraphQL schema
│   │   │   │   ├── resolvers/
│   │   │   │   │   ├── workflow.resolver.ts
│   │   │   │   │   ├── tenant.resolver.ts
│   │   │   │   │   └── user.resolver.ts
│   │   │   │   └── context.ts             # GraphQL context (auth, loaders)
│   │   │   ├── middleware/
│   │   │   │   ├── auth.middleware.ts
│   │   │   │   ├── tenant.middleware.ts
│   │   │   │   └── logging.middleware.ts
│   │   │   ├── config/
│   │   │   │   └── env.ts                 # Environment variables
│   │   │   └── plugins/
│   │   │       └── health.plugin.ts       # Health check endpoints
│   │   ├── tests/
│   │   │   ├── integration/
│   │   │   └── unit/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── README.md
│   │
│   ├── admin-ui/                          # Market Operations Dashboard
│   │   ├── src/
│   │   │   ├── routes/                    # SvelteKit routes
│   │   │   │   ├── +layout.svelte
│   │   │   │   ├── +layout.ts
│   │   │   │   ├── +page.svelte           # Dashboard home
│   │   │   │   ├── workflows/
│   │   │   │   │   ├── +page.svelte       # Workflow list
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── +page.svelte   # Workflow detail
│   │   │   │   ├── tenants/
│   │   │   │   │   ├── +page.svelte       # Tenant list
│   │   │   │   │   └── [id]/
│   │   │   │   │       └── +page.svelte   # Tenant detail
│   │   │   │   └── analytics/
│   │   │   │       └── +page.svelte       # Reporting
│   │   │   ├── lib/
│   │   │   │   ├── components/            # App-specific components
│   │   │   │   ├── stores/                # Svelte stores
│   │   │   │   ├── api/                   # GraphQL client
│   │   │   │   │   └── client.ts
│   │   │   │   └── utils/
│   │   │   └── app.html
│   │   ├── static/
│   │   ├── tests/
│   │   ├── package.json
│   │   ├── svelte.config.js
│   │   ├── vite.config.ts
│   │   └── tsconfig.json
│   │
│   └── worker/                            # Background Job Processor
│       ├── src/
│       │   ├── index.ts
│       │   ├── jobs/
│       │   │   ├── workflow-cleanup.job.ts
│       │   │   ├── notification.job.ts
│       │   │   └── db-sync.job.ts
│       │   └── config/
│       ├── tests/
│       ├── package.json
│       └── tsconfig.json
│
├── libs/                                   # Core Infrastructure Libraries
│   ├── workflow-engine/                   # Workflow Execution Engine
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── engine/
│   │   │   │   ├── WorkflowEngine.ts      # Main engine class
│   │   │   │   ├── StateMachine.ts        # State transitions
│   │   │   │   └── ExecutionContext.ts    # Runtime context
│   │   │   ├── steps/
│   │   │   │   ├── StepHandler.ts         # Base interface
│   │   │   │   ├── StepRegistry.ts        # Plugin registry
│   │   │   │   └── handlers/              # Built-in handlers
│   │   │   │       ├── FormStepHandler.ts
│   │   │   │       ├── ApprovalStepHandler.ts
│   │   │   │       ├── ApiCallStepHandler.ts
│   │   │   │       └── NotificationStepHandler.ts
│   │   │   ├── state/
│   │   │   │   ├── StateManager.ts        # State persistence
│   │   │   │   ├── StateTransitions.ts    # Transition logic
│   │   │   │   └── StateSnapshot.ts       # Checkpoint support
│   │   │   ├── events/
│   │   │   │   ├── EventStore.ts          # Event sourcing
│   │   │   │   ├── EventTypes.ts          # Event definitions
│   │   │   │   └── EventReplay.ts         # Rollback support
│   │   │   └── operations/
│   │   │       ├── pause.ts               # Pause workflow
│   │   │       ├── resume.ts              # Resume workflow
│   │   │       ├── rollback.ts            # Rollback to step
│   │   │       └── validate.ts            # Validate state
│   │   ├── tests/
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── database/                          # Database Layer
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── postgres/
│   │   │   │   ├── client.ts              # PG connection pool
│   │   │   │   ├── migrations/            # SQL migrations
│   │   │   │   │   ├── 001_initial_schema.sql
│   │   │   │   │   └── 002_add_market_roles.sql
│   │   │   │   ├── repositories/
│   │   │   │   │   ├── TenantRepository.ts
│   │   │   │   │   ├── UserRepository.ts
│   │   │   │   │   ├── TemplateRepository.ts
│   │   │   │   │   └── WorkflowIndexRepository.ts
│   │   │   │   └── schema.sql
│   │   │   ├── mongodb/
│   │   │   │   ├── client.ts              # Mongo connection
│   │   │   │   ├── repositories/
│   │   │   │   │   ├── WorkflowRepository.ts
│   │   │   │   │   └── EventRepository.ts
│   │   │   │   └── indexes.ts             # Index definitions
│   │   │   └── sync/
│   │   │       ├── SyncService.ts         # Cross-DB sync
│   │   │       └── ReconciliationJob.ts   # Consistency checker
│   │   ├── tests/
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── shared/                            # Shared Code
│   │   ├── types/                         # TypeScript types
│   │   │   ├── src/
│   │   │   │   ├── index.ts
│   │   │   │   ├── tenant.ts
│   │   │   │   ├── workflow.ts
│   │   │   │   ├── user.ts
│   │   │   │   ├── market-roles.ts
│   │   │   │   └── events.ts
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── validation/                    # Validation Schemas
│   │   │   ├── src/
│   │   │   │   ├── index.ts
│   │   │   │   ├── tenant.schema.ts
│   │   │   │   ├── workflow.schema.ts
│   │   │   │   └── user.schema.ts
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   └── utils/                         # Utility Functions
│   │       ├── src/
│   │       │   ├── index.ts
│   │       │   ├── dates.ts
│   │       │   ├── formatters.ts
│   │       │   └── logger.ts
│   │       ├── package.json
│   │       └── README.md
│   │
│   └── ui/                                # UI Component Library
│       ├── src/
│       │   ├── index.ts
│       │   ├── workflow/
│       │   │   ├── WorkflowStepper.svelte
│       │   │   ├── WorkflowCard.svelte
│       │   │   ├── WorkflowStatus.svelte
│       │   │   └── StepRenderer.svelte
│       │   ├── forms/
│       │   │   ├── DynamicForm.svelte
│       │   │   ├── FormField.svelte
│       │   │   └── ValidationMessage.svelte
│       │   ├── layout/
│       │   │   ├── Sidebar.svelte
│       │   │   ├── Header.svelte
│       │   │   └── PageLayout.svelte
│       │   └── common/
│       │       ├── Button.svelte
│       │       ├── Card.svelte
│       │       └── Modal.svelte
│       ├── tests/
│       ├── package.json
│       └── README.md
│
├── modules/                                # Business Modules (Pluggable)
│   ├── workflows/                         # Workflow Definitions
│   │   ├── contract-onboarding/
│   │   │   ├── src/
│   │   │   │   ├── index.ts
│   │   │   │   ├── template.ts            # Generic onboarding template
│   │   │   │   ├── steps/                 # Custom steps for this workflow
│   │   │   │   └── validators.ts
│   │   │   ├── tests/
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── portfolio-management/
│   │   │   ├── src/
│   │   │   │   ├── index.ts
│   │   │   │   ├── add-delivery-points.ts
│   │   │   │   └── remove-delivery-points.ts
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   └── market-notifications/
│   │       ├── src/
│   │       ├── package.json
│   │       └── README.md
│   │
│   ├── market-roles/                      # Market Role Customizations
│   │   ├── brp/                          # Balance Responsible Party
│   │   │   ├── src/
│   │   │   │   ├── index.ts
│   │   │   │   ├── workflows/
│   │   │   │   │   ├── BRPOnboarding.ts   # BRP-specific onboarding
│   │   │   │   │   └── BRPPortfolio.ts
│   │   │   │   ├── validators/
│   │   │   │   │   └── brp-validators.ts
│   │   │   │   └── types/
│   │   │   │       └── brp-types.ts
│   │   │   ├── tests/
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── bsp/                          # Balance Service Provider
│   │   │   ├── src/
│   │   │   │   ├── index.ts
│   │   │   │   ├── workflows/
│   │   │   │   │   └── BSPOnboarding.ts
│   │   │   │   └── validators/
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── grid-user/
│   │   │   ├── src/
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── ach/                          # Access Contract Holder
│   │   │   ├── src/
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── crm/                          # Customer Relationship Management
│   │   │   ├── src/
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   ├── esp/                          # Energy Service Provider
│   │   │   ├── src/
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   │
│   │   └── dso/                          # Distribution System Operator
│   │       ├── src/
│   │       ├── package.json
│   │       └── README.md
│   │
│   └── integrations/                      # External System Integrations
│       ├── kong/                         # Kong Dev Portal
│       │   ├── src/
│       │   │   ├── index.ts
│       │   │   ├── KongClient.ts
│       │   │   ├── ProvisioningService.ts
│       │   │   └── types.ts
│       │   ├── tests/
│       │   ├── package.json
│       │   └── README.md
│       │
│       └── notification-service/         # Email/SMS notifications
│           ├── src/
│           │   ├── index.ts
│           │   └── NotificationClient.ts
│           ├── package.json
│           └── README.md
│
├── extensions/                            # Optional/Custom Extensions
│   ├── .gitkeep                          # Placeholder for future use
│   ├── README.md                         # Extension development guide
│   │
│   └── examples/                         # Example extensions
│       ├── custom-step-handler/
│       │   ├── src/
│       │   │   └── VideoCallStepHandler.ts
│       │   └── package.json
│       │
│       └── custom-workflow/
│           ├── src/
│           │   └── CustomOnboarding.ts
│           └── package.json
│
├── tools/                                 # Development Tools
│   ├── cli/                              # CLI tool
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── commands/
│   │   │   │   ├── generate.ts           # Generate module scaffolding
│   │   │   │   ├── migrate.ts            # Run database migrations
│   │   │   │   └── seed.ts               # Seed test data
│   │   │   └── templates/                # Code templates
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── scripts/                          # Utility scripts
│   │   ├── seed-data.ts                  # Seed databases
│   │   ├── generate-types.ts             # Generate GraphQL types
│   │   ├── migrate.ts                    # Run migrations
│   │   └── check-deps.ts                 # Dependency checker
│   │
│   └── test-utils/                       # Shared test utilities
│       ├── src/
│       │   ├── fixtures/
│       │   │   ├── tenants.ts
│       │   │   └── workflows.ts
│       │   ├── mocks/
│       │   │   ├── database.mock.ts
│       │   │   └── api.mock.ts
│       │   └── helpers/
│       │       └── test-helpers.ts
│       ├── package.json
│       └── README.md
│
├── documentation/                         # Project Documentation
│   ├── Architecture/
│   │   ├── ADRs/
│   │   │   ├── ADR-001-hybrid-database-architecture.md
│   │   │   └── ADR-002-hybrid-modular-monorepo-structure.md
│   │   ├── diagrams/
│   │   │   ├── system-overview.png
│   │   │   └── workflow-engine.png
│   │   └── system-overview.md
│   │
│   ├── guides/
│   │   ├── getting-started.md
│   │   ├── creating-workflows.md
│   │   ├── adding-market-roles.md
│   │   └── plugin-development.md
│   │
│   └── api/
│       ├── graphql-schema.md
│       └── rest-endpoints.md
│
├── docker/                                # Docker Configuration
│   ├── docker-compose.yml                # Local development
│   ├── docker-compose.prod.yml           # Production
│   ├── Dockerfile.api                    # API container
│   ├── Dockerfile.worker                 # Worker container
│   ├── Dockerfile.admin-ui               # Admin UI container
│   ├── postgres/
│   │   └── init.sql
│   └── mongodb/
│       └── init.js
│
├── .github/                               # GitHub Actions
│   └── workflows/
│       ├── ci.yml                        # CI pipeline
│       ├── test.yml                      # Test pipeline
│       └── release.yml                   # Release automation
│
├── .claude/
│   └── CLAUDE.md                         # AI assistant context
│
├── package.json                          # Root workspace config
├── pnpm-workspace.yaml                   # Workspace definition
├── turbo.json                            # Turborepo config
├── tsconfig.base.json                    # Shared TypeScript config
├── .gitignore
├── .prettierrc
├── .eslintrc.js
└── README.md
```

## Key Design Principles

### 1. Clear Separation of Concerns

**apps/**: Runtime executables

- Each app is independently deployable
- Apps compose functionality from libs and modules
- No business logic in apps (orchestration only)

**libs/**: Infrastructure and reusable code

- Framework-agnostic where possible
- Well-tested, stable APIs
- No app-specific code

**modules/**: Business capabilities

- Self-contained features
- Can depend on libs, not on other modules
- Can be extracted to microservices later

**extensions/**: Optional functionality

- Third-party or custom code
- Plugin-based architecture
- No dependencies on other extensions

**tools/**: Development utilities

- Not deployed to production
- Improve developer experience
- Shared across all packages

### 2. Dependency Flow

```
extensions ──→ modules ──→ libs
              ↓           ↓
              └─── apps ──┘
                   ↓
                 tools (dev only)
```

Rules:

- ✅ Apps can depend on libs and modules
- ✅ Modules can depend on libs only
- ✅ Extensions can depend on libs and modules
- ❌ Libs cannot depend on modules or apps
- ❌ Modules cannot depend on other modules
- ❌ Apps cannot depend on other apps

### 3. Module Boundaries

Each module in `modules/` must:

- Have a clear, single responsibility
- Export a well-defined public API
- Include its own tests
- Document its purpose in README.md
- Register with appropriate registry (workflows, integrations)

### 4. Market Role Isolation

Each market role package (`modules/market-roles/*/`) contains:

- Workflow templates specific to that role
- Validators for role-specific data
- TypeScript types for role domain
- Can be developed independently
- Can be owned by different team members

## Workspace Configuration

### pnpm-workspace.yaml

```yaml
packages:
  - 'apps/*'
  - 'libs/**'
  - 'modules/**'
  - 'extensions/*'
  - 'tools/*'
```

### package.json (root)

```json
{
  "name": "workflow-manager",
  "version": "1.0.0",
  "private": true,
  "workspaces": ["apps/*", "libs/**", "modules/**", "extensions/*", "tools/*"],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check",
    "clean": "turbo run clean && rm -rf node_modules",

    "dev:api": "pnpm --filter @workflow-manager/api dev",
    "dev:admin": "pnpm --filter @workflow-manager/admin-ui dev",
    "dev:worker": "pnpm --filter @workflow-manager/worker dev",

    "db:migrate": "pnpm --filter @workflow-manager/database migrate",
    "db:seed": "tsx tools/scripts/seed-data.ts",

    "generate:types": "tsx tools/scripts/generate-types.ts",
    "test:integration": "turbo run test:integration",
    "test:e2e": "turbo run test:e2e"
  },
  "devDependencies": {
    "turbo": "^2.3.0",
    "typescript": "^5.8.0",
    "@types/node": "^22.0.0",
    "prettier": "^3.4.0",
    "eslint": "^9.0.0",
    "tsx": "^4.7.0"
  }
}
```

### tsconfig.base.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022"],
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "baseUrl": ".",
    "paths": {
      "@workflow-manager/workflow-engine": ["./libs/workflow-engine/src"],
      "@workflow-manager/database": ["./libs/database/src"],
      "@workflow-manager/shared-types": ["./libs/shared/types/src"],
      "@workflow-manager/validation": ["./libs/shared/validation/src"],
      "@workflow-manager/utils": ["./libs/shared/utils/src"],
      "@workflow-manager/ui": ["./libs/ui/src"],

      "@workflow-manager/contract-onboarding": ["./modules/workflows/contract-onboarding/src"],
      "@workflow-manager/brp": ["./modules/market-roles/brp/src"],
      "@workflow-manager/bsp": ["./modules/market-roles/bsp/src"],
      "@workflow-manager/kong": ["./modules/integrations/kong/src"]
    }
  },
  "exclude": ["node_modules", "dist", "build"]
}
```

## Extensibility Patterns

### Adding a New Market Role

```bash
# 1. Create module
mkdir -p modules/market-roles/new-role/src/workflows
cd modules/market-roles/new-role

# 2. Initialize package
pnpm init

# 3. Create workflow template
cat > src/workflows/NewRoleOnboarding.ts << EOF
import type { WorkflowTemplate } from '@workflow-manager/shared-types';

export const NewRoleOnboarding: WorkflowTemplate = {
  id: 'new-role-onboarding',
  name: 'New Role Contract Onboarding',
  applicableRoles: ['NEW_ROLE'],
  steps: [/* ... */]
};
EOF

# 4. Register in module index
cat > src/index.ts << EOF
import { TemplateRegistry } from '@workflow-manager/workflow-engine';
import { NewRoleOnboarding } from './workflows/NewRoleOnboarding';

export function registerNewRoleWorkflows() {
  TemplateRegistry.register(NewRoleOnboarding);
}

export * from './workflows/NewRoleOnboarding';
EOF

# 5. Import in API app
# In apps/api/src/index.ts
import { registerNewRoleWorkflows } from '@workflow-manager/new-role';
registerNewRoleWorkflows();
```

### Adding a Custom Workflow

```bash
# In extensions/ folder
mkdir -p extensions/elia-2024-onboarding/src
cd extensions/elia-2024-onboarding

# Follow same pattern as modules
# Can depend on libs and modules
```

### Adding a Custom Step Handler

```bash
# In extensions/ folder
mkdir -p extensions/video-call-step/src
cd extensions/video-call-step

cat > src/VideoCallStepHandler.ts << EOF
import { StepHandler, StepRegistry } from '@workflow-manager/workflow-engine';

export class VideoCallStepHandler implements StepHandler {
  readonly type = 'video-call';

  async execute(step, input) {
    // Custom logic
  }
}

// Auto-register
StepRegistry.register(new VideoCallStepHandler());
EOF
```

## Consequences

### Positive

1. **Clear Structure**
   - Easy to navigate and understand
   - Obvious where code belongs
   - Self-documenting organization

2. **Market Role Isolation**
   - Each role is independent module
   - Can evolve separately
   - Clear ownership boundaries

3. **Extensibility**
   - New workflows without core changes
   - Plugin system for custom functionality
   - Third-party extensions possible

4. **Microservice Ready**
   - Modules have clear boundaries
   - Can extract to services with minimal refactoring
   - Dependencies already explicit

5. **Code Sharing**
   - Libs provide reusable infrastructure
   - UI components shared across apps
   - Types ensure consistency

6. **Developer Experience**
   - Predictable structure
   - Easy to find code
   - Clear conventions

7. **Testing**
   - Each package independently testable
   - Integration tests at app level
   - Clear test boundaries

### Negative

1. **More Folders**
   - Deeper nesting than flat structure
   - More navigation required
   - Can be overwhelming initially

2. **Module Discipline Required**
   - Need to enforce no cross-module dependencies
   - Temptation to shortcut rules
   - Requires team agreement

3. **Build Complexity**
   - Need build orchestration (Turbo)
   - Dependency order matters
   - Slower cold builds

4. **Import Paths**
   - Long package names
   - Need path mapping configuration
   - Can be confusing for new developers

5. **Initial Setup**
   - More boilerplate per package
   - Package.json for each module
   - TypeScript config in each package

### Mitigation Strategies

1. **Documentation**
   - Clear guide on where code belongs
   - Examples for each module type
   - Onboarding documentation

2. **Code Generation**
   - CLI tool to scaffold modules
   - Templates for common patterns
   - Automated package setup

3. **Linting**
   - ESLint rules to enforce dependencies
   - TypeScript project references
   - Automated checks in CI

4. **Developer Tools**
   - Scripts for common tasks
   - Good error messages
   - VS Code workspace config

## Migration Strategy

### Phase 1: Bootstrap (Week 1)

- Create folder structure
- Set up workspace configuration
- Configure TypeScript and build tools
- Create empty package.json files

### Phase 2: Core Infrastructure (Week 2-3)

- Implement `libs/database` (PG + Mongo)
- Implement `libs/workflow-engine`
- Implement `libs/shared/types`
- Basic tests for each

### Phase 3: First Module (Week 4-5)

- Implement `modules/workflows/contract-onboarding`
- Implement `modules/market-roles/brp`
- Integrate with workflow engine
- End-to-end test

### Phase 4: API & UI (Week 6-7)

- Build `apps/api` with GraphQL
- Build `apps/admin-ui` with SvelteKit
- Connect frontend to backend
- Authentication & authorization

### Phase 5: Additional Roles (Week 8-10)

- Implement remaining market roles (BSP, GU, ACH, etc.)
- Register with workflow engine
- Add role-specific validations

### Phase 6: Integrations & Extensions (Week 11-12)

- Implement Kong integration
- Create extension examples
- Document plugin development
- Polish developer experience

## Alternatives Considered

### Alternative 1: Apps + Packages (Flat)

- **Pros**: Simpler structure
- **Cons**: No clear place for market roles, less extensible
- **Rejected**: Doesn't handle market role diversity well

### Alternative 2: Feature-Based (DDD)

- **Pros**: Domain-driven, self-contained features
- **Cons**: More complex, steeper learning curve
- **Rejected**: Too complex for initial implementation

### Alternative 3: Layer-Based (Traditional)

- **Pros**: Familiar to many developers
- **Cons**: Less flexible, monolithic tendency
- **Rejected**: Not idiomatic for monorepos, harder to extract

### Alternative 4: Plugin-First (Maximum Extensibility)

- **Pros**: Maximum flexibility
- **Cons**: Over-engineered, slow initial development
- **Rejected**: Too complex for current needs

## Related ADRs

- ADR-001: Hybrid Database Architecture (PostgreSQL + MongoDB)
- ADR-003: Workflow Engine Design [Pending]
- ADR-004: Module Registration and Plugin System [Pending]
- ADR-005: GraphQL API Architecture [Pending]

## References

- [Turborepo Documentation](https://turbo.build/repo/docs)
- [pnpm Workspaces](https://pnpm.io/workspaces)
- [TypeScript Project References](https://www.typescriptlang.org/docs/handbook/project-references.html)
- [Module Pattern in Large Applications](https://blog.logrocket.com/organizing-code-modules-large-applications/)
