# ADR 001: Agent Execution Model

## Status

Proposed

## Context

We are building a mobile-first application that enables developers to delegate coding tasks to AI agents directly from their phone. The MVP user flow is:

1. User creates or selects a GitHub issue
2. User instructs an AI agent with task details via mobile app
3. Agent creates a branch, makes commits, and opens a pull request
4. User reviews the PR on mobile or desktop

This requires making a fundamental architectural decision about where and how the AI coding agent executes its work. We have identified three primary approaches:

### Option 1: GitHub Actions-based execution
The agent runs as a GitHub Actions workflow directly in the user's repository. The mobile app triggers the workflow via GitHub API, and the agent operates with the repository's existing permissions and infrastructure.

### Option 2: Hosted agent service
We operate dedicated infrastructure (VMs, containers, Kubernetes) that runs the agent execution environment. The service clones repositories, performs work, and pushes changes back using GitHub App credentials or PATs.

### Option 3: Hybrid approach
A lightweight planning/orchestration component runs in GitHub Actions, whilst computationally expensive operations (LLM inference, complex analysis) run on our hosted infrastructure.

### Key constraints for MVP

- **Minimal infrastructure overhead**: We want to focus on product validation, not infrastructure management
- **Repository access**: The agent requires write permissions (branches, commits, PR creation)
- **Mobile triggerability**: Must be reliably triggered from a mobile application
- **Fast iteration**: Architecture should not impede rapid experimentation and feature development
- **Cost efficiency**: MVP budget is limited; avoid unnecessary compute costs

### Trade-offs analysis

**GitHub Actions approach:**
- ✅ Zero infrastructure to manage
- ✅ Native GitHub permissions model (GITHUB_TOKEN)
- ✅ Built-in secrets management
- ✅ Easy to trigger via GitHub API
- ✅ Users can inspect workflow runs
- ✅ No cold start issues (GitHub handles scheduling)
- ❌ Limited to 6 hours per job
- ❌ Less control over execution environment
- ❌ Costs may scale with Actions minutes usage
- ❌ Debugging requires understanding Actions logs

**Hosted service approach:**
- ✅ Full control over execution environment
- ✅ Predictable performance and timeouts
- ✅ Can optimise for cost (spot instances, etc.)
- ❌ Significant infrastructure complexity
- ❌ Must manage authentication/authorisation
- ❌ Requires secure repository cloning mechanism
- ❌ Need to handle secrets management
- ❌ Cold start latency for scaling
- ❌ More attack surface to secure

**Hybrid approach:**
- ✅ Can optimise costs for expensive operations
- ✅ Maintains some GitHub-native benefits
- ❌ Complexity of managing both systems
- ❌ Network latency between components
- ❌ Authentication between Actions and hosted service
- ❌ Premature optimisation for MVP

## Decision

We will implement a **GitHub Actions-based execution model** for the MVP.

The agent will run as a GitHub Actions workflow that:
- Is triggered via the GitHub Actions API from our mobile backend
- Receives task instructions as workflow inputs
- Uses `GITHUB_TOKEN` for repository operations
- Creates branches, commits, and pull requests directly
- Logs execution details to the Actions run interface

The mobile app backend will:
- Authenticate users via GitHub OAuth
- Ensure the workflow file exists in target repositories (or provide setup instructions)
- Trigger workflows via GitHub REST API
- Poll or use webhooks to monitor workflow completion
- Present results to the mobile app

## Consequences

### Positive

**Faster MVP delivery**: No infrastructure to build, deploy, or maintain. We can focus entirely on the mobile UX and agent logic.

**Built-in security**: GitHub's permission model handles authentication and authorisation. The `GITHUB_TOKEN` automatically has appropriate repository access without managing credentials.

**User transparency**: Developers can inspect workflow runs directly in GitHub, providing natural debugging and audit trails.

**Cost predictability**: For small-scale MVP usage, GitHub Actions free tier (2,000 minutes/month for free accounts, 3,000 for Pro) may cover testing. Costs scale with actual usage.

**Familiar debugging**: Developers understand GitHub Actions logs; no need to expose or build custom logging infrastructure.

**Easy repository setup**: Users only need to commit a workflow YAML file to `.github/workflows/` to enable the feature.

### Negative

**Execution time limits**: GitHub Actions jobs are limited to 6 hours. If agents require longer execution times for complex tasks, we'll need to implement chunking or migrate.

**Actions minutes costs**: Heavy usage will incur GitHub Actions minutes charges. For organisations with limited Actions minutes, this could be prohibitive.

**Limited environment control**: We cannot fully customise the execution environment (though we can use Docker actions if needed). This may constrain agent capabilities.

**Dependency on GitHub**: Tightly coupled to GitHub's platform. Supporting GitLab, Bitbucket, or other platforms would require significant rework.

**Cold start variability**: GitHub Actions runner provisioning time varies (typically 10-30 seconds but can be longer). This affects perceived responsiveness.

**Debugging complexity**: When things go wrong, users must understand Actions logs, which may be intimidating for some developers.

**Rate limiting**: GitHub API rate limits apply to workflow triggers. High-frequency usage patterns may require careful management.

### Mitigation strategies

- **Time limits**: Design agents to checkpoint progress and provide partial results if approaching timeout
- **Cost management**: Monitor Actions minutes usage; provide users with visibility into their consumption
- **Platform lock-in**: Keep agent logic abstracted from GitHub-specific APIs where possible to ease future migration
- **Rate limits**: Implement intelligent queuing and backoff strategies in the mobile backend

### Future evolution

This decision is explicitly scoped to the MVP. As we validate product-market fit, we can reassess:

- If Actions costs become prohibitive, migrate to hosted infrastructure
- If execution time limits are hit frequently, implement hybrid model
- If multi-platform support is needed, abstract execution layer

The GitHub Actions approach minimises risk and maximises learning velocity for the MVP phase.
