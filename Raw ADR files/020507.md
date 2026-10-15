# ADR 0003: Semantic Versioning Strategy and Conventional Commits

**Status**: Accepted  
**Date**: 2026-01-05  
**Context**: Feature 003 - Automated Binary Release Pipeline  
**Related**: [spec.md](../../specs/003-automated-release-pipeline/spec.md), [research.md](../../specs/003-automated-release-pipeline/research.md)

## Context

To automate the release process, we need a consistent versioning strategy that:

1. Automatically determines the next version number based on commit history
2. Follows industry-standard semantic versioning principles
3. Communicates breaking changes, new features, and bug fixes clearly
4. Integrates seamlessly with GitHub Actions workflows

## Decision

### Semantic Versioning 2.0.0

We will follow **Semantic Versioning 2.0.0** with the format: **MAJOR.MINOR.PATCH**

**Example**: `v1.2.3` where:

- `MAJOR` (1): Incompatible API changes (breaking changes)
- `MINOR` (2): New features (backward-compatible)
- `PATCH` (3): Bug fixes (backward-compatible)

### Conventional Commits 1.0.0

All commit messages MUST follow **Conventional Commits 1.0.0** specification.

**Format**: `<type>: <subject>`

**Supported Types**:

- `feat:` - New feature (triggers MINOR version bump)
- `fix:` - Bug fix (triggers PATCH version bump)
- `BREAKING CHANGE:` - Breaking change footer (triggers MAJOR version bump)
- `docs:` - Documentation only (no version bump)
- `style:` - Code style/formatting (no version bump)
- `refactor:` - Code refactoring (no version bump)
- `test:` - Test changes (no version bump)
- `chore:` - Build/tool changes (no version bump)

### Version Bump Rules

| Commit Type                                       | Version Bump | Example Transition  |
| ------------------------------------------------- | ------------ | ------------------- |
| `BREAKING CHANGE:` in commit body/footer          | MAJOR        | `v0.5.2` → `v1.0.0` |
| `feat:` in commit subject                         | MINOR        | `v0.5.2` → `v0.6.0` |
| `fix:` in commit subject                          | PATCH        | `v0.5.2` → `v0.5.3` |
| `docs:`, `style:`, `refactor:`, `test:`, `chore:` | None         | No release          |

### Implementation Tool

**Tool**: `paulhatch/semantic-version` GitHub Action (v5.4.0)

**Rationale**:

1. **Mature**: 1,000+ stars, actively maintained, widely used
2. **Configurable**: Supports custom patterns for MAJOR/MINOR/PATCH detection
3. **Commit History Parsing**: Analyzes all commits since last tag
4. **Git-Native**: No external dependencies, works with standard Git tags
5. **Deterministic**: Same commits → same version calculation
6. **GitHub Actions Native**: Seamless integration with workflows

**Configuration**:

```yaml
- name: Calculate next version
  uses: paulhatch/semantic-version@a8f8f59fd7f0625188492e945240f12d7ad2dca3 # v5.4.0
  with:
    tag_prefix: "v"
    major_pattern: "(BREAKING CHANGE:|BREAKING:)"
    minor_pattern: "feat:"
    version_format: "v${major}.${minor}.${patch}"
    bump_each_commit: false
    search_commit_body: true
```

### Git Tag Format

- **Tag Prefix**: `v` (e.g., `v1.2.3`)
- **GitHub Release Name**: Same as tag (e.g., `v1.2.3`)
- **Binary File Names**: Include version (e.g., `wt-v1.2.3-linux-x64`)

### Initial Version

- **First Release**: `v0.1.0` (pre-stable)
- **Stable Release**: `v1.0.0` (production-ready)

## Alternatives Considered

### Alternative 1: Manual Versioning

**Approach**: Developers manually specify version in `VERSION` file or `package.json`

**Pros**:

- Full control over version numbers
- No dependency on commit message format

**Cons**:

- Error-prone (developers forget to update version)
- Merge conflicts on version files
- No automated validation
- Inconsistent versioning across team

**Rejected**: Does not meet automation requirements (FR-006).

### Alternative 2: semantic-release (Node.js)

**Approach**: Use `semantic-release` NPM package

**Pros**:

- Industry standard for Node.js projects
- Rich plugin ecosystem
- Automatic changelog generation

**Cons**:

- Requires Node.js runtime (adds dependency to .NET project)
- Complex configuration (`.releaserc` file)
- Slower execution (npm install + semantic-release run)
- Overkill for simple version calculation

**Rejected**: Adds unnecessary runtime dependency and complexity.

### Alternative 3: Custom Bash Script

**Approach**: Write custom script to parse commits and calculate version

**Pros**:

- No external dependencies
- Full control over logic

**Cons**:

- Maintenance burden (testing, edge cases)
- Reinventing the wheel
- Potential for bugs in version calculation

**Rejected**: GitHub Action provides tested, proven solution.

## Consequences

### Positive

- **Automation**: Version numbers calculated automatically from commit history
- **Consistency**: All team members follow the same versioning rules
- **Clarity**: Commit messages clearly communicate the type of change
- **Predictability**: Users can understand version impact (MAJOR = breaking, MINOR = features, PATCH = fixes)
- **Traceability**: Version history is traceable through Git tags and commit messages

### Negative

- **Learning Curve**: Developers must learn Conventional Commits format
- **Strict Discipline**: Invalid commit messages block automated versioning
- **Merge Commits**: Squash-and-merge strategy recommended to maintain clean commit history
- **No Version Downgrade**: Cannot manually decrease version number (only forward)

### Migration Strategy

For existing projects without Conventional Commits:

1. **Start Fresh**: First release with new pipeline is `v0.1.0`
2. **Prefix Requirement**: All new commits must follow Conventional Commits
3. **Git Hooks**: Add `commitlint` to validate commit messages locally
4. **Documentation**: Provide team training on Conventional Commits

## Enforcement

### Pre-Commit Hook (Optional)

```bash
# .git/hooks/commit-msg
#!/bin/sh
npx --no-install commitlint --edit "$1"
```

### Pull Request Validation

GitHub Actions workflow validates commit messages:

```yaml
- name: Validate commit messages
  run: |
    git log origin/main..HEAD --pretty=format:%s | \
      grep -Ev '^(feat|fix|docs|style|refactor|test|chore|BREAKING CHANGE):' && \
      { echo "Invalid commit messages found!"; exit 1; } || echo "All commits valid"
```

## Examples

### Example 1: Feature Addition (MINOR bump)

```bash
git commit -m "feat: add support for multiple worktrees"
# v0.5.2 → v0.6.0
```

### Example 2: Bug Fix (PATCH bump)

```bash
git commit -m "fix: handle special characters in branch names"
# v0.5.2 → v0.5.3
```

### Example 3: Breaking Change (MAJOR bump)

```bash
git commit -m "feat: change CLI argument format

BREAKING CHANGE: All CLI arguments now use kebab-case instead of camelCase.
Migration guide: docs/migration/v2.0.md"
# v0.5.2 → v1.0.0
```

### Example 4: Documentation (No bump)

```bash
git commit -m "docs: update installation guide"
# v0.5.2 → v0.5.2 (no release)
```

## Documentation

- **Team Guide**: [docs/ja/CONVENTIONAL_COMMITS.md](../ja/CONVENTIONAL_COMMITS.md)
- **User Guide**: [specs/003-automated-release-pipeline/quickstart.md](../../specs/003-automated-release-pipeline/quickstart.md)
- **Enforcement**: Documented in `.github/CONTRIBUTING.md`

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/)
- [paulhatch/semantic-version GitHub Action](https://github.com/PaulHatch/semantic-version)
- [commitlint](https://commitlint.js.org/)

## Review Schedule

This ADR should be reviewed:

- Before major version 1.0.0 release
- If versioning strategy proves too restrictive or too lenient
- If Conventional Commits 2.0 is released
- Annually as part of architecture review
