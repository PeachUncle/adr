# ADR 0011: Configure CI/CD Pipeline with Linting, Git Hooks, and Planned GitHub Actions

## Status

Accepted

## Context

We want to establish a Continuous Integration and Continuous Deployment (CI/CD) foundation for the Meatbag project. At the MVP stage, the goal is to ensure:

- Clean code quality at every commit
- Preventing broken code from being pushed
- Ensuring all code contributions are tested, styled, and linted

We’ve started with commit-time safeguards and plan to extend CI/CD over time.

## Decision

### ✅ Phase 1: Commit-time Quality Enforcement

We’ve implemented the following tools and policies:

- **[Husky](https://typicode.github.io/husky/)** — Git hooks for pre-commit and pre-push checks
- **[lint-staged](https://github.com/okonet/lint-staged)** — Run linters only on staged files
- **ESLint** — Used to lint JavaScript and React code during development
- Pre-commit hook blocks commits if linting fails

This enforces high code quality **before anything leaves the local machine**, which helps maintain a stable main branch.

### 🔄 Phase 2: Planned CI/CD Enhancements

We plan to extend the pipeline with:

- **Stylelint** — To enforce styling best practices for CSS Modules and other stylesheets
- **GitHub Actions**:
  - ✅ Lint and test checks triggered on PRs
  - ✅ Required checks before merging into `main`
  - ✅ Future: deploy preview builds on PR (e.g., Vercel preview or Storybook)

These changes will formalize a **pull request-based CI/CD flow** and ensure the integrity of the main branch.

### 🚀 Deployment

- **Vercel** is used for both production and preview deployments.
- Automatic builds happen on pushes to `main`, with preview builds available for PRs via Vercel’s Git integration.

## Consequences

- Commits cannot proceed unless ESLint passes (enforced by pre-commit hook)
- Linting only runs on staged files, keeping performance fast
- Team members must install Husky hooks (automatically done via `prepare` script)
- GitHub Actions will need additional setup to support test automation and PR protection rules
- More CI checks = slower merges, but higher long-term quality

## Future Considerations

- Add a Stylelint config and integrate it into `lint-staged` and CI
- Explore `jest --coverage` or `vitest` coverage in CI
- Introduce GitHub Actions matrix to test across environments or dependency versions
- Enforce changelog and commit standards using `commitlint` or semantic PR titles

---

_Created: 2025-06-20_
