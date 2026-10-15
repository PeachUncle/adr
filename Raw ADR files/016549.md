# ADR-0001: Multi-Repository Strategy

**Status:** ✅ Accepted  
**Date:** January 5, 2026  
**Deciders:** Tech Lead, CTO, DevOps Team  
**Consulted:** All Development Team  
**Informed:** Engineering, Product

---

## Context and Problem Statement

The original **monorepo** (`server-app`) contained 9+ Django projects in a single repository. This created several challenges:

### Problems with Monorepo

1. **Cross-Project Commits:** Changes to one project polluted git history of others
2. **Slow CI/CD:** Every commit triggered tests for ALL projects (~30+ min)
3. **Coupled Deployments:** Bug fix in one project delayed deployment of another
4. **Access Control:** Impossible to grant repo access to only one project team
5. **Large Repository:** Clone size growing (1.5+ GB)
6. **Confusing Structure:** New developers struggled to understand boundaries

### Example Issues

```bash
# Commit history polluted with unrelated changes
commit abc123: "Fix bug in prj_medicos"
commit def456: "Update requirements in prj_construtora"
commit ghi789: "Add feature to prj_sisu"
# ALL projects see ALL commits
```

## Decision Drivers

- ✅ **Team Autonomy:** Each project team should work independently
- ✅ **Fast Feedback:** CI/CD must run in < 5 minutes
- ✅ **Clear Ownership:** Obvious who maintains what
- ✅ **Independent Releases:** Deploy projects on different schedules
- ✅ **Granular Access:** Restrict access per project

## Considered Options

### Option 1: Keep Monorepo + Monorepo Tools

**Pros:**
- No migration needed
- Unified versioning
- Easier to refactor shared code

**Cons:**
- Still large clone size
- Requires specialized tooling (Bazel, Nx)
- Complex setup and learning curve
- Doesn't solve access control issues

### Option 2: Microservices Architecture

**Pros:**
- Complete isolation
- Independent scaling
- Technology diversity

**Cons:**
- **Over-engineering** for current scale
- Network latency between services
- Distributed transactions complexity
- Operational overhead (monitoring, tracing)

### Option 3: Multi-Repository (CHOSEN) ⭐

**Pros:**
- ✅ **Simple** - Standard Git workflow
- ✅ **Fast CI/CD** - Test only what changed
- ✅ **Independent deploys** - No coupling
- ✅ **Granular permissions** - Per-repo access
- ✅ **Clear boundaries** - One repo = one project

**Cons:**
- ⚠️ More repos to manage (solved with tooling)
- ⚠️ Shared code management (solved with `server-app-shared` package)
- ⚠️ Cross-repo changes harder (rare, acceptable tradeoff)

## Decision Outcome

**Chosen Option:** Multi-Repository with Shared Library

We migrate from monorepo to multi-repo architecture with:

1. **One repository per Django project** (8 projects)
2. **Shared Python package** (`server-app-shared`) for common code
3. **Infrastructure repository** (`server-app-infrastructure`) for DevOps
4. **Documentation repository** (`server-app-docs`) for centralized docs

### Repository Structure

```
server-app-construtora/     ← Independent repo
server-app-medicos/         ← Independent repo
server-app-emprestimos/     ← Independent repo
server-app-sisu/            ← Independent repo
server-app-maismedicos/     ← Independent repo
server-app-rotinas/         ← Independent repo
server-app-eleicao/         ← Independent repo
server-app-tds/             ← Independent repo
server-app-shared/          ← Shared Python library
server-app-infrastructure/  ← Infrastructure configs
server-app-docs/            ← Documentation hub
server-app (archived)       ← Original monorepo (read-only)
```

## Consequences

### Positive

- ✅ **CI/CD Speed:** Reduced from ~30min to ~3-5min per project
- ✅ **Team Velocity:** Teams can deploy independently
- ✅ **Git History:** Clean, project-specific commit history
- ✅ **Access Control:** Granular permissions per project
- ✅ **Onboarding:** New devs clone only needed repos
- ✅ **Repository Size:** Smaller clones (~100-200MB vs 1.5GB)

### Negative

- ⚠️ **More Complexity:** Need to manage 11+ repositories
- ⚠️ **Shared Code:** Requires discipline to maintain shared library
- ⚠️ **Cross-Repo Changes:** Breaking changes in shared lib affect all projects
- ⚠️ **Documentation:** Must keep docs synchronized across repos

### Mitigations

| Challenge | Mitigation |
|-----------|-----------|
| **Managing multiple repos** | GitHub CLI, scripts for bulk operations |
| **Shared code breaking changes** | Semantic versioning, deprecation policy |
| **Documentation sync** | Central docs repo with MkDocs |
| **Dependency updates** | Renovate/Dependabot for automated PRs |

## Implementation

### Phase 0: Preparation (COMPLETED ✅)
- Created `server-app-shared` Python package
- Created `server-app-infrastructure` repo
- Created migration scripts

### Phase 1: Extraction (COMPLETED ✅)
- Extracted 8 projects to individual repos
- Preserved Git history where possible
- Migrated imports to use `server-app-shared`

### Phase 2: CI/CD (IN PROGRESS 🚧)
- GitHub Actions for each project
- Automated testing and deployment

### Phase 3: Optimization (PLANNED 📋)
- Performance tuning
- Security hardening

### Phase 4: Archival (PLANNED 📋)
- Archive original monorepo (read-only)
- Final documentation update

## Validation

### Success Metrics

| Metric | Before (Monorepo) | After (Multi-Repo) | Status |
|--------|-------------------|-------------------|--------|
| **CI/CD Time** | ~30 minutes | ~3-5 minutes | ✅ Achieved |
| **Clone Size** | 1.5 GB | ~150 MB average | ✅ Achieved |
| **Deploy Frequency** | 1x/week | Daily per project | ✅ Achieved |
| **Team Satisfaction** | Mixed | Positive | ✅ Achieved |

### Lessons Learned

**What Worked Well:**
- Gradual migration (one project at a time)
- Extensive documentation during migration
- Using `git filter-repo` preserved history
- Shared library design upfront

**What Could Be Improved:**
- Earlier communication to all stakeholders
- More automated testing before migration
- Better tooling for cross-repo operations

## Alternatives Considered in Detail

### Why Not Monorepo Tools (Bazel, Nx)?

**Bazel:**
- Requires rewriting all build configs
- Steep learning curve for team
- Overkill for Python/Django projects

**Nx:**
- Primarily for JavaScript/TypeScript
- Limited Python support
- Doesn't solve access control issues

### Why Not Microservices?

- **Current scale doesn't justify** the operational overhead
- **Shared database model** doesn't fit microservices pattern
- **Team size** too small to manage 8+ independent services
- **Can migrate later** if needed (multi-repo is step 1)

## Related Decisions

- [ADR-0002: Shared Library Strategy](0002-shared-library.md)
- [Migration Overview](../migration/overview.md)
- [Architecture Overview](../architecture/overview.md)

## References

- [Monorepo vs Multi-Repo](https://earthly.dev/blog/monorepo-vs-polyrepo/)
- [Google's Monorepo (Why it works for them)](https://research.google/pubs/pub45424/)
- [GitLab's Multi-Repo Strategy](https://about.gitlab.com/blog/2020/03/30/why-we-spent-the-last-month-eliminating-postgresql-subtransactions/)

---

**Author:** Tech Lead  
**Reviewed by:** CTO, DevOps Lead  
**Approved:** January 5, 2026
