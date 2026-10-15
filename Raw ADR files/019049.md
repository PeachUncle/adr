# ADR-0005: AI Agent Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "AI Agent Stack" includes agent SDK, LLM provider, model routing).

- **Status:** Accepted
- **Date:** 2025-12-17
- **Feature:** 002-ai-chatbot
- **Context:** Phase 3 requires an AI-powered chatbot that can understand natural language commands and execute task operations (add, list, complete, delete, update tasks). The AI agent must integrate with MCP tools, support streaming responses for real-time UX, and use the Gemini model as specified. The agent must be stateless (conversation history loaded from database per request) and support function tool calling for MCP integration.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines AI orchestration pattern for all chatbot features
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - LangChain, direct Gemini API, CrewAI evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects agent code, tool integration, and response streaming
-->

## Decision

We will adopt the following integrated AI agent stack:

- **Agent SDK:** OpenAI Agents SDK (openai-agents)
- **Model Router:** LiteLLM extension (agents.extensions.models.litellm.LitellmModel)
- **LLM Provider:** Google Gemini (`gemini/gemini-2.5-flash`)
- **API Key Management:** Server-side environment variable (GEMINI_API_KEY)
- **Tool Definition:** @function_tool decorator wrapping MCP tool calls
- **Streaming:** Runner.run_streamed() for SSE-compatible token streaming
- **Hooks:** AgentHooks and RunHooks for observability and error handling

### Agent Configuration Pattern

```python
from agents import Agent, Runner, function_tool
from agents.extensions.models.litellm import LitellmModel

# Model configuration
model = LitellmModel(model="gemini/gemini-2.5-flash", api_key=GEMINI_API_KEY)

# Agent definition
agent = Agent(
    name="TodoBot",
    instructions=SYSTEM_PROMPT,
    model=model,
    tools=[add_task, list_tasks, complete_task, delete_task, update_task]
)

# Streaming execution
async for event in Runner.run_streamed(agent, messages):
    # Handle streaming events (tokens, tool_calls)
```

### Rationale

OpenAI Agents SDK provides a standardized abstraction for building AI agents with function tools, hooks, and streaming support. The LiteLLM extension enables using Gemini models through the same interface that would work with OpenAI models. This abstraction allows future model switching without changing agent code. The SDK's @function_tool decorator provides automatic schema generation and validation for MCP tool wrappers.

## Consequences

### Positive

- **Model Portability:** LiteLLM abstraction allows switching between Gemini, OpenAI, Anthropic models with config changes only
- **Standardized Patterns:** SDK provides consistent patterns for tools, hooks, streaming, and context management
- **Streaming First:** Runner.run_streamed() provides SSE-compatible events for real-time UI updates
- **Type Safety:** @function_tool generates typed schemas from Python type hints
- **Hooks for Observability:** AgentHooks and RunHooks enable logging, metrics, and error handling
- **Stateless Design:** Agent is instantiated per request, loading conversation history from database
- **SDK Maintained:** Backed by OpenAI, actively maintained with documentation
- **Gemini Cost Efficiency:** Gemini Flash is cost-effective for high-volume chat interactions

### Negative

- **SDK Abstraction Overhead:** Additional layer between application and LLM API adds complexity
  - *Mitigation:* SDK overhead is minimal; abstraction benefits outweigh costs
- **LiteLLM Dependency:** Adds dependency on LiteLLM for Gemini support
  - *Mitigation:* LiteLLM is widely adopted and actively maintained
- **Gemini Model Limitations:** Gemini may have different capabilities than GPT-4
  - *Mitigation:* Gemini Flash is sufficient for task management; can upgrade to Gemini Pro if needed
- **Learning Curve:** Team must learn OpenAI Agents SDK patterns
  - *Mitigation:* SDK has clear documentation; patterns are similar to other agent frameworks
- **Version Coupling:** SDK updates may require code changes
  - *Mitigation:* Pin SDK version; update deliberately

## Alternatives Considered

### Alternative A: LangChain + LangGraph
- **Pros:** Mature ecosystem, extensive LLM provider support, built-in chains and tools
- **Cons:** Heavy dependency (200+ transitive packages), complex abstractions, slower startup
- **Why Rejected:** Over-engineered for single-agent task management; LangChain's complexity adds cognitive overhead without proportional benefit for our simple agent use case.

### Alternative B: Direct Gemini API (google-generativeai)
- **Pros:** No abstraction overhead, direct API access, smaller dependency footprint
- **Cons:** No standardized tool calling, must build streaming logic, no agent abstraction
- **Why Rejected:** Would require building agent orchestration, tool calling, and streaming from scratch; violates "don't reinvent the wheel" principle.

### Alternative C: CrewAI
- **Pros:** Multi-agent support, built-in collaboration patterns, task delegation
- **Cons:** Designed for multi-agent scenarios, overkill for single agent, newer/less stable
- **Why Rejected:** Multi-agent features unnecessary for todo chatbot; single agent pattern is simpler and sufficient.

### Alternative D: Semantic Kernel (Microsoft)
- **Pros:** Enterprise-grade, multi-language support (C#, Python, Java), plugin architecture
- **Cons:** Enterprise-focused abstractions, heavier than needed, Microsoft ecosystem
- **Why Rejected:** Enterprise patterns are overkill; OpenAI Agents SDK is lighter and purpose-built for agent scenarios.

## References

- Feature Spec: [specs/002-ai-chatbot/spec.md](../../specs/002-ai-chatbot/spec.md)
- Implementation Plan: [specs/002-ai-chatbot/plan.md](../../specs/002-ai-chatbot/plan.md)
- Research Notes: [specs/002-ai-chatbot/research.md](../../specs/002-ai-chatbot/research.md) §1
- Related ADRs: ADR-0002 (Backend Stack - Python/FastAPI foundation), ADR-0006 (MCP Server Architecture)
- OpenAI Agents SDK Documentation: https://openai.github.io/openai-agents-python/
- LiteLLM Documentation: https://docs.litellm.ai/
