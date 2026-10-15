# ADR-002: Use Monorepo Structure

## Status
Accepted

## Date
2025-12-19

## Context

We need to decide on the project structure for Smart Health Synchronizer, which consists of three main components:
1. Backend (Django REST API)
2. Frontend (React application)
3. AI Service (FastAPI ML service)

### Options Considered

**Option 1: Separate Repositories (Polyrepo)**
- Each component in its own repository
- Independent versioning
- Separate CI/CD pipelines

**Option 2: Monorepo**
- All components in a single repository
- Shared tooling and configuration
- Unified version control

**Option 3: Hybrid**
- Core backend and frontend in one repo
- AI service separate

## Decision

We will use a **Monorepo structure** with all three components (backend, frontend, ai-service) in a single repository.

### Structure
```
smart-health-sync/
├── backend/          # Django REST API
├── frontend/         # React application
├── ai-service/       # FastAPI ML service
├── docs/            # Shared documentation
├── README.md
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## Rationale

### Why Monorepo?

1. **Simplified Development Workflow**
   - Single clone/setup for entire project
   - Easier for new developers
   - No need to sync multiple repos

2. **Atomic Changes**
   - Changes across backend and frontend in single commit
   - No versioning mismatch between components
   - Easier to maintain consistency

3. **Shared Documentation**
   - All docs in one place
   - Architecture decisions affect all components
   - Sprint planning covers all parts

4. **Code Sharing**
   - Share types/interfaces between backend and frontend
   - Common utilities and constants
   - Consistent API contracts

5. **Simplified CI/CD**
   - Single CI/CD pipeline
   - Test all components together
   - Deploy as a unit

6. **Better for Learning**
   - See full stack in one place
   - Understand how components interact
   - Easier to refactor across boundaries

## Consequences

### Positive

✅ **Simplified Setup**
- New developers clone one repo
- Single set of Git workflows
- Unified documentation

✅ **Consistency**
- Shared linting/formatting configs
- Consistent commit conventions
- Unified versioning strategy

✅ **Cross-component Changes**
- API changes update backend and frontend together
- No synchronization issues
- Easier refactoring

✅ **Reduced Overhead**
- Single issue tracker
- One PR process
- Unified changelog

✅ **Better Collaboration**
- Full-stack developers see everything
- Easier code reviews across boundaries
- Shared understanding

### Negative

❌ **Larger Repository Size**
- More files to download
- Larger .git history
- Mitigation: Use .gitignore properly

❌ **Potential for Tight Coupling**
- Risk of creating dependencies between components
- Mitigation: Maintain clear boundaries, use APIs

❌ **Build Complexity**
- Need to handle multiple build systems
- Mitigation: Clear documentation, separate scripts

❌ **Access Control Challenges**
- Cannot give different access to different components
- Mitigation: Not an issue for solo/small team learning project

## Implementation Details

### Directory Structure
Each component maintains its own:
- Dependencies (requirements.txt, package.json)
- Configuration files
- README.md
- Tests

### Git Workflow
- Main branch: production-ready code
- Develop branch: integration
- Feature branches: component-specific or cross-component

### Build & Deploy
```bash
# Backend
cd backend && python manage.py runserver

# Frontend
cd frontend && npm run dev

# AI Service
cd ai-service && python main.py
```

### Documentation
- Root README: project overview
- Component READMEs: component-specific docs
- docs/: shared architecture and design docs

## Alternatives Considered

### Why Not Separate Repos?

**Cons:**
- Complex setup (3 repos to clone)
- Hard to sync API changes
- More overhead in issue tracking
- Difficult for learning purposes

**When to Use:**
- Large teams with separate ownership
- Components deployed independently
- Need granular access control

### Why Not Hybrid?

**Cons:**
- Adds complexity without significant benefits
- Still need to sync 2 repos
- AI service is integral to the application

**When to Use:**
- AI service maintained by different team
- AI service used by multiple projects

## Review Date

This decision will be reviewed at the end of Sprint 3 (after 6 weeks) to ensure it's working well for the project.

## References

- [Monorepo Tools](https://monorepo.tools/)
- [Google's Monorepo](https://cacm.acm.org/magazines/2016/7/204032-why-google-stores-billions-of-lines-of-code-in-a-single-repository/fulltext)
- [Monorepo vs Polyrepo](https://blog.nrwl.io/misconceptions-about-monorepos-monorepo-monolith-df1250d4b03c)

## Notes

- This is appropriate for our learning project and small team
- May need to reconsider for large-scale production with multiple teams
- Focus on maintaining clear component boundaries despite monorepo structure
