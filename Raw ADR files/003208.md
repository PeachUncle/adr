# ADR-015: Choice of Monorepo Structure

## Date
2025-09-14

## Status
Decided & Implemented

## Context

The project has been successfully migrated to a clean monorepo structure with separate packages for frontend and backend services. This resolves previous architectural ambiguity and bundler resolution conflicts that existed in the original `vite-app/` structure.

The current structure:
```
/ (PlumbingPOC root)
├── packages/
│   ├── frontend/     # React/Vite application
│   │   ├── src/      # Frontend React code
│   │   ├── package.json
│   │   └── vite.config.js
│   └── backend/      # Node.js/Express API
│       ├── api/      # Backend Node.js code
│       └── package.json
├── package.json      # Root workspace config
└── node_modules/
```

The previous nested structure led to:
- Bundler ambiguity with React module resolution
- Complex dependency management
- Difficulty scaling to multiple services
- Unclear separation of concerns

## Decision

We will refactor to a clean monorepo structure with separate packages for frontend and backend services:

```
/ (PlumbingPOC root)
├── packages/
│   ├── frontend/     # React/Vite application
│   │   ├── src/      # React components and logic
│   │   ├── public/   # Static assets
│   │   ├── package.json
│   │   └── vite.config.js
│   └── backend/      # Node.js/Express API
│       ├── controllers/
│       ├── routes/
│       ├── services/
│       ├── middleware/
│       ├── package.json
│       └── server.js
├── package.json      # Root workspace config
└── node_modules/
```

### Migration Plan

1. **Create packages directory structure** ✅ COMPLETED
2. **Move frontend code**: `packages/frontend/src/` ✅ COMPLETED
3. **Move backend code**: `packages/backend/api/` ✅ COMPLETED
4. **Create package.json for each service** ✅ COMPLETED
5. **Update workspace configuration** ✅ COMPLETED
6. **Update build and dev scripts** ✅ COMPLETED
7. **Update import paths and configurations** ✅ COMPLETED
8. **Test and validate all functionality** ✅ COMPLETED

## Consequences

### Pros
- **Clean Architecture**: Clear separation between frontend and backend
- **Scalability**: Easy to add mobile apps, admin panels, or microservices
- **Dependency Isolation**: Each service manages its own dependencies
- **Build Optimization**: Independent build processes for each service
- **Developer Experience**: Clear mental model of service boundaries
- **CI/CD**: Independent deployment pipelines for each service

### Cons
- **Migration Complexity**: Significant refactoring required
- **Time Investment**: Multi-hour effort to restructure
- **Breaking Changes**: All relative import paths need updating
- **Configuration Complexity**: More package.json files to maintain

## Alternatives Considered

### Option 1: Keep Current Structure with resolve.alias
- **Pros**: Quick fix, minimal changes, industry standard for bundler ambiguity
- **Cons**: Doesn't address root architectural issues, still nested structure
- **Decision**: Not chosen - doesn't provide long-term architectural benefits

### Option 2: Micro-frontend Architecture
- **Pros**: Ultimate modularity, independent deployments
- **Cons**: Overkill for current project size, complex orchestration
- **Decision**: Not chosen - too heavy for current needs

## Implementation Notes

### Package Configuration

**packages/frontend/package.json**:
```json
{
  "name": "@plumbingpoc/frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  }
}
```

**packages/backend/package.json**:
```json
{
  "name": "@plumbingpoc/backend",
  "version": "1.0.0",
  "type": "module",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "node server.js"
  }
}
```

### Root package.json Updates
```json
{
  "workspaces": ["packages/*"],
  "scripts": {
    "dev": "npm-run-all --parallel dev:frontend dev:backend",
    "dev:frontend": "npm run dev --workspace=@plumbingpoc/frontend",
    "dev:backend": "npm run start --workspace=@plumbingpoc/backend"
  }
}
```

## Next Steps

✅ **All migration steps completed successfully:**

1. ✅ Create ADR-015 documentation (this file)
2. ✅ Plan detailed migration steps
3. ✅ Execute structural refactoring
4. ✅ Update all configurations
5. ✅ Test complete functionality
6. ✅ Update deployment scripts

**Migration Summary:**
- Frontend code moved from `vite-app/src/` to `packages/frontend/src/`
- Backend code moved from `vite-app/api/` to `packages/backend/api/`
- All configuration files updated (vitest.config.ts, netlify.toml, .gitignore)
- All import paths updated throughout the codebase
- All documentation updated to reflect new structure
- All tests updated with new import paths
- Build and deployment scripts updated
