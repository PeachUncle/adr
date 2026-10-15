# ADR-002: Multi-Agent Orchestration Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-19
- **Feature:** Phase 3 - Todo AI Chatbot
- **Context:** The AI chatbot requires intelligent request handling where different types of user intents (CRUD operations, planning, general chat) need specialized processing. We must decide how to structure the AI processing layer: single monolithic agent vs. multi-agent system, routing strategy, and capability boundaries.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ Yes - defines entire AI layer structure
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ Yes - single agent, LangChain, custom
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ Yes - affects all chat interactions
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We adopt a **multi-agent orchestration pattern** with specialized agents coordinated by a primary ConversationAgent:

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestrator** | ConversationAgent | Intent classification, routing, response generation |
| **CRUD Executor** | TaskManagerAgent | Read/write task operations via MCP tools |
| **Analyst** | PlannerAgent | Read-only task analysis, planning, summarization |
| **Safety Layer** | GuardrailAgent | Pre/post execution validation, confirmation flow |
| **Tool Server** | MCPServerAgent | MCP tool registration and execution |
| **SDK** | OpenAI Agents SDK | Agent coordination, tool binding, Runner execution |

### Agent Hierarchy

```
ConversationAgent (Router)
    ├── TaskManagerAgent (CRUD)
    │       └── MCPServerAgent (Tools)
    ├── PlannerAgent (Analysis)
    └── GuardrailAgent (Safety) ← validates all write operations
```

### Routing Rules

| Intent | Target Agent | Guardrails Required |
|--------|--------------|---------------------|
| read | TaskManagerAgent | No |
| create | TaskManagerAgent | Yes (validation) |
| update | TaskManagerAgent | Yes (validation) |
| delete | TaskManagerAgent | Yes (confirmation) |
| complete | TaskManagerAgent | Yes (validation) |
| plan | PlannerAgent | No |
| chat | ConversationAgent | No |

## Consequences

### Positive

- **Separation of concerns**: Each agent has a single responsibility, making code easier to test and maintain
- **Specialized prompts**: Agents can have focused system prompts optimized for their task
- **Independent scaling**: Heavy operations (planning) don't block simple queries (listing)
- **Safety boundaries**: GuardrailAgent provides a clear enforcement point for all write operations
- **Extensibility**: New agents can be added without modifying existing ones (e.g., NotificationAgent)
- **Debugging**: Agent chain logged for traceability (`["ConversationAgent", "TaskManagerAgent"]`)

### Negative

- **Latency overhead**: Multi-hop routing adds ~100-200ms per additional agent
- **Complexity**: More moving parts than a single-agent solution
- **Context propagation**: Session context must be passed through agent chain
- **Token costs**: Each agent invocation consumes tokens (mitigated by using gpt-4o-mini)
- **Error propagation**: Failures can occur at any hop; requires robust error handling

## Alternatives Considered

### Alternative A: Single Monolithic Agent

- **Approach**: One agent handles all intents with a comprehensive system prompt
- **Pros**: Simpler architecture, lower latency, easier to debug
- **Cons**: Bloated prompt, harder to maintain, no clear safety boundaries, testing complexity
- **Why rejected**: Intent-specific specialization and guardrail enforcement require separation

### Alternative B: LangChain Agents Framework

- **Approach**: Use LangChain's agent/tool abstractions
- **Pros**: Mature ecosystem, built-in memory, many integrations
- **Cons**: Heavy dependency, opinionated patterns, abstraction overhead, Python-specific
- **Why rejected**: OpenAI Agents SDK is lighter, more aligned with our direct OpenAI usage

### Alternative C: LangGraph State Machine

- **Approach**: Model agent flow as a directed graph with LangGraph
- **Pros**: Visual workflow, explicit state transitions, parallel execution
- **Cons**: Learning curve, additional dependency, overkill for linear flows
- **Why rejected**: Our flow is mostly linear; state machine complexity not justified

### Alternative D: Direct Function Routing (No Agents)

- **Approach**: Simple if/else routing to service functions based on intent
- **Pros**: Fastest, simplest, no SDK dependency
- **Cons**: No conversational context, no natural language response generation, rigid
- **Why rejected**: Need AI-powered intent classification and response generation

## References

- Feature Spec: `specs/phase3-ai-chatbot/spec.md`
- Architecture Diagram: `specs/phase3-ai-chatbot/architecture.md`
- Related ADRs: ADR-001 (Authentication integrates with chat auth)
- Agent Definitions: `.claude/agents/conversation-agent.md`, `.claude/agents/task-manager.md`
