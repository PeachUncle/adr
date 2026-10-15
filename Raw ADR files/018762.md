# Implementing Semantic Versioning in our Monorepo

## Status

Accepted

## Context

In our current Turborepo monorepo setup, we have multiple developers contributing to various parts of the monorepo. As the project grows and multiple people contribute code, the challenge of understanding and managing versions becomes increasingly difficult. Without a clear versioning strategy, developers may find it challenging to know what changes have been made, or how those changes might impact their work. We've identified an article titled ["Monorepo Semantic Releases"](https://medium.com/valtech-ch/monorepo-semantic-releases-db114811efa5) that provides a blueprint for the integration of semantic versioning in this monorepo.

## Decision

To introduce clarity and ensure consistency, we propose the adoption of Semantic Versioning (SemVer) for our monorepo, as detailed in the aforementioned article. Specific tools and practices will aid in this process:

1. [**Conventional Commits**](https://www.conventionalcommits.org/en/v1.0.0/): This standardized commit message format provides an easy-to-read history, making it simpler to deduce the version bump (major, minor, or patch) and the type of changes made (fixes, features, etc.). It also supports automated changelog generation.
2. [**Husky**](https://typicode.github.io/husky/): With `husky`, we can enforce the usage of Conventional Commits format, ensuring that every commit adheres to the standard.

3. [**Release-it**](https://github.com/release-it/release-it): This tool will be responsible for handling our releases, making it more straightforward to tag and version our codebase, while also helping to automatically update changelogs and apply tags based on commit messages.

4. [**MVM (Monorepo Version Manager)**](https://github.com/b12k/mvm/tree/master#monorepo-versions-manager): We utilize `mvm` to manage releases between dependent packages within a monorepo. Changes of an up-stream dependency should cause a release down-stream dependents.

## Consequences

1. **Clearer Versioning**: Developers and stakeholders will have a more explicit understanding of the changes and state of the project at any given version.

2. **Enhanced Collaboration**: Developers can have confidence in the changes made by their peers and how those changes impact their own work.

3. **Improved Changelog**: With automated changelog generation, the record of changes will be organized and easy to understand.

4. **Learning Curve**: Developers will need to familiarize themselves with the Conventional Commits format and the tools being introduced. Some time will be needed for adaptation, but the long-term benefits will outweigh the initial setup time.

5. **Discipline in Commits**: Developers must be more thoughtful about their commit messages as they can directly impact versioning and changelogs.
