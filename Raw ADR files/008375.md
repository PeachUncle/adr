---
status: accepted
date: 2025-05-10
decision-makers: Whole Group
consulted: Whole Group
informed: Whole Group
---

# CI/CD Pipeline Strategy for UCSD College Card Compare MVP

## Context and Problem Statement

Our team is developing a browser-based offline card collection MVP. To support stable development and ensure quality, we decided to implement a lightweight CI/CD pipeline using GitHub Actions. The goal is to automate essential quality checks (like linting, testing, validation, documentation generation, and performance auditing) on Pull Requests to prevent errors, enforce consistency, and maintain project standards. Each team member has researched a pipeline component, and Pranay will consolidate the pieces into a single `.yaml` workflow.

## Decision Drivers

* Maintain a stable, deployable `main` branch
* Automate detection of code quality issues
* Enable fast feedback loops on Pull Requests
* Align with team size, experience level, and MVP simplicity
* Follow best practices using open-source tools and minimal overhead

## Considered Options

* Single `.yaml` GitHub Actions workflow integrating all CI steps
* Separate workflows per component (e.g., linting, testing, docs, etc.)
* Manual pre-merge checks without CI
* Post-merge validation (reactive, not preventative)

## Decision Outcome

Chosen option: **"Single `.yaml` GitHub Actions workflow integrating all CI steps"**, because it balances automation, simplicity, and effectiveness. It allows us to run all quality checks in a centralized way and integrates well with our simplified GitHub Flow-based branching strategy.

### Consequences

* Good, because automated checks will run on all PRs to `develop` and `main`, reducing regressions
* Good, because developers receive clear, consistent feedback from the same workflow
* Good, because code reviews and CI checks together raise confidence in merges
* Neutral, because build times may be slightly longer with a monolithic workflow
* Bad, because setup and debugging of the integrated pipeline may be initially time-consuming

### Confirmation

We will verify implementation by:
* Requiring passing checks from the `.yaml` workflow on all PRs to `main` and `develop`
* Using GitHub branch protection rules
* Ensuring the pipeline includes all components: ESLint + Prettier, Jest, Lighthouse, JSDoc, and W3 HTML/CSS validators
* Confirming workflow triggers on every push/PR and reports results in the GitHub UI

## Pros and Cons of the Options

### Single `.yaml` GitHub Actions Workflow

* Good, because it's centralized and easy to maintain for a small project
* Good, because it provides consistent PR feedback across tools
* Neutral, because the build can be slower if many tools are included
* Bad, because failure debugging may be less granular

### Separate Workflows Per Component

* Good, because easier to debug individual failures
* Good, because team members can own specific pipelines
* Neutral, because it may not save time on small projects
* Bad, because setup is more verbose and complex

### Manual Pre-Merge Checks Without CI

* Good, because no time spent on CI setup
* Neutral, because may still catch some errors
* Bad, because it's prone to human error and inconsistency
* Bad, because developers may skip steps under time pressure

### Post-Merge Validation Only

* Good, because it's less disruptive to development flow
* Bad, because broken code can already be merged
* Bad, because error discovery is reactive and late in the process

## More Information

This decision reflects our goal of building a clean, well-engineered MVP with minimal bugs and consistent formatting. The CI/CD pipeline will support this by checking every PR for:
* Linting with ESLint + Prettier (using a shared config based on W3Schools JS conventions)
* Unit testing via Jest
* Lighthouse auditing (accessibility and performance)
* JSDoc comment coverage (confirm docs generate successfully)
* HTML and CSS validation using W3C tools

The GitHub Actions workflow will be located in `.github/workflows/ci.yml` and triggered on `push` and `pull_request` events. This setup creates a foundation we can expand in future iterations if needed (e.g., E2E testing, deployment).
