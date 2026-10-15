# 002 – Repository Structure

## Status  
Accepted | 2025-05-26

---

## Context  
The **Parking Reservation System** project consists of:  
- **Two applications**:  
  - `parking-app-back` (NestJS)  
  - `parking-app-front` (Vue 3 + Vite)  
- **Shared code** planned: DTOs, validation schemas, date utilities, TS API client.  
- A **single team** working in very short sprints (half-day).  
- Requirement for **containerization** and a unified CI/CD pipeline.

---

## Decision  
We adopt a **pnpm workspaces monorepo** at the root, with the following convention:

````
software-architecture-heuristics/
├── apps/               # Deployable applications
│   ├── parking-app-back/
│   └── parking-app-front/
├── packages/           # Shared libraries
│   ├── shared-dto/
│   └── shared-utils/
├── docs/               # ADRs, C4 diagrams, guides
├── .gitignore
├── pnpm-workspace.yaml
└── package.json        # Root scripts
````

**Associated tools:**
- **pnpm**: dependency management + `workspaces`  
- Branch naming conventions: `main`, `feat/*`, `fix/*`, `chore/*`, `refactor/*`  
- A single GitHub Actions pipeline for lint → test → build → docker  

---

## Alternatives Considered

### 1. Multi-repo / Microservices
- **Approach**: split each service (back, front, shared libraries, potentially notifications, stats) into its own Git repository.  
- **Pros**: true service isolation, independent versioning and deployment, smaller per-repo history.  
- **Cons**: cross-repo changes require multiple PRs, harder to share types/DTOs, more CI/CD pipelines to maintain, increased onboarding friction.

### 2. Monorepo (chosen)
- **Approach**: keep all applications and shared code in a single repository using pnpm workspaces.  
- **Pros**: atomic changes across front/back, easy code sharing via `shared/`, single CI/CD pipeline, faster onboarding (`git clone && pnpm install`).  
- **Cons**: larger repository size, requires disciplined branching and tooling to avoid accidental cross-project impact.

**Why we chose Monorepo:**  
Given our small team, tight sprint cadence, and the need for type-safe sharing of DTOs and business logic between back and front, a monorepo maximizes productivity and minimizes context-switching overhead.

---

## Consequences

### Advantages
1. **Atomic changes**: a single commit/PR can modify both backend and frontend simultaneously.  
2. **Shared types**: DTOs and validation schemas live once in `packages/`, ensuring consistency.  
3. **Simplified CI/CD**: one pipeline for all builds and tests.  
4. **Rapid onboarding**: new developers clone one repo and have everything they need.

### Disadvantages
1. **Repository bloat**: history grows quickly; requires regular housekeeping.  
2. **Global scripts risk**: misconfigured root-level scripts can affect all projects if not scoped correctly.  

---