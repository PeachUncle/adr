---
title: "ADR 014: Centralized UI Design System (@squievreux/ui)"
type: "architecture"
audience: "developer"
status: "accepted"
priority: "high"
version: "1.0.0"
created: "2025-12-30"
updated: "2025-12-30"
reviewers: ["@quievreux"]
tags: ["ui", "design-system", "npm", "github-packages"]
---

# ADR 014: Centralized UI Design System (@squievreux/ui)

## Status
Accepted

## Date
2025-12-30

## Context
Across the ecosystem of Quievreux applications, UI consistency has been challenging. Specifically:
- **Icons:** We rely on `lucide-react`, but the implementation varies. Some projects use raw imports, others wrap them. Changing an icon style requires changes in every repository.
- **Design Tokens:** Maintaining consistent colors (Primary/Secondary) and "Vibe" aesthetics (Glassmorphism, Neon) is manual and error-prone when duplicated across projects.
- **Maintenance:** Updates to the design language require manual pull requests in multiple repositories.

## Decision
We decided to extract the core UI elements into a centralized, private NPM package: **`@squievreux/ui`**.

### Key Components
1.  **Registry:** Hosted on **GitHub Packages** (allowing private access scoped to `@squievreux`).
2.  **Icons:** A unified `<Icon />` component that standardizes size, class names, and default styling for `lucide-react` icons.
3.  **Styles:**
    - Shared CSS variables for colors (`--q-color-primary`, etc.).
    - A Tailwind CSS preset (or configuration injection) to ensure all apps share the same theme extensibility.

### Authentication
- **CI/CD:** Uses `GITHUB_TOKEN` automatically injected by GitHub Actions.
- **Local Dev:** Uses a Personal Access Token (PAT) with `read:packages` scope, configured via `.npmrc`.

## Consequences

### Positive
- **Consistency:** All apps immediately inherit the correct design tokens and icon styles upon updating the package.
- **Maintainability:** Fixes to styles or icons are done in one place (`quievreux/ui-design-system` repo) and versioned.
- **Speed:** New projects can be bootstrapped with the "Vibe" look immediately by installing the package.

### Negative
- **Dependency:** All projects now depend on the GitHub Package Registry uptime and authentication.
- **Complexity:** Local development requires setting up a PAT. CI/CD pipelines need `packages: read` permissions explicitly configured.

## Mitigations
- Created a `rollout-ui.ts` script to automate the `.npmrc` and CI workflow updates to prevent configuration errors.
- Documented the PAT setup process clearly for developers.
