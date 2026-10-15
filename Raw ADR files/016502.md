# Title: ADR 3: Development Workflow

## Context
Our team needs a development workflow that supports the course requirements for GitLab and Docker usage. The workflow must accommodate phase-based development cycles, maintain code quality through automated testing, and ensure proper traceability between code changes and project requirements. Constraints include maintainer-only access to main branch, required GitLab issue tracking for all work, and Docker containerization for deployment.

## Decision
We will follow a development workflow that uses branches for each project phase, issue/feature branches for individual work, automated CI/CD pipelines for quality assurance and testing, and standardized tooling for consistency across local development environments. 

## Status
Revised

## Consequences

**Branch Strategy:**
- Protected `main` branch with maintainer-only access
- Cycle branches (`cycle-1/design`, `cycle-2/implement`, etc.) serve as development bases for each project phase. These branches will require merge requests after Design 1 is complete
- Feature branches (`feature/name` or `feature-#/name`) used when multiple people work together on related issues or work spans several interconnected issues.
- Issue branches (`issue-#/description`) created directly off current cycle or feature branches for individual work based on GitLab issues
- Branch names are enforced through GitLab

**Review & Merge Process:**
- Merge requests with minimum 1 (non-author) reviewer required for merges into cycle branches or main.
- Automated testing pipeline (detailed in [Test Plan](../1-design/test-plan.md)) must pass for merges into cycle branches or main.
- Full commit history preserved (no squashing, enforced) for traceability during grading.
- Individual work on issue/feature branches can be pushed without review.
- Captured in issue #17

**CI/CD & Testing Pipelines:**
- Pipeline stages: `lint` $\rightarrow$ `build` $\rightarrow$ `test` $\rightarrow$ `publish`
- Automated Jest tests and Docker container builds run only on merge requests to cycle branches/main.
    - Includes checks for minimum code coverage of 70% based on Jest reports.
- Merges to main that pass the pipeline are automatically deployed to GitLab container registry.
- Captured in issue #15 #14 #13 #12
- Captured metrics about the pipeline can be found here: [Pipeline Metrics](https://gitlab.csc.uvic.ca/courses/2025091/SENG350_COSI/teams/group_1_proj/-/pipelines/charts?chart=pipelines)
    * Goal: 100% of merge requests pass the pipeline
    * Good: 75% of merge requests pass pipeline
    * Acceptable: 50% of merge requests pass pipeline
    * Improvement needed: less than 50% of merge requests pass pipeline

**Issue Management:**
- All work tracked through GitLab issues as required by course.
- Issues linked to milestones for deadline tracking.
- Issue boards with lanes: Open $\rightarrow$ In Progress $\rightarrow$  Closed.

**Local Development:**
- ESLint used for TypeScript linting to ensure consistent/clean code style across project.
    - Developers should run linting locally before pushing to avoid CI failures.
- NPM scripts: `npm test`, `npm lint`, etc. for commonly used commands.
    - These scripts can then also be used in pipelines which makes it easy to synchronize changes if the underlying commands change.
- Standardized VSCode setup with committed `.vscode/` folder for launch scripts and workspace configuration.