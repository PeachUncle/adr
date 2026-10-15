# ADR-029: Independent App Deployment Architecture

## Status

Accepted and Implemented

## Context

The platform was initially structured as a pnpm monorepo with:

- Shared `pnpm-workspace.yaml` at root
- Shared `.npmrc` with `node-linker=hoisted` creating single `node_modules` at root
- Single `pnpm-lock.yaml` for all apps and services
- Shared packages referenced via `file:../../packages/*` protocol
- Build-time coupling where apps had `prebuild` scripts to build shared packages

This structure violated DDD principles for independent bounded contexts:

1. **Dependency Version Lock-in**: All apps forced to use same dependency versions
2. **Build Coupling**: Apps couldn't build without building shared dependencies first
3. **Deployment Dependencies**: Apps couldn't be deployed independently
4. **Version Conflicts**: Couldn't have `landing-page` on Next.js 14 while another app uses Next.js 16

Example of coupling:

```json
// apps/landing-page/package.json (OLD)
{
  "scripts": {
    "prebuild": "cd ../../packages/observability-edge && npm install && npm run build"
  },
  "dependencies": {
    "@platform/observability-edge": "file:../../packages/observability-edge"
  }
}
```

## Decision

**Restructure to truly independent applications following polyrepo principles within a monorepo structure.**

### Key Changes

#### 1. Remove Shared Workspace Configuration

- ❌ Delete root `pnpm-workspace.yaml`
- ❌ Delete root `.npmrc`
- ❌ Delete root `pnpm-lock.yaml`
- ✅ Each app manages its own pnpm configuration

#### 2. Per-App Dependency Management

- ✅ Each app has its own `.npmrc` (if needed for special requirements like OpenNext)
- ✅ Each app has its own `pnpm-lock.yaml` committed to git
- ✅ Each app has its own `node_modules` directory (gitignored)
- ✅ Apps install dependencies independently: `cd apps/landing-page && pnpm install`

#### 3. Eliminate Build-Time Coupling

- ❌ Remove `prebuild` scripts that reach into other directories
- ❌ Remove `file:../../packages/*` dependency references
- ✅ **Primary Strategy**: Publish shared packages to npm registry (GitHub Packages) with semantic versioning
- ✅ **Interim Solution**: Inline small shared code (< 1000 lines) until package publishing workflow is established

**Package Publishing Strategy**:

```json
// Future state - apps consume published packages
{
  "dependencies": {
    "@platform/observability": "^1.2.0",  // Published to GitHub Packages
    "@platform/shared-domain": "^2.0.1",  // Versioned dependency
    "next": "^16.0.1"
  }
}
```

**Rationale**:

- Semantic versioning enables independent evolution of packages and apps
- Published packages are immutable and auditable
- Apps can use different package versions without coordination
- Clear dependency graph and version management
- No build-time coupling between apps and packages

#### 4. Landing Page Implementation (Proof of Concept)

**Changes Made**:

```bash
# Structure
apps/landing-page/
├── .npmrc                           # NEW: App-specific pnpm config
├── pnpm-lock.yaml                   # NEW: App-specific lockfile
├── node_modules/                    # NEW: App-specific dependencies
├── package.json                     # MODIFIED: No file: references
└── src/
    └── lib/
        └── observability-edge/      # NEW: Inlined from packages/
            ├── index.ts
            └── types.ts
```

**package.json Changes**:

```json
{
  "scripts": {
    "dev": "next dev",
    // "prebuild": "..." REMOVED
    "build": "NODE_ENV=production next build",
    "build:cloudflare": "opennextjs-cloudflare build"
  },
  "dependencies": {
    // "@platform/observability-edge": "file:../../packages/observability-edge" REMOVED
    "next": "latest",  // Now resolves independently!
    "react": "latest",
    "react-dom": "latest",
    "zustand": "latest"
  }
}
```

**Import Changes**:

```typescript
// OLD:
import { createEdgeObservability } from '@platform/observability-edge'

// NEW:
import { createEdgeObservability } from './observability-edge/index'
```

### Benefits

**DDD Compliance**:

- ✅ Each app is a truly independent bounded context
- ✅ Apps can evolve dependency versions independently
- ✅ No build-time coupling between contexts
- ✅ Clear ownership and boundaries

**Deployment Independence**:

- ✅ `landing-page` can deploy on Next.js 14.2.18 while other apps use Next.js 16.0.1
- ✅ Each app builds and deploys without requiring other apps
- ✅ Dependency updates in one app don't force updates in others
- ✅ CI/CD pipelines are fully independent per app

**Development Velocity**:

- ✅ Developers can work on one app without impacting others
- ✅ Faster builds (only install dependencies for app being developed)
- ✅ Clearer dependency trees per app
- ✅ Easier to reason about what each app requires

### Drawbacks

**Initial Code Duplication (Temporary)**:

- ⚠️ Small shared code (observability-edge: 718 lines) temporarily inlined into apps during migration
- **Timeline**: Interim solution until package publishing workflow is established
- **Resolution**: Publish packages to GitHub Packages with semantic versioning (planned Phase 2)

**Package Publishing Setup Required**:

- ⚠️ Need to configure GitHub Packages registry and CI/CD publishing workflow
- **Mitigation**: One-time setup, automated thereafter
- **Scope**: ~4-8 hours to configure GitHub Actions for automated publishing

**Initial Migration Effort**:

- ⚠️ Each app needs migration from workspace to independent structure
- **Mitigation**: Incremental migration, starting with landing-page as proof-of-concept

## Alternatives Considered

### Alternative 1: pnpm Workspace with workspace:* Protocol

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
  - 'services/*'
```

```json
// Apps consume via workspace protocol
{
  "dependencies": {
    "@platform/observability": "workspace:*"
  }
}
```

**Decision: Rejected**

**Reasons**:

- ❌ Creates dependency version coupling - all apps must use same package versions
- ❌ Violates DDD principle of independent bounded contexts
- ❌ Apps cannot evolve package dependencies independently
- ❌ Deployment coordination required when packages change
- ❌ Defeats the purpose of microservices independence

**When it might be acceptable**:

- All apps deploy together as a unit (modular monolith)
- Team is very small (< 3 developers)
- Rapid prototyping phase

### Alternative 2: True Polyrepo (Separate Git Repos)

**Decision: Rejected**

**Reasons**:

- ❌ Loses benefits of unified tooling, CI/CD orchestration
- ❌ Harder to maintain shared deploy/ scripts and infrastructure code
- ❌ Documentation fragmentation
- ❌ Overhead of managing multiple repositories

**When it might be acceptable**:

- Apps owned by different teams/organizations
- Need strict access control per app
- Apps have completely different tech stacks

### Alternative 3: Nx/Turborepo Monorepo Tools

**Decision: Rejected**

**Reasons**:

- ❌ Adds significant tooling complexity
- ❌ Still couples dependency versions across apps
- ❌ Opinionated build system may conflict with OpenNext/Cloudflare requirements
- ❌ Learning curve for team

**When it might be acceptable**:

- Large monorepo (50+ apps)
- Need sophisticated caching and build orchestration
- Team already familiar with tools

## Package Publishing Strategy

### Overview

Shared TypeScript packages will be published to **GitHub Packages** using semantic versioning. Apps consume packages as versioned npm dependencies.

### Publishing Workflow

#### 1. Package Structure

```
packages/
├── observability/
│   ├── package.json          # "@platform/observability"
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts
│   │   └── types.ts
│   ├── dist/                 # Build output (gitignored)
│   └── README.md
```

#### 2. Package Configuration

```json
// packages/observability/package.json
{
  "name": "@platform/observability",
  "version": "1.0.0",
  "description": "Edge-compatible observability for Cloudflare Workers",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": ["dist", "README.md"],
  "publishConfig": {
    "registry": "https://npm.pkg.github.com",
    "access": "restricted"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/TomRiddelsdell/tomriddelsdell.com"
  },
  "scripts": {
    "build": "tsc",
    "test": "vitest",
    "prepublishOnly": "pnpm build && pnpm test"
  }
}
```

#### 3. GitHub Actions Publishing Workflow

```yaml
# .github/workflows/publish-packages.yml
name: Publish Packages

on:
  push:
    tags:
      - '@platform/*@*'  # e.g., @platform/observability@1.0.0

permissions:
  contents: read
  packages: write

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: pnpm/action-setup@v2
        with:
          version: 10
      
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          registry-url: 'https://npm.pkg.github.com'
          scope: '@platform'
      
      - name: Extract package info
        id: package
        run: |
          PACKAGE_NAME=$(echo ${{ github.ref_name }} | cut -d@ -f1,2)
          VERSION=$(echo ${{ github.ref_name }} | cut -d@ -f3)
          echo "name=$PACKAGE_NAME" >> $GITHUB_OUTPUT
          echo "version=$VERSION" >> $GITHUB_OUTPUT
      
      - name: Install dependencies
        run: cd packages/${PACKAGE_NAME#@platform/} && pnpm install
      
      - name: Build package
        run: cd packages/${PACKAGE_NAME#@platform/} && pnpm build
      
      - name: Publish to GitHub Packages
        run: cd packages/${PACKAGE_NAME#@platform/} && pnpm publish --no-git-checks
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### 4. App Consumption

```json
// apps/landing-page/.npmrc
@platform:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_PACKAGES_TOKEN}
```

```json
// apps/landing-page/package.json
{
  "dependencies": {
    "@platform/observability": "^1.0.0",  // Versioned dependency
    "next": "^16.0.1"
  }
}
```

#### 5. Local Development Setup

```bash
# Developers need GitHub PAT with read:packages permission
export GITHUB_PACKAGES_TOKEN=ghp_xxxxxxxxxxxxx

# Or configure globally
echo "//npm.pkg.github.com/:_authToken=${GITHUB_PACKAGES_TOKEN}" >> ~/.npmrc
```

### Versioning Guidelines

**Semantic Versioning (semver)**:

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes - incompatible API changes
- **MINOR** (1.0.0 → 1.1.0): New features - backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes - backward compatible

**Examples**:

```bash
# Bug fix
git tag @platform/observability@1.0.1
git push --tags

# New feature (backward compatible)
git tag @platform/observability@1.1.0
git push --tags

# Breaking change
git tag @platform/observability@2.0.0
git push --tags
```

### Package Development Workflow

```bash
# 1. Create/update package
cd packages/observability
# Edit src/index.ts

# 2. Build and test
pnpm build
pnpm test

# 3. Update version in package.json
# Manually or use: npm version patch|minor|major

# 4. Commit changes
git add .
git commit -m "feat(observability): add new trace method"

# 5. Create version tag
git tag @platform/observability@1.1.0

# 6. Push (triggers GitHub Actions publishing)
git push origin develop
git push --tags
```

### Managing Breaking Changes

When publishing breaking changes:

1. **Major version bump**: `2.0.0`
2. **Update CHANGELOG**: Document breaking changes
3. **Migration guide**: Provide upgrade instructions
4. **Coordinate with apps**: Notify app owners before releasing
5. **Deprecation period**: Mark old APIs as deprecated before removing

**Example Migration**:

```typescript
// v1.x.x (deprecated)
import { createObservability } from '@platform/observability'

// v2.0.0 (new API)
import { initObservability } from '@platform/observability'
```

### When to Inline vs. Publish

**Publish to GitHub Packages when**:

- ✅ Code used by 2+ apps
- ✅ Package is stable (infrequent changes)
- ✅ Need version control and immutability
- ✅ Want to share with external projects

**Inline code when**:

- ✅ Small code (< 500 lines)
- ✅ Rapid prototyping phase
- ✅ App-specific customizations
- ✅ Tightly coupled to single app

## Implementation Plan

### Phase 1: Landing Page Independence (✅ COMPLETED - November 10, 2025)

- [x] Remove root workspace configuration
- [x] Create `apps/landing-page/.npmrc`
- [x] Install landing-page dependencies independently
- [x] Inline observability-edge source code (temporary)
- [x] Update imports to use local paths
- [x] Verify build succeeds
- [x] Commit changes

**Status**: Landing page now fully independent with Next.js 16.0.1

### Phase 2: Package Publishing Infrastructure (PLANNED - Priority: HIGH)

**Objective**: Enable semantic versioning of shared packages via GitHub Packages

**Tasks**:

1. [ ] Configure GitHub Packages for @platform/* scope
   - Set up `.npmrc` with registry configuration
   - Configure authentication tokens
   - Document publishing workflow

2. [ ] Create Package Publishing Workflow

   ```yaml
   # .github/workflows/publish-packages.yml
   name: Publish Packages
   on:
     push:
       tags:
         - '@platform/*@*'  # e.g., @platform/observability@1.0.0
   ```

3. [ ] Establish Versioning Standards
   - Semantic versioning (MAJOR.MINOR.PATCH)
   - Changeset-based version management
   - Automated changelog generation

4. [ ] Publish Initial Packages
   - `@platform/observability-edge@1.0.0`
   - `@platform/shared-domain@1.0.0` (if exists)
   - `@platform/shared-infra@1.0.0` (if exists)

5. [ ] Update Package Consumption

   ```json
   // apps/landing-page/package.json
   {
     "dependencies": {
       "@platform/observability-edge": "^1.0.0"  // Published version
     }
   }
   ```

6. [ ] Remove Inlined Code
   - Delete `apps/landing-page/src/lib/observability-edge/`
   - Update imports to use npm package

**Timeline**: 4-8 hours  
**Dependencies**: GitHub Packages access (free for private repos)

### Phase 3: Other Apps Migration (Future Work)

For each app in `apps/`:

1. [ ] Create app-specific `.npmrc` (if needed)
2. [ ] Evaluate shared dependencies
   - Use published packages from Phase 2
   - Inline only app-specific code
3. [ ] Run `pnpm install` to create app-specific lockfile
4. [ ] Test build and deployment
5. [ ] Update CI/CD workflows if needed

### Phase 4: Services Migration (Future Work)

Same process for `services/` directory

- [x] Update imports to use local paths
- [x] Verify build succeeds
- [x] Commit changes

### Phase 2: Other Apps (Future Work)

For each app in `apps/`:

1. Create app-specific `.npmrc` (if needed)
2. Evaluate shared dependencies - inline or publish
3. Run `pnpm install` to create app-specific lockfile
4. Test build and deployment
5. Update CI/CD workflows if needed

### Phase 3: Services (Future Work)

Same process for `services/` directory

## Success Criteria

- [x] landing-page builds successfully with own dependencies
- [x] landing-page has own pnpm-lock.yaml
- [x] No file: references in package.json
- [x] No prebuild scripts crossing directory boundaries
- [ ] Other apps migrated to independent structure
- [ ] CI/CD pipelines verified working for each app

## Consequences

**Positive**:

- ✅ True microservices independence - apps are genuinely decoupled
- ✅ Semantic versioning of shared packages enables controlled evolution
- ✅ Apps can use different versions of shared packages without coordination
- ✅ Faster development iteration per app (no workspace coordination)
- ✅ Clear separation of concerns and ownership boundaries
- ✅ Easier to scale team (different teams own different apps and packages)
- ✅ Deployment flexibility and safety (independent release cycles)
- ✅ Published packages are immutable and auditable
- ✅ External projects can consume published packages

**Negative**:

- ⚠️ Temporary code duplication during migration (< 1000 lines, resolved in Phase 2)
- ⚠️ Package publishing infrastructure setup required (~4-8 hours one-time)
- ⚠️ Need to coordinate breaking changes in shared packages across consuming apps
- ⚠️ Migration effort for existing apps (incremental, app-by-app)

**Neutral**:

- 🔄 Shifts from "monorepo with shared deps" to "polyrepo-style monorepo with published packages"
- 🔄 Maintains benefits of unified repo (shared CI/CD, infrastructure, documentation)
- 🔄 Adds package versioning responsibility (but improves clarity)

## Related ADRs

- **ADR-015**: Deployment Strategy - Updated to reflect per-app independence
- **ADR-013**: Frontend Framework - Landing page now independently versioned
- **ADR-016**: Application Architecture Standards - Reinforces DDD boundaries

## Notes

**November 10, 2025**: Initial implementation completed for landing-page (Phase 1).

- Successfully removed workspace coupling
- Verified OpenNext Cloudflare build works with independent dependencies
- Next.js version: 16.0.1 (latest) vs. previous 14.2.18 (demonstrates version independence)
- Temporarily inlined observability-edge (718 lines) - will be replaced with published package in Phase 2

**Next Steps**:

- Phase 2: Set up GitHub Packages publishing workflow for @platform/* packages
- Publish `@platform/observability-edge@1.0.0`
- Update landing-page to consume published package
- Remove inlined code

**Package Publishing Registry**: GitHub Packages (free for private repos)

- Registry: `https://npm.pkg.github.com`
- Scope: `@platform`
- Authentication: GitHub Personal Access Token with `write:packages` permission

---

**Decision Date**: November 10, 2025  
**Implemented**: November 10, 2025 (Phase 1)  
**Publishing Strategy**: GitHub Packages with semantic versioning  
**Authors**: Platform Team  
**Reviewers**: Architecture Team
