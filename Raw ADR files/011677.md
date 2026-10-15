# ADR-001: Unified Repository Structure

## Status
Accepted

## Date
2025-08-01

## Context

Minerva originally started as two separate repositories:
- `minerva-backend`: Django API server with Django Ninja
- `minerva-frontend`: Next.js React application with Chakra UI

This separation created several challenges:
- **Coordination Overhead**: Changes spanning frontend and backend required coordination across repositories
- **Development Complexity**: Developers needed to clone and manage two repositories
- **CI/CD Duplication**: Separate pipelines with potential inconsistencies
- **Version Synchronization**: Difficult to maintain compatibility between frontend and backend versions
- **Documentation Fragmentation**: Development guides scattered across repositories

## Decision

Merge both repositories into a single unified repository with the following structure:

```
minerva/
├── backend/          # Django backend (from minerva-backend/src)
├── frontend/         # Next.js frontend (from minerva-frontend/src)  
├── docs/             # Unified documentation
├── package.json      # Root workspace management
├── CLAUDE.md         # Comprehensive development guide
└── README.md         # Project overview
```

## Consequences

### Positive
- **Atomic Commits**: Full-stack changes can be committed together, ensuring consistency
- **Simplified Development**: Single `git clone` and `npm run dev` to start development
- **Unified CI/CD**: Single pipeline for coordinated testing and deployment
- **Better Documentation**: Centralized documentation and development guides
- **Easier Onboarding**: New developers have one repository to understand
- **Coordinated Releases**: Frontend and backend versions stay synchronized
- **Workspace Management**: npm workspaces allow dependency management across projects

### Negative
- **Larger Repository**: Increased clone time and repository size
- **Mixed Languages**: Single repository contains both Python and TypeScript code
- **Build Complexity**: Need to manage both Django and Next.js build processes
- **Permission Granularity**: Cannot grant different access levels to frontend vs backend

### Neutral
- **Git History**: Previous commit history preserved through migration process
- **Deployment Options**: Can still deploy frontend and backend independently if needed
- **Development Tools**: Most IDEs handle multi-language repositories well

## Alternatives Considered

### Option 1: Keep Separate Repositories
**Description**: Maintain the current two-repository structure

**Pros**:
- Clear separation of concerns
- Language-specific tooling
- Independent deployment cycles
- Granular access control

**Cons**:
- Coordination overhead for cross-stack changes
- Complex version synchronization
- Duplicate CI/CD setup
- Developer workflow complexity

**Why Rejected**: The coordination overhead outweighed the benefits of separation for a tightly-coupled full-stack application.

### Option 2: Monorepo with Separate Workspaces
**Description**: Use tools like Nx, Lerna, or Rush for advanced monorepo management

**Pros**:
- Advanced workspace management
- Sophisticated build caching
- Dependency graph analysis
- Granular change detection

**Cons**:
- Additional tooling complexity
- Learning curve for team
- Overkill for current project size
- Additional maintenance overhead

**Why Rejected**: The project is not complex enough to justify the additional tooling overhead. Simple npm workspaces provide sufficient workspace management.

### Option 3: Git Submodules
**Description**: Keep repositories separate but link them with git submodules

**Pros**:
- Maintains repository independence
- Allows coordinated development
- Preserves separate deployment

**Cons**:
- Git submodule complexity and common pitfalls
- Still requires coordination for changes
- Additional mental overhead for developers
- Deployment complexity

**Why Rejected**: Git submodules add complexity without solving the core coordination issues.

## Implementation Notes

### Migration Steps Completed
1. ✅ Removed `.git` directories from both sub-repositories
2. ✅ Created unified directory structure (`backend/`, `frontend/`)
3. ✅ Moved all source code to new locations
4. ✅ Updated configuration files for new paths
5. ✅ Created root-level `package.json` with workspace management
6. ✅ Added `concurrently` for parallel development server execution
7. ✅ Updated documentation and created unified `CLAUDE.md`
8. ✅ Created comprehensive `.gitignore` for both technologies
9. ✅ Initialized new git repository and made initial commit

### Configuration Changes
- **Backend**: Updated `rav.yaml` to remove `src/` directory references
- **Frontend**: No path changes needed within the frontend directory
- **Root**: Added npm scripts for unified development workflow
- **Documentation**: Consolidated separate CLAUDE.md files into comprehensive guide

### New Development Commands
```bash
npm run dev                    # Start both frontend and backend
npm run dev:frontend          # Start only frontend
npm run dev:backend           # Start only backend
npm run install:all           # Install all dependencies
npm run backend:migrate       # Database migrations
npm run backend:makemigrations # Create migrations
```

## References

- [Monorepo Best Practices](https://monorepo.tools/)
- [npm Workspaces Documentation](https://docs.npmjs.com/cli/v7/using-npm/workspaces)
- [Git Repository Migration Strategies](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)
- Original migration discussion and planning documents in `docs/updates/docker-unified-implementation.md`