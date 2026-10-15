# ADR 026: Local Agent Runner First, Netlify Function Second

## Status

**Superseded** – 2025-10-11

**Replaced by**: [ADR-027](027-self-contained-agent-functions.md) (Self-Contained Agent Functions) and [ADR-028](028-choice-of-custom-yaml-over-openai-agents-sdk.md) (Custom YAML Over OpenAI Agents SDK)

**Note**: This ADR described an approach using `@openai/agents` SDK, which we later evaluated and rejected. See ADR-028 for why we chose a custom YAML workflow engine instead.

## Context

- We are migrating the quote intake flow to OpenAI AgentKit / ChatKit.
- The current backend implementation attempts to import `createAgentRunner` from `@openai/agents`, but that helper is not exposed in the public SDK we can ship to Netlify. This breaks local dev and would fail continuous deployment.
- The YAML definition (`agents/quote-agent.yaml`) should remain the single source of the agent workflow so Product and Prompt teams can iterate there.
- We must unblock local development before wiring the serverless Netlify function, so that we can test the UI end-to-end and avoid broken production deploys.

## Decision

1. **Implement the agent runner locally first**
   - Build a dedicated module that:
     - Reads `agents/quote-agent.yaml`.
     - Constructs an `Agent` / `Runner` using the public `@openai/agents` API instead of the unavailable `createAgentRunner`.
     - Exposes the same staged responses (`stage`, `summary`, etc.) the frontend expects.
   - Wire Express (`/api/agents/quote/run`) to that module for local development.
   - Keep this implementation vanilla Node (no Netlify-specific constraints) so it runs under `npm run dev`.

2. **Once the local runner is stable, adapt it for Netlify**
   - Reuse the same module inside `packages/backend/netlify/functions/quote-agent.mjs`.
   - Ensure any filesystem reads (YAML) and environment variables are compatible with Netlify’s function runtime (read during cold start, cached between invocations).
   - Feature-flag the frontend endpoint to hit the serverless function only when deployed.

3. **Maintain the YAML as the single source of truth**
   - Do not hardcode the workflow steps in JS/TS; continue to parse the YAML to keep parity with Agent Builder.
   - Add unit tests around the parser/runner to guard against regressions.

## Consequences

- Local development gets unblocked before any deployment changes, letting us validate the ChatKit UI and Supabase integrations safely.
- The Netlify function implementation becomes a thin wrapper around the same runner, reducing drift between dev and prod.
- We incur a one-time cost to write the runner assembly code, but we avoid depending on unpublished SDK internals.
