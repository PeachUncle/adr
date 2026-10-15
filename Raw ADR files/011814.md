# ADR 005: GitHub Integration Authentication

## Status

Proposed

## Context

We are building a mobile-first application that enables developers to delegate coding tasks to AI agents from their mobile devices. The MVP user flow is:

1. User views a GitHub issue on their phone
2. User instructs an agent to work on the issue
3. Agent creates a branch, makes commits, and opens a pull request

The mobile application requires GitHub integration for the following capabilities:
- Reading repository issues
- Triggering GitHub Actions workflow dispatch events
- Reading pull request details and status
- Reading workflow run status

There are three primary authentication approaches to consider:

### Option 1: OAuth App
A traditional OAuth application where users authenticate via GitHub's OAuth flow. The app receives an access token with user-delegated permissions (scopes).

**Pros:**
- Simple implementation for MVP
- Well-documented, mature OAuth 2.0 flow
- User-centric model (actions appear as the user)
- Easy to request and manage scopes
- No installation step required

**Cons:**
- All actions appear as the user, not as a distinct bot identity
- Token has full user permissions for requested scopes across all accessible repos
- Less granular permission control
- Token management is user-specific

### Option 2: GitHub App
An installable GitHub App that acts as a separate bot identity with fine-grained, repository-specific permissions.

**Pros:**
- Distinct bot identity for agent actions
- More granular, repository-level permissions
- Better audit trail (clear distinction between user and bot actions)
- Scalable for multi-user, multi-repo scenarios
- Installation-based trust model

**Cons:**
- More complex setup (installation flow + OAuth flow for user identity)
- Requires webhook endpoint for optimal integration
- Heavier initial development effort
- Users must have admin rights to install on repos

### Option 3: Personal Access Token (PAT)
Users manually generate a PAT with required scopes and provide it to the app.

**Pros:**
- Simplest possible implementation
- No OAuth flow needed
- Useful for development and testing

**Cons:**
- Poor user experience (manual token generation and copying)
- Security concerns (long-lived tokens, manual rotation)
- No standardised revocation flow
- Not suitable for production mobile app

## Key Considerations

### Separation of Concerns
The mobile app's authentication is separate from the agent's authentication:
- **Mobile app**: Needs to read issues, trigger workflows, read PR/workflow status
- **Agent**: Needs to clone repos, commit code, push branches, create PRs (runs in GitHub Actions with `GITHUB_TOKEN` or separate credentials)

### MVP Priorities
- Minimal user friction
- Fast time to value
- Straightforward permission model
- Ability to iterate quickly

### Future Considerations
- Multi-user support
- Clear audit trails
- Bot identity for commits
- Organisational installations

## Decision

**Use OAuth App for MVP, with a clear migration path to GitHub App.**

For the initial release:
1. Implement GitHub OAuth App authentication
2. Request the following scopes:
   - `repo` (full repository access - includes issues, PRs, code)
   - `workflow` (trigger and read workflow runs)
3. Store OAuth tokens securely on the mobile device
4. Design the backend API to abstract authentication, enabling future auth method changes without client modifications

The agent's authentication in GitHub Actions will use the default `GITHUB_TOKEN` provided by Actions, which has automatic permissions for:
- Creating branches
- Committing code
- Opening pull requests
- Running within the workflow context

## Consequences

### Positive
- **Rapid MVP delivery**: OAuth flow is straightforward to implement and well-documented
- **Low user friction**: Single sign-in, no installation required
- **Familiar UX**: Standard OAuth pattern users understand
- **Sufficient for MVP**: All required permissions available via OAuth scopes
- **Clear separation**: Mobile app auth (OAuth) vs agent auth (GitHub Actions token)

### Negative
- **User identity for all actions**: Actions from the mobile app appear as the user, not a bot
- **Broader permissions**: `repo` scope grants access to code, not just issues/PRs (though necessary for triggering workflows)
- **Migration cost**: Moving to GitHub App later will require engineering effort

### Neutral
- **Agent commits**: Will appear as the workflow bot (using `GITHUB_TOKEN`) or can be configured with a bot user account if desired
- **Token management**: OAuth refresh tokens must be implemented for long-lived sessions

### Migration Path to GitHub App

When ready to transition (post-MVP):
1. Create a GitHub App with equivalent permissions
2. Implement installation flow alongside OAuth
3. Maintain backwards compatibility during migration period
4. Gradually migrate users to GitHub App authentication
5. Leverage GitHub App's bot identity for clearer audit trails
6. Retire OAuth App once migration is complete

The backend API should be designed with this migration in mind, using an abstraction layer that doesn't leak OAuth-specific details to clients.

## Related Decisions

- ADR TBD: Backend authentication token storage
- ADR TBD: GitHub Actions workflow design for agent execution
- ADR TBD: Bot identity management for commits

## References

- [GitHub OAuth Apps Documentation](https://docs.github.com/en/apps/oauth-apps)
- [GitHub Apps Documentation](https://docs.github.com/en/apps/creating-github-apps)
- [GitHub Actions GITHUB_TOKEN Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
