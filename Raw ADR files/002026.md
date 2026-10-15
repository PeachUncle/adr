# ADR-0005: Adopt Semantic Versioning

## Status

Accepted

## Context

Grafana-banana needs a clear, consistent versioning strategy for releases to:

- Communicate the nature of changes to users
- Signal breaking changes vs. backward-compatible changes
- Enable automated release processes
- Support dependency management
- Provide predictable upgrade paths
- Align with industry standards
- Support both manual and automated releases

The versioning system must be:
- Easy to understand for users and developers
- Automatable in CI/CD pipelines
- Compatible with package managers and container registries
- Industry-standard and widely recognized

## Decision

We will adopt Semantic Versioning (SemVer) 2.0.0 for all releases of Grafana-banana.

### Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

Examples:
- `1.0.0` - Initial stable release
- `1.2.3` - Minor feature update with patches
- `2.0.0` - Breaking changes
- `1.0.0-alpha.1` - Pre-release version
- `1.0.0+20231025` - Build metadata

### Versioning Rules

1. **MAJOR** version (X.0.0): Incremented when making incompatible API changes
   - Breaking changes to REST API
   - Removal of features or endpoints
   - Changes requiring migration steps
   - Major architectural changes affecting consumers

2. **MINOR** version (0.X.0): Incremented when adding functionality in a backward-compatible manner
   - New API endpoints
   - New features
   - Significant enhancements
   - Deprecations (with continued support)

3. **PATCH** version (0.0.X): Incremented when making backward-compatible bug fixes
   - Bug fixes
   - Security patches
   - Performance improvements
   - Documentation updates

4. **Pre-release** versions (0.0.0-LABEL): Used for alpha, beta, and release candidates
   - `alpha`: Early testing, unstable
   - `beta`: Feature complete, testing
   - `rc`: Release candidate, final testing

5. **Build metadata** (+BUILD): Optional, for build information

### Version Lifecycle

- **0.X.Y**: Initial development, public API not stable
- **1.0.0**: First stable release with public API
- **X.Y.Z**: Stable releases following SemVer rules

## Consequences

### Positive

1. **Clarity**: Users immediately understand impact of updates
2. **Industry Standard**: Widely recognized and understood
3. **Automation-Friendly**: Easy to automate version bumps
4. **Dependency Management**: Compatible with package managers
5. **Communication**: Clear signal of breaking changes
6. **Predictability**: Users know what to expect from updates
7. **Tooling Support**: Excellent tool support (npm, NuGet, Docker, etc.)
8. **Documentation**: Well-documented standard
9. **Git Tag Integration**: Works seamlessly with Git tags
10. **Release Planning**: Helps plan and communicate release content

### Negative

1. **Requires Discipline**: Team must follow rules consistently
2. **Judgment Calls**: Sometimes unclear what constitutes breaking change
3. **Version Inflation**: Strict rules can lead to large version numbers
4. **Pre-1.0 Ambiguity**: 0.X versions have different stability guarantees
5. **Human Error**: Risk of incorrect version bumps
6. **Coordination**: Team must agree on version impacts

### Neutral

1. **Starting Point**: Beginning at 0.X or 1.0 requires decision
2. **Breaking Changes**: Need clear definition of "breaking"
3. **Deprecation Policy**: Need companion deprecation strategy
4. **Calendar vs. SemVer**: Cannot use calendar versioning

## Implementation

### Timeline
- Adoption: Immediate
- Current version: 0.X.Y (pre-1.0 development)
- Target 1.0.0: When API is stable and production-ready

### Owner
@markcoleman

### Dependencies
- Git tags for version marking
- CI/CD workflows updated for SemVer
- Release notes template aligned with SemVer
- CHANGELOG format supporting SemVer sections

### Version Management

#### Automated Versioning
For automatic releases (push to main):
```yaml
# .github/workflows/publish-release.yml
- uses: mathieudutour/github-tag-action@v6.1
  with:
    default_bump: minor  # Default increment
    release_branches: main
```

#### Manual Versioning
For manual releases:
```bash
# Create and push tag
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3
```

#### Conventional Commits Integration

We use Conventional Commits to automate version bumps:

- `feat:` → MINOR bump (new feature)
- `fix:` → PATCH bump (bug fix)
- `BREAKING CHANGE:` → MAJOR bump (breaking change)
- `docs:`, `chore:`, etc. → No version bump (unless include fixes/features)

Examples:
```
feat: add user authentication
fix: resolve memory leak in API
feat!: change API response format
BREAKING CHANGE: remove deprecated endpoint
```

### Release Process

1. **Prepare Release**
   - Update CHANGELOG.md
   - Review version increment
   - Ensure tests pass

2. **Create Release**
   - Tag version in Git
   - GitHub Actions automatically builds and publishes
   - Docker images tagged with version and `latest`
   - GitHub Release created with notes

3. **Post-Release**
   - Verify published artifacts
   - Update documentation if needed
   - Announce release

### Breaking Change Policy

Breaking changes must include:
1. **Deprecation Notice**: One minor version advance warning (if possible)
2. **Migration Guide**: Clear documentation on how to upgrade
3. **CHANGELOG Entry**: Explicitly marked as breaking
4. **MAJOR Version Bump**: Increment major version
5. **Announcement**: Communicate through appropriate channels

Example:
```
# Version 1.5.0
- DEPRECATED: `/old-endpoint` will be removed in 2.0.0
- Use `/new-endpoint` instead

# Version 2.0.0
- BREAKING: Removed `/old-endpoint` (use `/new-endpoint`)
```

## Alternatives Considered

### Alternative 1: Calendar Versioning (CalVer)

**Format:** `YYYY.MM.DD` or `YYYY.MM.MICRO`

**Pros:**
- Immediate indication of release date
- Simple, no judgment about change type
- Works well for time-based releases
- Used by Ubuntu, PyCharm

**Cons:**
- Doesn't communicate impact of changes
- No signal for breaking changes
- Not compatible with semantic dependency resolution
- Less suitable for libraries/APIs
- Requires date-based release schedule

**Why Rejected:**
Doesn't communicate the nature of changes, which is crucial for API consumers. SemVer better signals breaking vs. non-breaking changes.

### Alternative 2: Simple Sequential Versioning

**Format:** `1`, `2`, `3`, etc.

**Pros:**
- Extremely simple
- No confusion about what increments
- Used by some browser versions

**Cons:**
- Provides no information about changes
- No minor/patch distinction
- Difficult for dependency management
- Not industry standard
- No automation support

**Why Rejected:**
Too simplistic, provides no useful information about the nature of changes. Not suitable for API versioning.

### Alternative 3: Date-Based with Revision

**Format:** `YYYY.MM.REV`

**Pros:**
- Combines date and sequential info
- Clear chronological ordering
- Multiple releases per month possible

**Cons:**
- Still doesn't communicate change impact
- More complex than pure CalVer
- Less standard
- Not semantic

**Why Rejected:**
Combines disadvantages of both CalVer and sequential versioning without SemVer's benefits.

### Alternative 4: Marketing Versions

**Format:** Named releases (e.g., "Panther", "Tiger", "Leopard")

**Pros:**
- Memorable
- Good for marketing
- Used by macOS, Android

**Cons:**
- No programmatic meaning
- Can't automate
- Confusing for dependencies
- Requires separate technical version
- Not professional for business software

**Why Rejected:**
Impractical for technical dependency management. Could be used alongside SemVer for marketing but not as primary version.

### Alternative 5: Year.Major.Minor

**Format:** `2025.1.0`

**Pros:**
- Includes year for context
- Maintains major/minor
- Somewhat semantic

**Cons:**
- Non-standard
- Confusing (is year major version?)
- Doesn't follow SemVer conventions
- Poor tool support
- Ambiguous semantics

**Why Rejected:**
Attempts to combine calendar and semantic versioning poorly. Standard SemVer is clearer.

### Alternative 6: No Versioning (Continuous Delivery)

**Approach:** Use commit SHAs or timestamps, continuous deployment

**Pros:**
- No version management overhead
- Truly continuous delivery
- Every commit potentially deployed

**Cons:**
- Hard to communicate specific releases
- Difficult for users to track versions
- No stable reference points
- Poor for dependency management
- Unsuitable for distributed software

**Why Rejected:**
Not appropriate for software distributed to users or used as a dependency. Need stable reference points.

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [npm Semantic Versioning](https://docs.npmjs.com/about-semantic-versioning)
- [NuGet Versioning](https://learn.microsoft.com/en-us/nuget/concepts/package-versioning)
- [Project CHANGELOG](../../CHANGELOG.md)
- [Project Repository](https://github.com/markcoleman/Grafana-banana)

## Related ADRs

- [ADR-0004: Use GitHub Actions for CI/CD](./ADR-0004-github-actions-cicd.md)

## Metadata

| Field | Value |
|-------|-------|
| **Created** | 2025-10-25 |
| **Updated** | 2025-10-25 |
| **Author** | @markcoleman |
| **Reviewers** | Architecture Review Board |
| **Status** | Accepted |
| **Implementation Status** | Complete |
