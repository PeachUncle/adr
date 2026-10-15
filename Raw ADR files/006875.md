# ADR 010: Semantic Versioning Automation

**Date**: 2025-08-31  
**Status**: Accepted  
**Deciders**: Development Team  

## Context

The project currently uses manual versioning in package.json (v0.1.0) with informal commit messages. This approach is error-prone, time-consuming, and leads to inconsistent version bumps and manual changelog maintenance. We need automated semantic versioning to ensure consistent releases and reduce human error.

## Decision

We will implement **semantic-release** with conventional commits for fully automated versioning and releases.

### Components Installed:
- `semantic-release` (core automation)
- `@semantic-release/changelog` (automatic changelog generation)
- `@semantic-release/git` (git operations for version commits)
- `@commitlint/cli` and `@commitlint/config-conventional` (commit message enforcement)

### Configuration:
- Conventional commit format enforcement via commitlint
- Husky commit-msg hook for validation
- GitHub Actions integration for automated releases
- Automatic changelog generation from commit messages

## Alternatives Considered

### 1. Standard-Version
- **Pros**: Manual control over releases, simpler setup
- **Cons**: Still requires manual intervention, prone to human error
- **Rejected**: Doesn't fully solve automation goals

### 2. GitVersion
- **Pros**: Works with GitFlow, calculates from branch structure
- **Cons**: More complex, requires specific branching strategy
- **Rejected**: Overkill for current simple workflow

### 3. Manual Versioning (Status Quo)
- **Pros**: Full control, simple to understand
- **Cons**: Error-prone, inconsistent, time-consuming
- **Rejected**: Current pain points make this unsustainable

## Consequences

### Positive:
- Zero manual version bump errors
- Consistent changelog generation
- Faster release cycles
- Improved commit message quality
- Automated GitHub releases
- Clear correlation between commit types and version bumps

### Negative:
- Learning curve for conventional commit format
- Less control over release timing
- Requires commit message discipline from all contributors

### Mitigation:
- Commitlint enforcement prevents invalid commits
- Team training on conventional commit format
- Can be disabled/reverted if needed

## Implementation Details

### Commit Types:
- `feat`: New feature (minor version bump)
- `fix`: Bug fix (patch version bump)
- `BREAKING CHANGE`: Breaking change (major version bump)
- `docs`, `style`, `refactor`, `test`, `chore`: No version bump

### Automation Flow:
1. Developer commits with conventional format
2. Commitlint validates commit message
3. On main branch push, semantic-release analyzes commits
4. Version bump determined by commit types
5. Changelog generated from commit messages
6. GitHub release created with release notes
7. Package.json updated with new version

## Success Metrics

- Zero manual versioning errors after implementation
- 100% adherence to conventional commit format
- Automated release creation on every main branch update
- Generated changelogs accurately reflect changes