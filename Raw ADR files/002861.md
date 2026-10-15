# ADR-005: Trunk-Based Development with Feature Flags

## Status

Accepted

## Context

We need a branching and release strategy that:

- Supports continuous delivery
- Minimizes merge conflicts
- Enables safe deployment of incomplete features
- Allows instant rollback without code changes
- Scales with team size

## Decision

We adopt **Trunk-Based Development** with **LaunchDarkly feature flags**.

### Branching Model

- **Single trunk**: `main` is the only long-lived branch
- **Short-lived branches**: Feature branches live 1-3 days max
- **Squash merge**: All PRs squash into single commits
- **No release branches**: Releases are controlled by flags, not branches

### Feature Flags (LaunchDarkly)

- All incomplete features are wrapped in flags
- Flags decouple deployment from release
- Gradual rollout: internal → beta → canary → GA
- Instant rollback by toggling flag off

### Alternatives Considered

| Strategy        | Pros                           | Cons                            | Decision               |
| --------------- | ------------------------------ | ------------------------------- | ---------------------- |
| **GitFlow**     | Clear release process          | Long-lived branches, merge hell | Rejected               |
| **GitHub Flow** | Simple                         | No flag-based releases          | Partial (we extend it) |
| **Trunk-Based** | Fast integration, CI/CD native | Requires discipline, flags      | **Accepted**           |

### Why LaunchDarkly?

| Alternative       | Pros                           | Cons                   | Decision     |
| ----------------- | ------------------------------ | ---------------------- | ------------ |
| **LaunchDarkly**  | Full-featured, SDKs, targeting | Cost                   | **Accepted** |
| **Unleash**       | Open source                    | Self-hosted complexity | Rejected     |
| **Custom flags**  | Free                           | Maintenance burden     | Rejected     |
| **AWS AppConfig** | AWS-native                     | Limited targeting      | Rejected     |

## Consequences

### Positive

- Merge conflicts are rare (branches are short-lived)
- Main is always deployable
- Features can be released to specific users first
- Instant rollback without deployment
- Encourages small, incremental changes

### Negative

- Requires discipline to keep branches short
- Feature flags add code complexity
- Flag cleanup is ongoing maintenance
- LaunchDarkly has a cost

### Mitigations

- Enforce branch age limits in CI (warn > 2 days, block > 5 days)
- Quarterly flag cleanup sprints
- Document flag lifecycle and naming conventions
- Budget for LaunchDarkly as core infrastructure
