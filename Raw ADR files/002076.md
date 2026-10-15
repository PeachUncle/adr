# ADR-001: Transition from CLI to Web-Based GUI

**Status**: Accepted
**Date**: 2025-12-08
**Decision Makers**: Project Team
**Phase**: Phase I → Phase II Transition

---

## Context and Problem Statement

Phase I of the Hackathon II project successfully delivered a console-based Todo application with in-memory storage and JSON persistence. To progress to Phase II, we must transition from a Command-Line Interface (CLI) to a Web-Based Graphical User Interface (GUI) while introducing multi-user support, persistent database storage, and authentication.

This represents a fundamental architectural shift that impacts:
- **User Experience**: CLI → Browser-based GUI
- **Deployment Model**: Local Python script → Distributed web application (Frontend + Backend)
- **Storage**: File-based JSON → PostgreSQL database
- **User Model**: Single-user → Multi-user with authentication
- **Technology Stack**: Python-only → Full-stack (Next.js + FastAPI)

## Decision

We will transition from the Phase I CLI application to a full-stack web application with the following architecture:

### Architecture Components

1. **Frontend**: Next.js 16+ (App Router)
   - Browser-based GUI with responsive design
   - TypeScript for type safety
   - Tailwind CSS for styling
   - Deployed on Vercel

2. **Backend**: FastAPI (Python)
   - RESTful API with JWT authentication
   - SQLModel ORM for database operations
   - Deployed on Hugging Face Spaces

3. **Database**: Neon Serverless PostgreSQL
   - Persistent, multi-user data storage
   - User isolation at database level

4. **Authentication**: Better Auth with JWT
   - Shared secret between frontend and backend
   - Stateless authentication

### Monorepo Structure
```
Hackathon II/
├── phase-1/       # Preserved CLI application
├── frontend/      # Next.js web application
├── backend/       # FastAPI REST API
└── specs/         # Centralized specifications
```

## Rationale

### Why Web-Based GUI?

| Factor | CLI (Phase I) | Web GUI (Phase II) | Justification |
|--------|---------------|-------------------|---------------|
| **Accessibility** | Terminal required | Any browser | Wider user reach |
| **User Experience** | Text-based | Visual, interactive | Better usability |
| **Multi-user Support** | Single user | Multiple concurrent users | Scalability requirement |
| **Deployment** | Local installation | Cloud-hosted | Easier distribution |
| **Mobile Support** | Not available | Responsive web design | Modern requirement |
| **Collaboration** | Not possible | Shared task lists (future) | Team productivity |

### Why Separate Frontend and Backend?

1. **Independent Deployment**
   - Frontend on Vercel (static/server-rendered)
   - Backend on Hugging Face (Python hosting)
   - Scale independently based on load

2. **Technology Specialization**
   - Next.js excels at modern web UIs
   - FastAPI excels at Python APIs
   - Use best tool for each job

3. **Package Manager Isolation**
   - Frontend: npm/pnpm/yarn
   - Backend: uv/pip
   - No conflicts or mixed dependencies

4. **Future-Ready**
   - Phase III: Add AI chatbot interface
   - Phase IV: Containerize separately
   - Phase V: Deploy as microservices

### Why Next.js 16+?

- **App Router**: Modern React architecture with server components
- **Performance**: Built-in optimizations (code splitting, image optimization)
- **DX**: Excellent developer experience with TypeScript support
- **Deployment**: First-class Vercel integration
- **SEO**: Server-side rendering capabilities

### Why FastAPI?

- **Performance**: High-performance async Python framework
- **Type Safety**: Pydantic models for request/response validation
- **Documentation**: Auto-generated OpenAPI/Swagger docs
- **Ecosystem**: Compatible with SQLModel, Alembic, pytest
- **Python Continuity**: Maintains Python from Phase I

### Why Separate Database (Neon PostgreSQL)?

- **Persistence**: True persistent storage (not file-based)
- **Concurrency**: Handle multiple users simultaneously
- **Reliability**: ACID guarantees, backups, replication
- **Scalability**: Scale storage independently
- **Serverless**: Pay-per-use, auto-scaling

## Alternatives Considered

### Alternative 1: Enhance CLI with TUI (Terminal User Interface)
- **Pros**: Maintain Python-only stack, simpler deployment
- **Cons**: Limited accessibility, no mobile support, niche audience
- **Rejected**: Doesn't meet hackathon requirements for web application

### Alternative 2: Monolithic Full-Stack (Next.js with Next.js API Routes)
- **Pros**: Single deployment, simpler architecture
- **Cons**: Limited Python reuse, harder to scale backend independently
- **Rejected**: Hackathon requires FastAPI backend

### Alternative 3: Server-Side Rendered (SSR) Python (Flask/Django)
- **Pros**: Python-only stack
- **Cons**: Inferior frontend DX compared to Next.js, harder to achieve modern UI/UX
- **Rejected**: Next.js offers superior frontend experience

### Alternative 4: SPA with Vanilla React
- **Pros**: Simpler than Next.js
- **Cons**: Missing Next.js features (SSR, routing, optimization), requires custom setup
- **Rejected**: Next.js provides better DX and performance

## Consequences

### Positive

✅ **Enhanced User Experience**: Modern, responsive web interface accessible from any device
✅ **Scalability**: Multi-user support with proper authentication and isolation
✅ **Deployment Flexibility**: Independent frontend and backend deployments
✅ **Technology Leadership**: Modern stack (Next.js, FastAPI, PostgreSQL)
✅ **Future-Ready**: Prepared for Phases III-V (AI chatbot, Kubernetes, cloud deployment)
✅ **Maintained Phase I**: CLI application preserved in `phase-1/` folder
✅ **Developer Experience**: TypeScript, hot reload, auto-generated API docs
✅ **Performance**: Server components, code splitting, edge deployment

### Negative

⚠️ **Increased Complexity**: Two separate applications vs. single CLI script
⚠️ **Deployment Dependencies**: Requires Vercel, Hugging Face, and Neon accounts
⚠️ **Learning Curve**: Team must learn Next.js and TypeScript if not familiar
⚠️ **Development Overhead**: Manage two codebases and environments
⚠️ **Network Dependency**: Requires internet for frontend-backend communication
⚠️ **Authentication Overhead**: JWT token management, shared secrets
⚠️ **CORS Configuration**: Cross-origin requests require proper setup

### Mitigation Strategies

| Risk | Mitigation |
|------|------------|
| **Complexity** | Monorepo structure with centralized specs; clear documentation |
| **Deployment** | Free tiers available; comprehensive deployment guides |
| **Learning Curve** | Detailed CLAUDE.md files for frontend and backend patterns |
| **Development Overhead** | Spec-driven development with Claude Code to accelerate |
| **Network Dependency** | Local development with localhost; graceful error handling |
| **Authentication** | Shared secret via environment variables; clear documentation |
| **CORS** | Explicit CORS middleware configuration in FastAPI |

## Implementation Plan

### Phase Transition Steps

1. **Monorepo Restructuring** ✅ (Completed)
   - Move Phase I to `phase-1/` folder
   - Create `frontend/` and `backend/` folders
   - Reorganize `specs/` with new structure
   - Update documentation (CLAUDE.md, README.md)

2. **Frontend Setup** (Next)
   - Initialize Next.js 16+ project
   - Setup TypeScript and Tailwind CSS
   - Configure Better Auth
   - Implement singleton API service

3. **Backend Setup** (Concurrent)
   - Initialize FastAPI project with uv
   - Define SQLModel database models
   - Implement JWT middleware
   - Create RESTful API endpoints

4. **Database Setup** (Concurrent)
   - Create Neon PostgreSQL database
   - Define schema (users, tasks tables)
   - Setup connection pooling

5. **Integration** (After both ready)
   - Connect frontend to backend API
   - Test authentication flow
   - Verify user isolation
   - End-to-end testing

6. **Deployment** (Final)
   - Deploy frontend to Vercel
   - Deploy backend to Hugging Face
   - Configure environment variables
   - Test production deployment

## Technical Specifications

### API Communication Pattern

**Singleton API Service** (Frontend)
```
constants/endpoints.ts  → All API endpoint URLs
services/api.ts        → HTTP client with axios (GET, POST, PUT, DELETE)
```

**RESTful API** (Backend)
```
All routes under /api/ prefix
JWT authentication required for all endpoints
User isolation enforced at database query level
```

### Authentication Flow

1. User signs in via Better Auth (frontend)
2. Frontend receives JWT token
3. Frontend stores token (localStorage/cookie)
4. All API requests include `Authorization: Bearer <token>` header
5. Backend verifies token with shared secret
6. Backend extracts user_id from token
7. Backend filters all queries by user_id

### Data Model Evolution

**Phase I**: In-memory list with JSON file backup
**Phase II**: PostgreSQL with tables:
- `users` table (Better Auth managed)
- `tasks` table (user_id foreign key)

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Functionality** | All 5 Basic Level features working | Manual testing |
| **Authentication** | User isolation working | Security audit |
| **Performance** | < 200ms API response time | Load testing |
| **Deployment** | Both services deployed and accessible | Smoke testing |
| **Phase I Preservation** | CLI app still functional | Regression testing |
| **Documentation** | Complete specs and guides | Review checklist |

## Related Documents

- [Project Constitution](../../.specify/memory/constitution.md)
- [Phase II Requirements](../../Hackathon%20II%20-%20Todo%20Spec-Driven%20Development.md#phase-ii-todo-full-stack-web-application)
- [System Architecture](../../specs/architecture.md)
- [Project Overview](../../specs/overview.md)

## Decision History

- **2025-12-08**: ADR created and accepted
- **2025-12-08**: Monorepo structure implemented
- **2025-12-08**: Phase I preserved and verified working

## Notes

- Phase I CLI application remains fully functional in `phase-1/` folder
- Monorepo allows both CLI and web versions to coexist
- Future phases (III-V) will build upon Phase II architecture
- Spec-driven development approach maintained throughout transition

---

**ADR Status**: ✅ Accepted and Implemented (Monorepo Restructuring)
**Next ADR**: Authentication strategy details (JWT vs. session-based)
**Version**: 1.0.0
