# 7. Release Management with Changesets

Date: 2025-08-28

## Status

Accepted

## Context

The project needed an automated release management system that would:

- Generate semantic versions based on changes
- Maintain a comprehensive changelog
- Support conventional commit workflows
- Integrate with CI/CD for automated releases
- Provide flexibility for different types of changes
- Enable easy rollbacks and version tracking

Key options considered:

- **semantic-release**: Fully automated based on commit messages
- **Changesets**: Explicit change documentation with automation
- **Standard Version**: Conventional commits with manual control
- **Manual Versioning**: Full manual control with scripts

## Decision

We chose **Changesets** for release management because:

1. **Explicit Documentation**: Developers explicitly document changes
2. **Flexible Automation**: Automated versioning with human oversight
3. **Team Workflow**: Supports collaborative development patterns
4. **Changelog Quality**: High-quality changelogs with context
5. **Integration**: Excellent GitHub Actions integration

### Implementation Details

- **Changeset CLI**: `@changesets/cli` for managing changesets
- **GitHub Integration**: `@changesets/changelog-github` for rich changelogs
- **Workflow**:
  1. Developers add changesets with `pnpm changeset`
  2. CI validates changesets exist for feature/fix commits
  3. Version updates and changelog generation on merge to main
  4. Automated GitHub releases with artifacts

- **Validation**: Custom script ensures feat/fix commits have changesets
- **Empty Changesets**: Support for documentation-only changes
- **Release Artifacts**: Automated SBOM, build artifacts, and attestations

## Consequences

### Positive

- **Quality Documentation**: Forces developers to articulate changes clearly
- **Flexible Control**: Balance between automation and human oversight
- **Rich Changelogs**: GitHub integration provides context and links
- **Team Collaboration**: Multiple developers can contribute to release notes
- **Semantic Versioning**: Proper semver based on actual change impact
- **CI/CD Integration**: Seamless automation with validation
- **Rollback Capability**: Clear version history enables easy rollbacks

### Negative

- **Additional Step**: Developers must remember to add changesets
- **Learning Curve**: Understanding changeset workflow and semver impact
- **Complexity**: More complex than fully automated solutions
- **Validation Overhead**: CI fails if changesets missing for features/fixes

### Mitigation

- **Documentation**: Clear workflow documentation in CLAUDE.md
- **Validation**: CI prevents merging without proper changesets
- **Tooling**: Simple commands (`pnpm changeset`) reduce friction
- **Templates**: Changeset templates guide developers
- **Training**: Team guidance on effective changeset writing
- **Flexibility**: Empty changesets for non-release changes

## References

- [Changesets Documentation](https://github.com/changesets/changesets)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
