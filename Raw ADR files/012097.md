# ADR: Development Process

> **Warning:** This ADR was migrated from pre-documentation-standards decisions. Do not use as a template for new ADRs. See `TEMPLATE.md` instead.

> Date: 2025-12-04
> Status: **Adopted**

## Context

musix.js needs standardized development workflows for branching, versioning, CI/CD, documentation generation, and changelog management. These processes should support both solo development and future collaboration.

## Decision Drivers

- Simple workflow for small team/solo development
- Automated quality gates
- Clear version history
- Easy to generate documentation from code
- Standard practices familiar to contributors

## Options Considered

### Branch Strategy
- **Option 1:** Git Flow
- **Option 2:** GitHub Flow
- **Option 3:** Trunk-based development

### Versioning
- **Option 1:** SemVer
- **Option 2:** CalVer
- **Option 3:** Custom

### CI/CD
- **Option 1:** GitHub Actions
- **Option 2:** CircleCI
- **Option 3:** None

### Documentation
- **Option 1:** TypeDoc
- **Option 2:** VitePress
- **Option 3:** None

### Changelog Management
- **Option 1:** Manual CHANGELOG.md
- **Option 2:** Conventional Commits
- **Option 3:** Automated from PRs

## Decisions

| Category | Decision |
|----------|----------|
| Branch Strategy | **GitHub Flow** |
| Versioning | **SemVer** |
| CI/CD | **GitHub Actions** |
| Documentation | **TypeDoc** |
| Changelog | **Conventional Commits** |

## Rationale

### Branch Strategy: GitHub Flow

- Simple: `main` + feature branches
- PR-based development with reviews
- Suitable for continuous deployment
- Low overhead compared to Git Flow

Workflow:
1. Create branch from `main`
2. Make changes
3. Open PR
4. Review and merge

### Versioning: SemVer

Standard semantic versioning:
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

Well understood by npm ecosystem and consumers.

### CI/CD: GitHub Actions

- Native GitHub integration
- Free for public repositories
- Large marketplace of actions
- Handles test, build, and publish workflows

### Documentation: TypeDoc

- Most popular TSDoc documentation generator (8,300+ GitHub stars, 2.4M weekly downloads)
- Simple configuration
- Generates standalone HTML site
- Rich plugin ecosystem
- Direct integration with TypeScript compiler

### Changelog: Conventional Commits

Commit format:
```
type(scope): description

body
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Benefits:
- Consistent commit history
- Enables automated CHANGELOG generation
- Clear communication of change intent
- Standard recognized across the ecosystem

## Consequences

**Positive:**
- Simple, familiar workflows
- Automated quality enforcement
- Documentation stays in sync with code
- Clear version and change history

**Negative:**
- Conventional Commits requires discipline
- TypeDoc output may need customization for complex documentation needs

**Risks:**
- Conventional Commits may be ignored without tooling - Can add commitlint later if needed

## Related Decisions

- [20251204-development-toolchain.md](./20251204-development-toolchain.md)
