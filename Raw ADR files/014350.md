# 11. GitHub Flow with Linear Integration

Date: 2025-09-12

## Status

Accepted

## Context

The portfolio development team needs an efficient workflow that integrates:

- Project management and issue tracking
- Version control and code collaboration
- CI/CD pipeline automation
- Traceability from requirements to deployment
- Team coordination and communication

The team requires:

- Clear branching strategy for feature development
- Integration between project management and code
- Automated workflows that reduce manual overhead
- Traceability for compliance and debugging
- Seamless developer experience

## Decision

Implement GitHub Flow with Linear integration:

- **GitHub Flow** branching strategy with feature branches from main
- **Linear ticket integration** with branch naming convention `PORT-{number}-{description}`
- **Conventional commits** for automated semantic versioning
- **Automatic linking** between branches, PRs, and Linear tickets
- **Status updates** that sync between GitHub and Linear

## Consequences

### Positive

- **Seamless integration**: Project management and code are tightly integrated
- **Complete traceability**: Full audit trail from ticket to deployment
- **Automated workflows**: Reduces manual overhead and human error
- **Clear communication**: Team always knows what work is being done
- **Efficient collaboration**: Easy to understand context and dependencies

### Negative

- **Learning curve**: Team needs to understand both GitHub and Linear
- **Naming discipline**: Requires strict adherence to branch naming conventions
- **Tool dependency**: Reliance on both GitHub and Linear working together
- **Configuration complexity**: More complex setup and maintenance
- **Cost**: Two separate service subscriptions

### Risks

- **Integration failures**: Linear or GitHub API changes could break integration
- **Naming mistakes**: Incorrect branch names break automatic linking
- **Vendor lock-in**: Dependency on both GitHub and Linear
- **Data synchronization**: Keeping ticket and PR status in sync
- **Team adoption**: Requires team discipline to follow conventions
