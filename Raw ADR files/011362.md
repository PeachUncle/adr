# ADR-0017: Switch Default LLM to Llama 3 via Ollama

**Status:** Proposed

**Date:** 2025-10-16

**Deciders:** Core team

**Tags:** architecture, llm, performance, cost

---

## Context

Recent regression and integration tests have been exceeding OpenAI rate limits, delaying feedback
cycles and blocking local development. The current default configuration selects OpenAI's
`gpt-4o-mini`, which requires a cloud API key and consumes quota during automated test runs. This
conflicts with our quality gates that mandate running the full suite (tests, lint, security, docs)
before every commit.

Project requirements:

- Deterministic, always-available LLM for CI and local testing
- Zero incremental cost for repeated suite executions
- Configurable pathway for higher-quality hosted models when explicitly requested
- Alignment with OWASP LLM Top 10 guidance to prefer self-hosted models when feasible for sensitive data (LLM01, LLM05) ([OWASP 2025](https://genai.owasp.org/))

Ollama provides an OpenAI-compatible local API and ships `llama3.2:3b`, which we already use for golden tests. Switching the default to this local model resolves quota pressure while keeping summarization functional out of the box.

## Decision

We will make `ollama` the default summarizer provider and `llama3.2:3b` the default model. Configuration remains fully overridable via environment variables or YAML, allowing teams to opt into OpenAI or other providers when desired.

## Alternatives Considered

### Alternative 1: Keep OpenAI `gpt-4o-mini` Default

- **Description:** Maintain the existing default while documenting how to switch locally.
- **Pros:** Higher summary quality; no documentation updates required.
- **Cons:** Continues to hit OpenAI limits during CI; forces developers to provision keys; incurs recurring cost.
- **Reason for rejection:** Does not unblock automated quality gates or reduce cost.

### Alternative 2: Introduce Dynamic Provider Selection

- **Description:** Auto-detect availability of local Ollama; fall back to OpenAI otherwise.
- **Pros:** Seamless experience for both local and hosted environments.
- **Cons:** Adds complexity to configuration loading; increases surface for misconfiguration; harder to test deterministically.
- **Reason for rejection:** Complexity outweighs benefit for current roadmap; explicit configuration keeps behavior predictable.

## Consequences

### Positive Consequences

- Eliminates OpenAI quota bottlenecks for tests and local runs.
- Reduces operational cost by defaulting to a free local model.
- Improves security posture by keeping sensitive content on-device (LLM05).

### Negative Consequences

- Default summaries may be lower fidelity than GPT-4-class models.
- Requires developers to install and run Ollama before using defaults.

### Neutral Consequences

- Documentation and tests must acknowledge the new default.
- Teams targeting higher quality must explicitly set provider/model overrides.

## Implementation

- Update `SummarizerSettings` defaults in `src/mcp_web/config.py`.
- Adjust unit tests (`tests/unit/test_config.py`) to expect the new defaults.
- Refresh documentation (`README.md`, `docs/reference/CONFIGURATION.md`, `docs/reference/ENVIRONMENT_VARIABLES.md`, `PROJECT_SUMMARY.md`, and related guides).
- Mark ADR-0010 as superseded and reference this decision.

## References

- [OWASP LLM Top 10 (2025)](https://genai.owasp.org/)
- [Meta Llama 3 Model Card](https://ai.meta.com/llama/)
- [Ollama Model Library](https://ollama.com/library/llama3)
- Related ADR: [0010-openai-gpt4-default-llm.md](0010-openai-gpt4-default-llm.md)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-10-16 | Initial proposal | Cascade |
