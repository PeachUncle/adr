---
title: Hosting Strategy for ADR Repositories
status: accepted
date: 2025-06-10
tags: [infra, process]
---

# 000001 - Hosting Strategy for ADR Repositories

## Context

As technical and organizational decisions grow in number and scope, it becomes important to manage where and how decisions are stored and surfaced. Our goals include:

- Making decision records transparent and easily accessible
- Supporting both org-wide and project-scoped decisions
- Preserving the ability to evolve our tooling or presentation strategy over time
- Minimizing initial setup effort while laying groundwork for future growth

## Decision

We will adopt the [MADR format](https://adr.github.io/madr/) with YAML frontmatter to capture metadata such as `title`, `status`, `date`, and `tags`. Decisions will be organized across two scopes:

1. **Org-Wide Decisions**
   - Stored in a public GitHub repository: `org-decisions`
   - Located in a `decisions/` directory, with one file per decision
   - Filenames will follow the pattern: six-digit, zero-padded, monotonically increasing integer, followed by a lowercased, hyphen-delimited version of the title (e.g., `000001-hosting-strategy-for-adr-repositories.md`)
   - No dedicated viewer tooling initially—decisions will be read directly via GitHub
   - No license applied, preserving full copyright

2. **Project-Specific Decisions**
   - Stored within each project repository
   - Preferably in a developer documentation branch (e.g., `dev-docs`)
   - If incompatible with documentation tooling, decisions may live in an orphan branch or a dedicated internal directory

## Alternatives Considered

- **Store decisions only in each project repo**  
  *Rejected.* This would fragment high-level decisions and reduce visibility of org-wide choices (e.g., shared tooling or documentation standards).

- **Single flat `adr/` directory in the org-wide repo**  
  *Rejected.* Using a dedicated `decisions/` directory avoids future collision with tooling or index files.

- **Render via MkDocs or Docusaurus immediately**  
  *Postponed.* We opted to keep tooling light initially. Once a small library of decisions is established, we may revisit presentation options like:
  - Docusaurus-based site
  - `log4brains` viewer
  - MkDocs with `awesome-pages-plugin`

- **Use a permissive open-source license**  
  *Rejected for now.* Given the personal and strategic nature of these decisions, we prefer to control reuse. This may change later.

## Consequences

### Positive

- Avoids premature investment in viewer tooling while enabling future migration
- Distinct scopes prevent cross-contamination of project-local vs. organizational decisions
- GitHub provides a low-friction path to publish and consume decisions
- YAML frontmatter enables machine-parsing and future viewer integration with minimal refactor

### Negative

- Markdown files viewed in GitHub may lack polish or structure expected from a documentation system
- No index, search, or categorization beyond what GitHub provides natively
- Requires manual navigation between related decisions (e.g., supersession)
- Storing decisions in multiple locations introduces decentralization, increasing cognitive load for contributors who span multiple projects
- Lacks built-in validation of metadata fields (e.g., typos in `status` or `tags`) unless future tooling is added
