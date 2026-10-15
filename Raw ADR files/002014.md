# ADR-002: Mono-Repo Structure and Dependency Management

**Date:** 2025-11-15  
**Status:** Accepted  
**Accepted Date:** 2025-11-15  
**Deciders:** Agent Frontend, Agent Backend, Agent Blockchain  
**Technical Story:** Phase 0.1 - Repository Architecture  
**Supersedes:** None  
**Relates to:** ADR-001 (Tech Stack)

---

## Context and Problem Statement

Ghost Protocol requires a code organization strategy that supports:
- Multiple frontend applications (web, admin)
- Multiple backend services (API gateway, indexer, RPC orchestrator, AI engine)
- Blockchain components (chain node, CLI tools)
- Smart contracts (multiple contracts)
- Shared tooling and infrastructure code

**Question:** Should we use a mono-repo or poly-repo structure? If mono-repo, what package structure and dependency management strategy?

## Decision Drivers

- **Code Sharing:** Enable sharing types, utilities, components across packages
- **Atomic Changes:** Single PR can update frontend + backend + contracts
- **Consistent Versioning:** All packages version together
- **Build Efficiency:** Only rebuild changed packages
- **Developer Experience:** Single clone, unified CI/CD
- **Dependency Hell:** Avoid version conflicts across packages
- **Scalability:** Support 10+ packages without build slowdown

## Considered Options

1. **Mono-repo with pnpm workspaces**
2. **Mono-repo with npm workspaces**
3. **Mono-repo with Turborepo**
4. **Mono-repo with Lerna**
5. **Poly-repo (separate repositories)**

## Decision Outcome

**Chosen option:** "Mono-repo with pnpm workspaces", because:
- pnpm supports true per-package isolation (strict dependencies)
- Fastest package manager (symlinks, hard links, content-addressable store)
- Best disk space efficiency (shared dependencies across projects)
- Supports per-workspace lockfiles (pnpm-lock.yaml per package)
- Can enforce "no root dependencies" with proper configuration
- Aligns with CRITICAL RULE: **NEVER INSTALL DEPENDENCIES IN ROOT**

**Why not npm:** npm workspaces create a single root package-lock.json and do NOT support per-package lockfiles or `nohoist`, making true package isolation impossible.

### Repository Structure

```
ghost-protocol/
├── packages/
│   ├── backend/
│   │   ├── api-gateway/          # package.json, node_modules
│   │   ├── indexer/              # package.json, node_modules
│   │   ├── rpc-orchestrator/     # package.json, node_modules
│   │   └── ai-engine/            # package.json, node_modules
│   ├── chain/
│   │   ├── node-core/            # Cargo.toml, target/
│   │   └── chain-cli/            # Cargo.toml, target/
│   ├── contracts/
│   │   ├── chaing-token/         # package.json, node_modules
│   │   └── marketplace/          # package.json, node_modules
│   ├── frontend/
│   │   ├── web/                  # package.json, node_modules
│   │   ├── admin/                # package.json, node_modules
│   │   └── components/           # package.json, node_modules
│   └── tooling/
│       ├── scripts/
│       └── devcontainers/
├── infra/
│   ├── terraform/
│   ├── k8s/
│   └── runbooks/
├── docs/
│   ├── adr/
│   ├── templates/
│   └── ...
├── package.json                   # ⚠️ WORKSPACE DEFINITION ONLY
├── .gitignore
└── README.md
```

### Root package.json (Workspace Definition ONLY)

```json
{
  "name": "ghost-protocol-workspace",
  "version": "1.0.0",
  "private": true,
  "packageManager": "pnpm@8.15.0",
  "scripts": {
    "dev:web": "pnpm --filter web dev",
    "dev:api": "pnpm --filter api-gateway dev",
    "build:all": "pnpm -r build",
    "test:all": "pnpm -r test"
  }
}
```

### pnpm-workspace.yaml

```yaml
packages:
  - 'packages/frontend/*'
  - 'packages/backend/*'
  - 'packages/contracts/*'
```

### .npmrc (pnpm configuration)

```ini
# Enforce strict isolation
shamefully-hoist=false
strict-peer-dependencies=true

# Per-workspace lockfiles (each package has pnpm-lock.yaml)
shared-workspace-lockfile=false

# Prevent accidental root installs
ignore-workspace-root-check=false
```

**CRITICAL: NO `dependencies` or `devDependencies` allowed in root package.json!**

### Dependency Management Rules

#### Rule 1: NEVER INSTALL DEPENDENCIES IN ROOT

**FORBIDDEN:**
```bash
❌ pnpm install react          # At root (without -w flag)
❌ pnpm add -D typescript      # At root
❌ Root package.json with "dependencies": {...}
```

**REQUIRED:**
```bash
✅ cd packages/frontend/web && pnpm install react
✅ pnpm --filter api-gateway add @nestjs/core
✅ Each package has its own package.json, pnpm-lock.yaml, node_modules/
```

**Enforcement:**
- `.npmrc` with `ignore-workspace-root-check=false` prevents accidental root installs
- CI checks: Fail build if root has dependencies field
- Pre-commit hook: Warn if root package.json has dependencies/devDependencies
- Documentation: CRITICAL RULE prominently displayed in agent-rules.md

#### Rule 2: Per-Package Lockfiles

**pnpm configuration (.npmrc):**
```ini
shared-workspace-lockfile=false
```

Each workspace maintains its own lockfile:
```
packages/frontend/web/pnpm-lock.yaml
packages/backend/api-gateway/pnpm-lock.yaml
packages/contracts/chaing-token/pnpm-lock.yaml
```

**Why:** Prevents version conflicts, allows true per-package dependency isolation.

#### Rule 3: Strict Peer Dependencies

**pnpm configuration (.npmrc):**
```ini
strict-peer-dependencies=true
```

**Why:** Ensures all peer dependencies are explicitly declared (no phantom deps).

#### Rule 4: Disabled Hoisting for Package Isolation

**pnpm configuration (.npmrc):**
```ini
shamefully-hoist=false
```

**Why:**
- Avoids phantom dependencies (packages cannot access deps not in their package.json)
- Makes each package truly standalone
- Easier to extract package to separate repo later
- Enforces explicit dependency declarations

#### Rule 4: Version Alignment (Optional)

For critical shared dependencies (React, TypeScript), document recommended versions:

```json
// packages/frontend/web/package.json
{
  "dependencies": {
    "react": "18.x",           // Aligned with admin, components
    "next": "14.x"
  }
}
```

**Enforcement:** Manual review during PR, no automatic enforcement initially.

### Positive Consequences

- **Atomic Changes:** One PR updates all related packages
- **Code Sharing:** Types, utilities shared via workspace references
- **Unified CI/CD:** Single pipeline tests all packages
- **Consistent Tooling:** ESLint, Prettier configs shared
- **Developer Experience:** Single `git clone`, easier onboarding
- **Dependency Isolation:** Each package's dependencies isolated
- **No Phantom Deps:** Explicit dependencies in each package.json

### Negative Consequences

- **Build Time:** Initially slower (rebuilds all packages)
  - **Mitigation:** Add Turborepo later for caching
- **Repository Size:** Larger repo (all code in one place)
  - **Mitigation:** Use Git LFS for large assets
- **CI Complexity:** Need to detect changed packages
  - **Mitigation:** Use GitHub Actions matrix for parallel builds
- **Dependency Conflicts:** Need to manage version alignment
  - **Mitigation:** Document recommended versions, use Dependabot

## Pros and Cons of the Options

### Mono-repo with pnpm workspaces ✅ CHOSEN

**Pros:**
- Fastest package manager (symlinks, hard links, content-addressable)
- Best disk space efficiency (shared node_modules across projects)
- **TRUE per-workspace lockfiles** (pnpm-lock.yaml per package)
- **Strict dependency isolation** (shamefully-hoist=false)
- Built-in workspace protocol (workspace:* versions)
- Prevents phantom dependencies
- Better monorepo support than npm

**Cons:**
- Requires pnpm installation (one-time: `npm install -g pnpm`)
- Team needs to learn pnpm commands (very similar to npm)
- Slightly less common than npm (but widely adopted in modern monorepos)

**Why chosen:** Only tool that can enforce "no root dependencies" rule with per-package isolation.

---

### Mono-repo with npm workspaces ❌ REJECTED

**Pros:**
- Native to Node.js 20+ (no extra tool)
- Team already knows npm
- Widely supported by tools
- Simpler mental model

**Cons:**
- **CRITICAL:** Single root package-lock.json (cannot have per-package lockfiles)
- **CRITICAL:** No `nohoist` support (cannot disable hoisting)
- **CRITICAL:** Cannot run `npm ci` in individual workspaces
- Slower than pnpm
- Less efficient disk usage
- Phantom dependency risk (packages can access hoisted deps not in their package.json)

**Why rejected:** Cannot enforce "no root dependencies" rule - npm workspaces fundamentally incompatible with isolated package requirements.

---

### Mono-repo with Turborepo

**Pros:**
- Best build caching (remote cache)
- Parallel builds (max CPU utilization)
- Dependency graph analysis
- Incremental builds (only changed packages)

**Cons:**
- Extra tool to learn
- Adds complexity
- Requires configuration
- May be overkill initially

**Decision:** Start with npm workspaces, add Turborepo in Phase 1+ when build times become issue.

---

### Mono-repo with Lerna

**Pros:**
- Mature tool (used by Babel, Jest)
- Good versioning support
- Independent package versioning

**Cons:**
- Maintenance has slowed
- Turborepo is more modern
- Overkill for our use case

**Why not:** Turborepo is better modern alternative, npm workspaces simpler for start.

---

### Poly-repo (Separate Repositories)

**Pros:**
- Smaller repos (faster clone)
- Independent deployment
- Clear boundaries
- Easier access control

**Cons:**
- Cross-repo changes require multiple PRs
- Harder to share code (need to publish packages)
- Version synchronization complex
- Dependency hell (each repo manages deps)
- Slower developer iteration

**Why not:** Cross-cutting changes (frontend + backend + contracts) would require 3 PRs + coordination overhead.

---

## Links

- [npm workspaces documentation](https://docs.npmjs.com/cli/v10/using-npm/workspaces)
- [Turborepo documentation](https://turbo.build/repo/docs)
- [Monorepo best practices](https://monorepo.tools/)

## Notes

### Future Migration Path

**Phase 0-1:** npm workspaces (simple, no extra tools)

**Phase 2+ (if needed):** Migrate to Turborepo
- Add `turbo.json` configuration
- Define build pipeline
- Enable remote caching (CI speed boost)
- Keep npm workspaces for dependency management

**Indicators to migrate:**
- Build time >10 minutes
- >15 packages
- Frequent cross-package changes

### CI/CD Strategy

**GitHub Actions Workflow:**
```yaml
jobs:
  detect-changes:
    # Detect which packages changed
    outputs:
      packages: ${{ steps.changes.outputs.packages }}
    
  build-test:
    needs: detect-changes
    strategy:
      matrix:
        package: ${{ fromJSON(needs.detect-changes.outputs.packages) }}
    steps:
      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8.15.0
      
      - name: Install
        run: cd packages/${{ matrix.package }} && pnpm install --frozen-lockfile
      
      - name: Test
        run: cd packages/${{ matrix.package }} && pnpm test
      
      - name: Build
        run: cd packages/${{ matrix.package }} && pnpm build
```

**Benefits:**
- Only build changed packages
- Parallel builds (matrix strategy)
- Fail fast (independent jobs)

### Shared Code Strategy

**Types Sharing (Backend → Frontend):**
```typescript
// packages/backend/api-gateway/src/types/user.ts
export interface User {
  id: string;
  walletAddress: string;
}

// Generate OpenAPI spec
// packages/frontend/web generates types from spec
```

**Component Sharing (Frontend):**
```typescript
// packages/frontend/components/src/Button.tsx
export const Button = ({ ... }) => { ... }

// packages/frontend/web/package.json
{
  "dependencies": {
    "@ghost/components": "workspace:*"  // pnpm workspace protocol
  }
}

// Install with:
// cd packages/frontend/web
// pnpm add @ghost/components --workspace
```

### Dependency Update Strategy

**Weekly:**
- Review Dependabot PRs
- Test in staging before merging
- Update one package at a time

**Monthly:**
- Align major version updates across packages
- Test all packages together
- Update documentation

**Security:**
- Snyk alerts: Immediate fix
- Critical vulnerabilities: Hotfix same day
- High vulnerabilities: Fix within 7 days

---

**Review Date:** 2025-12-15  
**Next Review:** After adding 10+ packages or if build time >10min
