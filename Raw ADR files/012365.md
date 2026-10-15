# ADR 0010: Use Monorepo Project Structure

## Status

Accepted

## Context

The Meatbag project consists of multiple interconnected parts, including:

- A **Next.js application** (`/`)
- A **Docusaurus documentation site** (`/docs`)
- Future additions such as utility libraries, design systems, or an API layer

We needed to decide whether to keep each concern in a separate repo (polyrepo) or in a single unified repo (monorepo).

Options considered:

| Approach     | Pros                                                        | Cons                              |
| ------------ | ----------------------------------------------------------- | --------------------------------- |
| **Monorepo** | Easier refactoring, unified tooling, single source of truth | Requires structure & discipline   |
| **Polyrepo** | Clear separation of concerns, isolated CI                   | Difficult to coordinate changes   |
| **Hybrid**   | Isolate external libraries, but keep main app/docs together | More complex setup and deployment |

## Decision

We chose to adopt a **monorepo** approach.

Rationale:

- Jonathan's prior **experience** with monorepos ensures confidence in tooling and structure
- Docusaurus documentation and Next.js app live side-by-side in one Git project
- Easier to **manage dependencies**, share components, and refactor across boundaries
- Simplified **CI/CD pipeline** (single GitHub repo, unified Vercel deployments)
- Smooth development experience for solo and team workflows

## Consequences

- All code lives in one repo, with clear top-level folders:
  - `/` → Next.js app
  - `/docs` → Docusaurus documentation
- Shared tooling for linting, testing, formatting, version control
- Documentation and app can be deployed independently from the same repo
- Requires consistent naming, structure, and `package.json` script coordination

## Future Considerations

- Consider tools like **Turborepo** or **Nx** if build complexity increases
- Introduce a `packages/` directory if shared packages/modules emerge
- Document and enforce naming conventions and folder boundaries in contributing guide

---

_Created: 2025-06-20_
