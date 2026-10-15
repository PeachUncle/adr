---
status: 'accepted'
date: 2025-09-10
decision-makers: voder.ai website team
consulted: DevOps Research and Assessment (DORA) practices
informed: development team, CI/CD stakeholders
---

# ADR 0024: Adopt DORA-style Trunk-based Development

## Context and Problem Statement

As we scale our development practices, we need to establish a branching strategy that supports high-velocity software delivery while maintaining code quality and stability. The DevOps Research and Assessment (DORA) research consistently shows that elite performing teams use trunk-based development to achieve faster delivery and better outcomes.

We need to decide on a development workflow that enables:

- Fast integration and feedback cycles
- Reduced merge conflicts and integration overhead
- High deployment frequency with low change failure rates
- Quick recovery from failures

## Decision Drivers

- **DORA Metrics Optimization**: Need to optimize for deployment frequency, lead time, and change failure rate
- **Continuous Integration**: Require frequent integration to catch issues early
- **Team Collaboration**: Enable smooth collaboration without long-lived feature branches
- **Quality Assurance**: Maintain code quality through automated verification
- **Risk Mitigation**: Reduce integration risks and merge conflicts
- **Developer Experience**: Provide fast feedback and smooth development flow

## Considered Options

- **Trunk-based Development (DORA-style)**: All developers work on main branch with short-lived feature branches
- **GitFlow**: Feature branches, develop branch, release branches, hotfix branches
- **GitHub Flow**: Feature branches with pull requests, no develop branch
- **Release Flow**: Feature branches with regular releases from main

## Decision Outcome

Chosen option: "Trunk-based Development (DORA-style)", because it aligns with DORA research findings for high-performing teams and supports our goals of fast delivery with quality.

### Implementation Details

- **Main Branch**: Single source of truth, always deployable
- **Feature Branches**: Short-lived (max 1-2 days), small changes only
- **Integration Frequency**: Multiple commits per day to main branch
- **Automated Verification**: All changes must pass automated tests and quality checks
- **Feature Flags**: Use feature toggles for incomplete features rather than long branches
- **Direct Commits**: Allow direct commits to main for small, verified changes

### Consequences

- Good, because reduces integration overhead and merge conflicts
- Good, because enables faster feedback cycles and deployment frequency
- Good, because aligns with DORA best practices for elite performing teams
- Good, because simplifies branching model and reduces cognitive overhead
- Good, because supports continuous delivery and deployment practices
- Bad, because requires discipline in maintaining main branch stability
- Bad, because may require cultural shift for teams used to long-lived branches
- Bad, because requires robust automated testing and verification

### Confirmation

Implementation compliance will be confirmed through:

- **Branch Protection Rules**: Main branch requires status checks and up-to-date branches
- **Automated Verification**: All changes must pass `npm run verify` before merge
- **Integration Frequency Monitoring**: Track average branch lifespan (target: <2 days)
- **DORA Metrics**: Monitor deployment frequency and lead time improvements
- **Code Review Process**: Ensure changes are small, focused, and quickly reviewable

## Pros and Cons of the Options

### Trunk-based Development (DORA-style)

Elite performing teams practice from DORA State of DevOps reports.

- Good, because proven to correlate with high performance in DORA research
- Good, because reduces integration complexity and merge conflicts
- Good, because enables fast feedback and continuous integration
- Good, because supports high deployment frequency
- Good, because simplifies mental model of branching
- Neutral, because requires cultural adjustment for teams new to the practice
- Bad, because requires discipline in maintaining main branch quality
- Bad, because needs robust automated testing infrastructure

### GitFlow

Traditional branching model with multiple long-lived branches.

- Good, because provides clear separation of concerns
- Good, because familiar to many developers
- Neutral, because supports structured release process
- Bad, because creates integration bottlenecks and merge conflicts
- Bad, because increases lead time for changes
- Bad, because contradicts DORA findings for high-performing teams

### GitHub Flow

Simple feature branch workflow with pull requests.

- Good, because simpler than GitFlow
- Good, because GitHub native workflow
- Neutral, because allows for controlled integration
- Bad, because can encourage longer-lived feature branches
- Bad, because may slow down integration frequency
- Bad, because doesn't align with DORA trunk-based recommendations

### Release Flow

Microsoft's branching strategy with regular releases.

- Good, because supports regular release cadence
- Good, because balances simplicity with control
- Neutral, because provides structured release process
- Bad, because still uses feature branches that can become long-lived
- Bad, because doesn't fully embrace trunk-based development benefits
- Bad, because adds complexity compared to pure trunk-based approach

## More Information

- [DORA State of DevOps Reports](https://dora.dev/research/)
- [Trunk-based Development Guide](https://trunkbaseddevelopment.com/)
- [Google's trunk-based development practices](https://cloud.google.com/architecture/devops/devops-tech-trunk-based-development)
- Repository branch protection rules enforce automated verification requirements
- Feature flag implementation will be addressed in future architectural decisions
