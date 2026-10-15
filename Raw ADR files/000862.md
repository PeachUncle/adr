# ADR-001: Monorepo & Tooling Setup

**Date:** 2025-10-17  
**Status:** Accepted  
**Deciders:** Development Team  

## Context

Implementing T-001: Monorepo & Tooling to establish the foundation for the Basketball AI Ecosystem project with proper development workflows, linting, and build processes.

## Decision

### Package Management
- **pnpm** with workspace support for monorepo management
- Workspace configuration in `pnpm-workspace.yaml`
- Root package.json with cross-workspace scripts

### Project Structure
```
/
├── src/                 # React Native/Expo mobile app
├── backend/             # Fastify API service
├── packages/            # Shared packages (future)
├── docs/adr/            # Architecture Decision Records
├── .github/workflows/   # CI/CD pipelines
└── tools/               # Development tools
```

### Development Scripts
- `make dev` - Start both backend and mobile app
- `make test` - Run all tests
- `make lint` - Lint all packages
- `make build` - Build all packages

### Code Quality
- **ESLint** with TypeScript support
- **Prettier** for code formatting
- **Husky** + **lint-staged** for pre-commit hooks
- **TypeScript** strict mode across all packages

### CI/CD
- GitHub Actions workflow for PR validation
- Automated linting, type checking, testing, and building
- Staging deployment pipeline ready

## Implementation Details

### Backend
- **Fastify** web framework
- **TypeScript** with strict configuration
- **Prisma** ORM for database operations
- **Swagger/OpenAPI** documentation
- **Jest** for testing

### Mobile App
- **Expo** managed workflow
- **React Native** 0.72
- **Expo Router** for navigation
- **TypeScript** strict mode
- EAS build configuration

### Shared Configuration
- Consistent ESLint and Prettier rules
- TypeScript project references
- Unified development commands

## Acceptance Criteria Verification

✅ **CI runs lint/build/test on PR**: GitHub Actions workflow configured  
✅ **make dev runs app + backend locally**: Makefile and scripts implemented  
✅ **Pre-commit hooks configured**: Husky and lint-staged setup  
✅ **Workspace packages properly linked**: pnpm workspace configuration  

## How I Verified

**Commands:**
```bash
pnpm install                    # ✅ All dependencies installed
pnpm --filter backend dev       # ✅ Backend starts on port 3000
curl http://localhost:3000/healthz  # ✅ Returns {"status":"ok","timestamp":"..."}
make lint                       # ✅ Linting passes
make type-check                 # ✅ Type checking passes
```

**Files Created:**
- Root package.json with workspace scripts
- pnpm-workspace.yaml configuration
- Makefile with development commands
- .eslintrc.js and .prettierrc configuration
- GitHub Actions CI workflow
- Backend package with Fastify setup
- Mobile app package with Expo configuration
- TypeScript configurations for all packages

## Next Steps

Continue with T-002: Backend Health & OpenAPI - enhance health endpoint with request-id middleware and comprehensive OpenAPI documentation.
