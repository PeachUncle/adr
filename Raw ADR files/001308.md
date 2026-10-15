# ADR-004: Versioning Strategy

## Status

Accepted

## Context

The project requires a clear and automated versioning strategy to ensure that
each change to the **main** branch is treated as a release. Every commit to the
**main** branch must represent a fully functional product and be assigned a
semantic version. This ensures consistency, traceability, and easy
identification of breaking changes, new features, and patches.

To achieve this, the versioning strategy will follow these principles:

1. Each commit to the **main** branch is treated as a new release.
2. The repository will start with an initial version of `0.1.0`.
3. Commit messages will include specific prefixes to determine the type of
   semantic version bump:
   - **"Major:"** or **"Breaking:"**: Increments the major version (e.g.,
     `1.2.3` -> `2.0.0`).
   - **"Minor:"** or **"Feature:"**: Increments the minor version (e.g., `1.2.3`
     -> `1.3.0`).
   - All other commit messages increment the patch version (e.g., `1.2.3` ->
     `1.2.4`).

## Decision

We decided to use a versioning strategy where each commit to the **main** branch
corresponds to a release, following semantic versioning rules driven by commit
message prefixes.

Additionally, each release commit will be tagged using `git tag` with its
corresponding semantic version. Tags will be lightweight and will follow the
format `v<MAJOR>.<MINOR>.<PATCH>` (e.g., `v1.2.3`). Tagging will be automated as
part of the CI/CD pipeline to ensure consistency and reduce manual effort.

## Reasons

1. **Automated and Predictable Versioning**:
   - Automating version bumps ensures that releases are consistent and
     predictable without manual intervention.

2. **Semantic Versioning Compliance**:
   - Following semantic versioning makes it clear to users and contributors what
     kind of changes to expect (e.g., breaking changes, new features, or patches).

3. **Streamlined Workflow**:
   - Treating each commit to the **main** branch as a release simplifies the
     workflow, eliminating the need for separate release branches or manual tagging.

4. **Improved Traceability**:
   - Tagging each release commit with a version ensures that every version is
     easily identifiable, allowing developers to quickly trace changes and debug issues.

5. **Clarity for Collaboration**:
   - Explicit commit message prefixes encourage developers to categorize their
     changes properly, improving communication and collaboration.

## Consequences

1. **Commit Discipline**:
   - Developers must write clear, categorized commit messages with the correct
     prefixes to ensure accurate version bumps.

2. **No Unstable Changes on Main**:
   - Only fully tested and production-ready changes can be merged into the
     **main** branch, as each commit will represent a new release.

3. **Increased Tag Volume**:
   - Tagging every release commit will result in a large number of tags in the
     repository. However, this is considered acceptable to maintain clear
     traceability of versions.

4. **Initial Setup**:
   - Automation scripts and tools will need to be configured to parse commit
     messages, handle version increments, and create tags automatically as part
     of the CI/CD pipeline.

## Alternatives Considered

### Manual Versioning

- **Pros**: Offers complete control over version bumps and release timing.
- **Cons**: Prone to human error and delays in version increments, requiring
  manual effort for each release.

### Using Release Branches

- **Pros**: Allows for more granular control over releases.
- **Cons**: Introduces additional complexity and delays, conflicting with the
  goal of a simple and automated process.

### Skipping Git Tags

- **Pros**: Reduces the number of tags and potential clutter in the
  repository.
- **Cons**: Makes it harder to trace specific versions to commits, reducing
  traceability and clarity.
