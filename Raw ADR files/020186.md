# ADR 003: Git Usage Strategy

## Status

Accepted

## Context

In this project, we are embracing a Git workflow that may not align with industry standards or the most commonly accepted practices. However, it reflects a philosophy I believe can greatly enhance the clarity, maintainability, and usability of a codebase. This Git strategy is designed to curate a clean, well-documented history that makes it easier for developers to understand the evolution of the project. As this project is intended to serve as a reference, the aim is to showcase an alternative approach that others may appreciate and adopt.

The strategy revolves around two pillars: **Conventional Commits** and **rebasing/amending workflows**. By enforcing a consistent commit style and a polished Git history, we aim to create a more meaningful, informative, and navigable version history.

### Pillar 1: Conventional Commits

We will adopt the **Conventional Commits** specification for structuring commit messages. This helps us in several ways:

1. **Release Notes**: By following a structured format for commits (e.g., `feat:`, `fix:`, `chore:`), we can automatically generate changelogs and release notes, ensuring that every feature or fix is accurately tracked and reflected in our documentation.

2. **Clear History**: Conventional commit messages make it much easier to understand the context of changes when reviewing the Git history. They provide developers with a uniform language for categorizing and interpreting commits.

The commit message structure will follow this pattern:
```
<type>(<scope>): <subject>
```
Where:
- **type**: The category of the change (e.g., `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`).
- **scope**: Optional, but it can be used to define the module or context of the change.
- **subject**: A brief description of the change.

This convention will be enforced throughout the codebase, and we will use tooling (such as commit linting) to ensure compliance.

### Pillar 2: Rebasing and Amending

The second core practice is **rebasing** and **amending** commits, with an explicit prohibition on merge commits. Our goal is to have a clean and coherent commit history, where each feature or bug fix is encapsulated in a single, well-crafted commit. This approach encourages discipline in commit crafting and results in a readable, informative Git history.

#### Key Practices:

- **Rebasing**: Instead of merging feature branches into the main branch with a merge commit, we will use rebasing to apply changes on top of the latest version of the main branch. This removes the unnecessary "noise" introduced by merge commits and ensures that the history remains linear.

- **Amending**: Developers are encouraged to amend commits within their feature branches as necessary. This allows for the refinement and polishing of commits before they are introduced to the main branch. It provides the flexibility to create any number of commits during development, as long as the final version is cleaned up to reflect one neatly curated commit per feature or fix.

Note that the main branch should not be rewritten, as the cost to synchronise between developers would be too great.

#### Benefits:

- **Curated History**: By encouraging the cleanup and consolidation of commits, the main branch will have a history where each feature or bug fix is presented as a single, cohesive commit. This makes it much easier for others to review changes and track the evolution of the project.

- **Duplication Elimination**: Git's rebase functionality intelligently handles redundant or duplicate commits, allowing developers to easily drop commits that are no longer necessary. This is particularly useful when integrating partial or overlapping changes.

- **Prevention of Merge Commits**: By prohibiting merge commits, we avoid cluttering the Git history with unnecessary markers and maintain a clear, linear progression of changes.

## Decision

We will adopt the following Git workflow for this project:
1. **Conventional Commits**: All commits must follow the Conventional Commits format to ensure clarity and consistency in the commit history.

2. **Rebasing and Amending**: Developers are required to rebase their feature branches before merging into the main branch and consolidate their commits into a single, well-structured commit. Merge commits are prohibited.

3. **Branching Strategy**: Within a feature branch, developers can create as many commits as they need for their work. However, before merging to the main branch, they must clean up the history, amending and squashing commits as necessary to produce curated, single-commit representations of the features or fixes.

4. **No Merge Commits**: To maintain a clean, linear history, we will not allow merge commits. All changes must be rebased onto the latest version of the main branch.

## Consequences

- **Positive**:
	- **Curated History**: The Git history will remain clean, concise, and easy to navigate, making it simpler for developers to review and understand the codebase.
	- **Automated Release Notes**: The use of Conventional Commits enables us to automatically generate accurate release notes and changelogs.
	- **Easier Code Reviews**: Each feature or fix will be encapsulated in a single commit, making it easier to review the impact of changes.
	- **Less Noise**: The absence of merge commits will prevent the Git history from becoming cluttered with redundant or meaningless commit messages.
	- **Code sharing**: Fixes can be shared between branches before being merged, allow developers to continue without having to wait for reviews or merge trains.

- **Negative**:
	- **Initial Learning Curve**: Developers unfamiliar with rebasing and amending may require time to adapt to this workflow.
	- **Increased Effort**: Cleaning up and consolidating commits requires extra effort at the end of the feature development process.
