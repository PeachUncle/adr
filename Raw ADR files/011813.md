# ADR 004: Agent LLM Tooling Selection

## Status

Proposed

## Context

We're building a mobile-first application that enables developers to delegate coding tasks to AI agents directly from their phone. The MVP user flow is:

1. User creates/selects a GitHub issue
2. User instructs the agent via mobile interface
3. Agent creates a branch, writes code, commits changes, and opens a PR

The agent executes within GitHub Actions on Linux runners. We need to select the LLM and tooling the agent will use to understand issues, analyse the codebase, and write code autonomously.

### Requirements

- Must run reliably in GitHub Actions (Linux environment)
- Must handle: reading issues, understanding codebase context, writing code, creating commits
- API keys/credentials will be stored as GitHub secrets
- Minimal custom scaffolding code preferred for MVP
- Should provide agentic coding capabilities out of the box
- Cost is a consideration but not the primary constraint for MVP

### Options Evaluated

#### 1. Claude Code (CLI)

Anthropic's official CLI tool for agentic coding.

**Pros:**
- Purpose-built for agentic coding workflows
- Includes codebase understanding, file editing, and git operations
- Can run in CI/CD environments
- Minimal wrapper code needed
- Strong code generation capabilities
- Built-in tools for reading, searching, and editing files

**Cons:**
- Requires Anthropic API key (cost per token)
- Relatively new tool, less battle-tested than alternatives
- Tied to Anthropic's models

#### 2. Gemini CLI

Google's CLI tool with free tier.

**Pros:**
- Free tier available
- Works in GitHub Actions
- Backed by Google's infrastructure

**Cons:**
- Less mature for agentic coding workflows
- Would require significant scaffolding for file operations, git integration
- Fewer examples of autonomous coding agents using Gemini

#### 3. OpenAI GPT-4 (via API)

Direct API integration with OpenAI models.

**Pros:**
- Well-documented and widely used
- Strong code generation
- Flexible API

**Cons:**
- Requires building entire agent scaffolding (file I/O, git ops, codebase analysis)
- More custom code to maintain
- No built-in agentic coding tools

#### 4. Aider

Open source AI coding assistant supporting multiple LLMs.

**Pros:**
- Open source, actively maintained
- Multi-LLM support (can switch providers)
- Built for coding workflows
- Includes git integration
- Well-tested in coding scenarios

**Cons:**
- Primarily designed for interactive use, not autonomous agents
- May require adaptation for GitHub Actions environment
- Additional configuration for autonomous operation

#### 5. Custom Agent

Build our own agent using LLM APIs directly.

**Pros:**
- Full control over behaviour
- Can optimise for our specific use case

**Cons:**
- Significant development effort
- Need to build: file operations, codebase analysis, git integration, error handling
- Longer time to MVP
- More maintenance burden

## Decision

**We will use Claude Code (CLI) as the LLM tooling for the agent.**

### Rationale

1. **Minimal scaffolding required**: Claude Code is purpose-built for agentic coding. It includes file operations (read, write, edit), codebase search (grep, glob), and can execute bash commands for git operations. This means we can focus on the mobile app and workflow orchestration rather than building agent infrastructure.

2. **CI/CD compatibility**: Claude Code is designed to run in non-interactive environments and can be invoked via CLI in GitHub Actions workflows.

3. **Agentic by design**: Unlike raw LLM APIs or tools designed for interactive use, Claude Code is built for autonomous operation. It can plan multi-step tasks, search codebases, and make decisions about what files to modify.

4. **Faster MVP**: We can have a working agent with minimal wrapper code (essentially just: read issue → invoke Claude Code with context → handle PR creation).

5. **Quality of output**: Claude models (Sonnet 3.5/Opus 4.5) have demonstrated strong performance on coding tasks, and Claude Code's tooling provides good structured output.

### Implementation approach

- Install Claude Code in GitHub Actions runner
- Store Anthropic API key as GitHub secret
- Agent workflow:
  1. Parse issue content
  2. Invoke `claude-code` with issue description as prompt
  3. Let Claude Code handle codebase analysis, file modifications, commits
  4. Create PR from resulting branch

## Consequences

### Positive

- **Rapid MVP development**: Can build working agent quickly with minimal custom code
- **Reliable operations**: File operations, git integration handled by tested tooling
- **Good developer experience**: Claude Code provides clear output about actions taken
- **Maintained tooling**: Anthropic maintains and improves Claude Code

### Negative

- **Vendor lock-in**: Tied to Anthropic's API and pricing
- **Cost**: Pay-per-token model (though cost is acceptable for MVP)
- **Flexibility**: Less control over low-level agent behaviour compared to custom solution

### Risks and mitigations

- **Risk**: Anthropic API outages affect agent availability
  - *Mitigation*: Implement retry logic; consider Aider as backup option (supports multiple LLMs)

- **Risk**: Cost scaling if usage grows significantly
  - *Mitigation*: Monitor usage; architecture designed to allow swapping tooling later if needed

- **Risk**: Claude Code may have limitations we discover during implementation
  - *Mitigation*: Architecture keeps agent tooling loosely coupled; can switch to Aider or custom solution if needed

### Future considerations

- Monitor cost and performance metrics during MVP phase
- Evaluate whether multi-LLM support (via Aider) becomes important
- Consider custom agent if we need specific behaviours Claude Code doesn't support
- Track improvements to Gemini and other alternatives

## Notes

This decision prioritises speed to MVP and leveraging existing tooling over building custom infrastructure. The loose coupling in our architecture means we can revisit this decision based on real-world usage data.
