**ADR: 050925-Branching-Strategy.md**

**Title:** Branching Strategy for UCSD College Card Compare MVP

**Date:** 2025-05-09

**Status:** Accepted

**Context:**
The UCSD College Card Compare project is a web application aimed at creating a simple, offline, themed collectible card experience for UCSD students and enthusiasts. The MVP (as defined in the project pitch by Nick & Chencheng) focuses on displaying a predefined, static set of cards, local data storage (IndexedDB), and a basic card comparison interface using HTML, CSS, and vanilla JavaScript. Key "No-Gos" for the MVP include multiplayer features, user accounts, and complex game mechanics, emphasizing minimalism.

Our team (Team 13 - Cache me outside) is relatively small and working within a limited timeframe (typical of a course project). We need a branching strategy that supports parallel development of small features, ensures a stable main codebase, facilitates code reviews, and integrates with our planned CI/CD pipeline (linting, testing, etc., as discussed in our 05/09 meeting). The professor has also generally advised keeping processes manageable, utilizing Git branches, Pull Requests (PRs) for control, and issues for task monitoring (a common best practice).

**Decision Drivers:**

*   **Project Simplicity (MVP):** The MVP is focused on core read and simple logic operations, with many complex features explicitly excluded.
*   **Team Size & Experience:** As a student team, a straightforward strategy reduces cognitive overhead and potential for errors.
*   **Rapid Iteration & Feedback:** Aligns with Agile principles, allowing for quick development and integration of small features.
*   **CI/CD Integration:** The strategy must support automated checks on PRs.
*   **Maintainability of `main` branch:** The `main` branch should always represent a stable, deployable state.
*   **Course Guidelines & Professor's Advice:** Leaning towards practical, manageable workflows for student projects.

**Considered Options:**

1.  **GitFlow:**
    *   *Description:* A robust model with dedicated branches for features, releases, hotfixes, develop, and main.
    *   *Pros:* Excellent for managing complex release cycles, versioning, and hotfixes in larger, long-lived projects.
    *   *Cons:* Considered overly complex for our MVP's scope and team size. The overhead of managing multiple long-lived branches (e.g., `release`, `hotfix`) is unnecessary given our current "No-Gos" (no server deployment focus for MVP, simple offline app).
    *   *Rejection Reason:* Too heavyweight for our current project phase and scale. Our MVP doesn't have the complex release management needs GitFlow is designed for.

2.  **Trunk-Based Development (TBD):**
    *   *Description:* All developers commit to a single branch (`main` or `trunk`), possibly using short-lived feature flags or branches.
    *   *Pros:* Maximizes CI/CD, very simple branching structure.
    *   *Cons:* Requires extremely mature and robust automated testing, CI/CD pipelines, and feature flagging capabilities from the outset. High risk of destabilizing `main` if not managed perfectly.
    *   *Rejection Reason:* While attractive for its simplicity, it's too risky for a student team still developing its CI/CD pipeline and testing practices (as per our 05/09 meeting notes where we are still assigning tasks for setting up these components).

3.  **GitHub Flow (or Simplified Feature Branching):**
    *   *Description:* `main` is always deployable. New work is done on descriptively named feature branches created from `main` (or a `develop` branch). When complete, feature branches are merged back via Pull Requests, encouraging code review and CI checks.
    *   *Pros:* Simple, lightweight, promotes frequent integration, supports PRs and code reviews effectively, `main` remains stable. Aligns well with CI/CD.
    *   *Cons:* Relies on team discipline for timely PR reviews and maintaining small, focused feature branches.

**Decision Outcome:**

We have decided to adopt a **Simplified Feature Branching Model**, akin to GitHub Flow, with the following structure:

*   **`main` branch:** This branch will always represent the most stable, production-ready (or in our MVP case, demo-ready and "done") version of the application. All CI checks must pass before merging into `main`. This branch will be protected.
*   **`develop` branch:** This will serve as an integration branch. All feature branches will be merged into `develop` first. This allows for testing the combined features before they are promoted to `main`. CI checks will also run on PRs to `develop`.
*   **`feature/<descriptive-name>` branches:** All new work (features, bug fixes identified through issues) will be done on short-lived feature branches. These will be branched off `develop`.
    *   Example: `feature/card-display`, `feature/comparison-logic`, `feature/setup-eslint`
*   **Pull Requests (PRs):** All merges from `feature/*` branches into `develop`, and from `develop` into `main`, will be done via Pull Requests. This ensures code review (by at least one other team member, as per our planned human review in CI/CD discussion) and allows automated CI checks (linting, unit tests, etc.) to run before merging.
*   **Issues:** GitHub Issues will be used to track tasks, features, and bugs. PRs should reference the issue(s) they address. This aligns with the professor's general guidance and our team's assignment of Pranay and Chencheng to manage GitHub issues.

This decision was based on the discussion in our 05/09 meeting ("work on feature -> commit and push to dev-branch -> merge dev and main; main branch – functioning?; protected – git actions here?; branching for features (teams)").

**Consequences:**

*   **Workflow:** Developers will create a new `feature/*` branch from `develop` for each task/issue. Upon completion, they will open a PR to merge their feature branch into `develop`. After `develop` is verified (e.g., at the end of a sprint or when a set of features is complete and tested together), a PR will be made to merge `develop` into `main`.
*   **Stability:** The `main` branch remains stable and deployable. The `develop` branch allows for integration testing before code reaches `main`.
*   **Collaboration:** PRs provide a clear mechanism for code review and discussion.
*   **CI/CD:** Our CI/CD pipeline (as planned in the 05/09 meeting with linting, code quality tools like Lighthouse, CSS/HTML validators, Jest unit tests, and JSDoc generation) will be configured to run on Pull Requests targeting `develop` and `main`.
*   **Tooling:** This strategy integrates well with GitHub Issues for task tracking and project management.
*   **Simplicity:** It's a relatively simple model for the team to understand and follow, fitting the MVP's minimalist approach and our current development stage.

**Links:**

*   [Team 13 Project Pitch (Cache me outside)](https://docs.google.com/document/d/1z_BC8iYo8Uf_ouSWurhVS4jXji_YweiUFMjcMMR5MZc/edit?tab=t.0)
*   [Team 13 Meeting Notes 05/09](https://docs.google.com/document/d/14ISN6ozl9i7FTTKV629b80B0p1wjgC_N9H0BXZPPrf8/edit?tab=t.0)
*   [Course Notes: 04 - Groups - Work Patterns and Practices](https://houses-pay-526.craft.me/kWQ3qUEctR4yNc) (specifically the "Branch Wisely" section)
*   [GitHub Flow Guide](https://docs.github.com/en/get-started/quickstart/github-flow)
