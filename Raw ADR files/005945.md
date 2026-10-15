# ADR-001: Separate Frontend and Backend Architecture

**Date**: 2025-10-24
**Status**: Accepted
**Author**: Leo (System Architect)
**Reviewed By**: CTO

---

## Context

When designing the `antarose-template-nodejs` project structure, we needed to decide between:

1. **Separate projects**: Frontend and backend as independent projects with separate `package.json`
2. **Monorepo**: Using Turborepo, Nx, or pnpm workspaces to manage both frontend and backend in a single repository with shared dependencies

This decision impacts:
- Development workflow
- Dependency management
- Deployment strategy
- Team collaboration
- Type sharing capabilities
- Maintenance complexity

---

## Decision

We decided to use **separate frontend and backend** architecture:

- `frontend/` - Standalone Next.js project with its own `package.json`
- `backend/` - Standalone Express project with its own `package.json`
- No shared workspace or monorepo tooling

### Project Structure

```
antarose-template-nodejs/
├── frontend/                # Independent Next.js project
│   ├── package.json
│   ├── node_modules/
│   └── ...
├── backend/                 # Independent Express project
│   ├── package.json
│   ├── node_modules/
│   └── ...
├── docs/
└── README.md
```

---

## Rationale

### Advantages of Separate Architecture

#### 1. Dependency Isolation
**Problem with Monorepo**: Frontend and backend dependencies can conflict
- Frontend might need `react@19.0.0`
- Backend might indirectly depend on older React through some tool
- Monorepo workspace resolution can cause version conflicts

**Solution with Separation**: Complete isolation
- Frontend has its own `node_modules/` with only frontend dependencies
- Backend has its own `node_modules/` with only backend dependencies
- Zero chance of dependency conflicts

**Real-world example**:
```bash
# Frontend needs
next@15.1.6
react@19.0.0

# Backend needs
express@5.1.0
# No React dependency at all
```

#### 2. Independent Deployment
**Flexibility**:
- Deploy frontend to Vercel (optimized for Next.js)
- Deploy backend to Railway (optimized for Node.js APIs)
- Deploy them to completely different platforms if needed

**Scaling**:
- Scale frontend independently (static files via CDN)
- Scale backend independently (add more API servers)
- No need to redeploy frontend when backend changes, and vice versa

**Example Deployment**:
```
Frontend: Vercel (or Netlify, Cloudflare Pages)
Backend:  Railway (or Render, AWS, DigitalOcean)
```

#### 3. Team Autonomy
**Separate Workflows**:
- Frontend team can update Next.js without backend team coordination
- Backend team can refactor API without affecting frontend build
- Different CI/CD pipelines for frontend and backend
- Faster CI/CD (only build what changed)

**Example**:
```bash
# Frontend team pushes changes
→ Only frontend tests run
→ Only frontend deploys

# Backend team pushes changes
→ Only backend tests run
→ Only backend deploys
```

#### 4. Simplified Mental Model
**Easier to Understand**:
- New developers only need to understand one side initially
- Clear boundary between frontend and backend
- Easier debugging (no workspace magic to understand)
- Standard `npm install` workflow (no special tools)

**Onboarding**:
```bash
# Clear, standard workflow
cd frontend
npm install
npm run dev

cd backend
npm install
npm run dev
```

#### 5. Smaller `node_modules`
**Faster Install**:
- Frontend `node_modules`: ~200MB (only frontend deps)
- Backend `node_modules`: ~50MB (only backend deps)
- Total: ~250MB

**Monorepo Alternative**:
- Shared `node_modules`: ~280MB (all deps + workspace overhead)
- Hoisting can cause unexpected behavior

#### 6. Microservices-Ready
**Future Architecture**:
- Easy to add more backend services
- Each service can be a separate project
- No monorepo tool lock-in

**Example Evolution**:
```
antarose-template-nodejs/
├── frontend/
├── backend-api/           # Main API
├── backend-auth/          # Auth service (future)
└── backend-jobs/          # Background jobs (future)
```

---

### Disadvantages of Separate Architecture

#### 1. No Type Sharing
**Problem**: Cannot share TypeScript types between frontend and backend

**Example**:
```typescript
// Backend (Express route)
interface User {
  id: string
  email: string
  name: string
}

// Frontend cannot import this type
// Must duplicate or use API contract
```

**Mitigation Strategies**:

1. **OpenAPI/Swagger Schema**:
   ```bash
   # Generate TypeScript types from OpenAPI spec
   npx openapi-typescript backend/openapi.yaml -o frontend/types/api.ts
   ```

2. **Manual Type Synchronization**:
   ```typescript
   // frontend/types/api.ts (manually maintained)
   export interface User {
     id: string
     email: string
     name: string
   }
   ```

3. **Contract Testing**:
   ```typescript
   // Ensure frontend and backend agree on API shape
   test('GET /api/users returns correct shape', async () => {
     const response = await request(app).get('/api/users/1')
     expect(response.body).toMatchObject({
       id: expect.any(String),
       email: expect.any(String),
       name: expect.any(String),
     })
   })
   ```

#### 2. Duplicate Configuration
**Problem**: Some config files are duplicated

**Examples**:
- `.prettierrc` (frontend and backend)
- `eslint.config.mjs` (frontend and backend)
- `tsconfig.json` (frontend and backend)

**Mitigation**:
- Keep configurations simple and synchronized manually
- Use configuration templates
- Accept small duplication as trade-off for isolation

#### 3. Separate Dependency Updates
**Problem**: Must update dependencies separately

**Example**:
```bash
# Update TypeScript in both projects
cd frontend && npm update typescript
cd backend && npm update typescript
```

**Mitigation**:
- Use Renovate or Dependabot (can handle multiple package.json)
- Script to update both:
  ```bash
  #!/bin/bash
  cd frontend && npm update
  cd ../backend && npm update
  ```

---

## Alternatives Considered

### Alternative 1: Monorepo with Turborepo

**Structure**:
```
antarose-template-nodejs/
├── apps/
│   ├── web/              # Frontend
│   └── api/              # Backend
├── packages/
│   ├── types/            # Shared types
│   ├── utils/            # Shared utilities
│   └── config/           # Shared config
├── package.json
├── turbo.json
└── pnpm-workspace.yaml
```

**Pros**:
- ✅ Shared TypeScript types
- ✅ Shared utilities (validation, etc.)
- ✅ Single `pnpm install` for all packages
- ✅ Incremental builds (only build what changed)

**Cons**:
- ❌ Adds complexity (Turborepo, pnpm workspaces)
- ❌ Dependency conflicts possible
- ❌ Steeper learning curve
- ❌ More configuration (turbo.json, workspace config)
- ❌ Harder to debug workspace issues
- ❌ Overkill for minimal template

**Why Rejected**: **Too complex for a minimal template**. Monorepo tools add significant complexity and learning curve that doesn't justify the benefits for this simple use case.

---

### Alternative 2: Monorepo with pnpm Workspaces (No Turborepo)

**Structure**:
```
antarose-template-nodejs/
├── apps/
│   ├── frontend/
│   └── backend/
├── packages/
│   └── shared/           # Shared code
├── package.json
└── pnpm-workspace.yaml
```

**Pros**:
- ✅ Shared types
- ✅ Simpler than Turborepo
- ✅ pnpm is fast

**Cons**:
- ❌ Still requires pnpm (not everyone uses it)
- ❌ Workspace hoisting can cause issues
- ❌ Still adds configuration complexity
- ❌ No incremental builds (without Turborepo)

**Why Rejected**: Still adds unnecessary complexity. pnpm is great, but requiring it adds a barrier to entry for developers who use npm or yarn.

---

### Alternative 3: Single Next.js Project with API Routes

**Structure**:
```
antarose-template-nodejs/
├── app/
│   ├── api/              # API routes
│   └── ...
├── lib/
│   └── api/              # API logic
└── package.json
```

**Pros**:
- ✅ Simple single project
- ✅ Next.js handles everything
- ✅ Easy deployment (Vercel)

**Cons**:
- ❌ Cannot deploy API separately
- ❌ Cannot scale API independently
- ❌ Next.js API routes are serverless (cold starts)
- ❌ Not suitable for long-running APIs
- ❌ Tied to Next.js deployment platform

**Why Rejected**: Lack of flexibility. Many projects need a separate backend for:
- Long-running processes
- WebSocket servers
- Database migrations
- Background jobs
- Non-Vercel deployments

---

## Consequences

### Positive Consequences

1. **Clear Separation of Concerns**
   - Frontend and backend are completely independent
   - Easy to understand project boundaries
   - No confusion about what runs where

2. **Deployment Flexibility**
   - Deploy to different platforms optimized for each
   - Scale frontend and backend independently
   - Update one without affecting the other

3. **Team Independence**
   - Frontend and backend teams can work in parallel
   - Different release cycles
   - Faster iteration

4. **Simpler Setup**
   - Standard `npm install` (no special tools)
   - No workspace configuration
   - Works with any package manager (npm, yarn, pnpm)

5. **Easier Debugging**
   - No workspace magic to understand
   - Clear dependency tree
   - Standard Node.js resolution

### Negative Consequences

1. **No Type Sharing**
   - **Impact**: Must maintain types separately or use code generation
   - **Severity**: Medium
   - **Mitigation**: Use OpenAPI/Swagger for type generation

2. **Configuration Duplication**
   - **Impact**: `.prettierrc`, `eslint.config.mjs`, `tsconfig.json` duplicated
   - **Severity**: Low
   - **Mitigation**: Keep configs simple, synchronize manually

3. **Separate Updates**
   - **Impact**: Must update dependencies in both projects
   - **Severity**: Low
   - **Mitigation**: Use Renovate/Dependabot, or simple update script

4. **No Shared Utilities**
   - **Impact**: Cannot share validation logic, utilities
   - **Severity**: Low (minimal template has little shared code)
   - **Mitigation**: Publish shared packages to npm if needed

---

## Migration Path

If project grows and shared types become critical:

### Option 1: Publish Shared Package
```bash
# Create shared package
npm init -y @yourorg/shared-types

# Install in both projects
cd frontend && npm install @yourorg/shared-types
cd backend && npm install @yourorg/shared-types
```

### Option 2: Migrate to Monorepo
```bash
# Use automated migration tools
npx create-turbo@latest --migrate
```

**When to Migrate**:
- When shared code exceeds 1000 lines
- When type sync becomes painful
- When team has grown and can handle complexity

---

## Review Schedule

**Next Review**: When considering adding:
- Database layer (Prisma)
- Authentication (NextAuth.js)
- Shared validation schemas
- More than 3 services

**Decision Valid Until**: Project requires significant shared code or team grows beyond 10 developers.

---

## References

- [Turborepo Documentation](https://turbo.build/repo/docs)
- [pnpm Workspaces](https://pnpm.io/workspaces)
- [Monorepo vs Polyrepo](https://monorepo.tools/)
- [Next.js API Routes Limitations](https://nextjs.org/docs/pages/building-your-application/routing/api-routes)

---

**Status**: Accepted
**Last Updated**: 2025-10-24
**Author**: Leo (System Architect)
**Approved By**: CTO (Pending)
