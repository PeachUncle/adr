# ADR-0001: Monorepo Architecture with Separate Frontend and Backend

**Date**: 2025-12-12
**Status**: Accepted
**Context**: 001-ai-native-textbook-platform
**Decision Makers**: Architecting Agent, Super Orchestrator

## Context

The AI-Native Textbook Platform requires both a content delivery frontend (Docusaurus) and an intelligent backend API (FastAPI) for RAG, personalization, and translation features. We needed to decide on the repository structure and deployment strategy.

## Decision

We will use a **monorepo structure** with independent frontend and backend applications:

```
apps/
├── docs/     # Docusaurus v3 (TypeScript/React)
└── api/      # FastAPI (Python 3.12+)
```

**Key Principles**:
1. **Physical Separation**: Frontend and backend are completely separate codebases
2. **Independent Deployment**: Each app can be deployed independently to Vercel
3. **No Cross-Runtime Imports**: TypeScript cannot import Python, and vice versa
4. **API-First Communication**: Frontend communicates with backend via REST API only

## Rationale

### Options Considered

**Option 1: Monorepo (Selected)**
- ✅ Single repository for all code
- ✅ Unified version control and CI/CD
- ✅ Easy to manage related changes across frontend/backend
- ✅ Constitutional requirement (Article IV: clean separation)
- ❌ Slightly more complex deployment configuration

**Option 2: Multi-Repo**
- ✅ Complete isolation
- ✅ Independent release cycles
- ❌ Harder to coordinate changes
- ❌ More complex CI/CD
- ❌ Violates hackathon submission requirement (single repo)

**Option 3: Backend-in-Frontend (Next.js API Routes)**
- ✅ Single deployment
- ❌ Violates Constitution Article IV (no cross-runtime imports)
- ❌ FastAPI cannot run inside Next.js
- ❌ Poor separation of concerns

### Why Monorepo Won

1. **Hackathon Requirement**: Single GitHub repository required for submission
2. **Constitutional Compliance**: Article IV mandates clean separation with independent deployment
3. **Developer Experience**: Easier to work on related features across frontend and backend
4. **CI/CD Simplicity**: Single GitHub Actions workflow tests and deploys both apps
5. **Vercel Support**: Vercel supports monorepo deployments natively

## Consequences

### Positive

- Single source of truth for all code
- Unified issue tracking and pull requests
- Coordinated releases possible
- Simplified local development (both apps in one clone)

### Negative

- Vercel deployment configuration more complex (requires proper routing in `vercel.json`)
- Need to maintain clear boundaries between apps
- Risk of accidental tight coupling (mitigated by API-only communication)

### Neutral

- Need explicit CORS configuration
- Environment variables managed separately per app
- Build processes independent (npm for docs, pip for api)

## Implementation Details

### Repository Structure

```
/
├── apps/
│   ├── docs/          # Frontend (Docusaurus)
│   │   ├── src/
│   │   ├── docs/
│   │   ├── package.json
│   │   └── docusaurus.config.ts
│   └── api/           # Backend (FastAPI)
│       ├── src/
│       ├── tests/
│       ├── requirements.txt
│       └── migrations/
├── .specify/          # Spec-Kit Plus artifacts
├── history/           # PHRs and ADRs
├── vercel.json        # Monorepo deployment config
└── .github/workflows/ # CI/CD
```

### Deployment Strategy

- **Frontend**: Vercel static build from `apps/docs/build/`
- **Backend**: Vercel Python serverless functions from `apps/api/src/main.py`
- **Routing**: `/api/*` → backend, `/*` → frontend (configured in `vercel.json`)

### Communication Pattern

```
User Browser → Frontend (Docusaurus) → API Calls → Backend (FastAPI) → Database/Qdrant
```

## Compliance

- ✅ **Constitution Article IV**: Clean separation, independent deployment
- ✅ **Hackathon Rules**: Single repository requirement met
- ✅ **Plan Section 2.1**: Matches planned project structure exactly

## Alternatives Rejected

- ❌ Next.js with API routes (violates Python requirement)
- ❌ Separate repositories (violates hackathon rules)
- ❌ Backend embedded in frontend (violates Constitution)

## Related Decisions

- ADR-0002: FastAPI + Qdrant + Neon for Backend Stack
- ADR-0003: Vercel for Hosting Both Apps

## References

- Constitution Article IV: Engineering Standards
- Plan Section: Project Structure
- Vercel Monorepo Documentation

---

**Status**: ✅ **ACTIVE** - Currently implemented as described
