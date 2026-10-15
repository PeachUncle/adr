# ADR-0002: LangGraph Agent System

**Date:** 2025-11-27  
**Status:** Active  
**Deciders:** Core Team, AI/ML Lead

---

## Context

Chef's Mind AI is a multi-agent system that handles diverse tasks:

- **Chef Agent:** Menu creation, recipe generation, ingredient substitutions
- **Accountant Agent:** Cost breakdown, pricing, budget analysis
- **Media Agent:** Image/video generation for dishes and menus
- **Researcher Agent:** External research, ingredient sourcing, trend analysis
- **Quality Control:** Validation, hallucination detection, safety checks

### Problem Statement

Without a structured orchestration layer:

- Requests would need manual routing in application code
- No clear separation of concerns between agents
- Difficult to trace agent decisions and handoffs
- Hard to add new agents or modify behavior
- No standard pattern for inter-agent communication

---

## Decision

**We will use LangGraph as the orchestration framework for all multi-agent workflows.**

### Architecture

```
User Request
    ↓
Router Node (determines primary agent)
    ↓
Agent Node (Chef / Accountant / Media / Researcher)
    ↓
Quality Control Node (validates output)
    ↓
Answer Node (formats response)
```

### Key Components

1. **Orchestrator** (`server/agents/orchestrator.ts`)
   - Entry point for all agent requests
   - Manages LangGraph state and execution flow

2. **Graph Definition** (`server/graph/graph.ts`)
   - Defines nodes, edges, conditional routing
   - Implements state management and context passing

3. **Agent Nodes** (`server/graph/nodes/`)
   - Individual agent implementations (chef, accountant, media, researcher)
   - Each node is self-contained with specific LLM config

4. **Router Strategy** (`server/config/agent-routing.ts`)
   - Intent classification rules
   - Agent selection logic based on user query

### Responsibilities

- **LangGraph:** State management, flow control, routing, tracing
- **Agent Nodes:** Business logic, LLM calls, tool execution
- **Services Layer:** Data access, external API calls, persistence

---

## Consequences

### Advantages

✅ **Traceability:** Every agent decision is logged in LangGraph state  
✅ **Extensibility:** Add new agents by defining new nodes  
✅ **Control Flow:** Complex workflows (loops, conditionals, parallel execution) are declarative  
✅ **Debugging:** LangSmith integration for visual debugging  
✅ **Testing:** Each node can be unit-tested independently  
✅ **Modularity:** Agents are loosely coupled, easy to modify  

### Disadvantages

⚠️ **Learning Curve:** Team needs to understand LangGraph concepts (state graphs, reducers, checkpointing)  
⚠️ **Complexity:** More abstraction layers compared to direct LLM calls  
⚠️ **Debugging Overhead:** Graph execution can be harder to debug than linear code  
⚠️ **Performance:** Graph execution adds slight latency vs direct agent calls  

### Risks

🔴 **LangGraph Dependency:** Tight coupling to LangChain/LangGraph ecosystem  
🔴 **Breaking Changes:** LangGraph API may change in future versions  
🟡 **Over-Engineering:** Simple single-agent tasks may not need full graph orchestration  

---

## Alternatives Considered

### Alternative 1: Custom Orchestrator

- ✅ Full control, no external dependencies
- ❌ Reinventing the wheel, significant dev time
- ❌ No built-in tracing/debugging tools

### Alternative 2: Simple If/Else Routing

- ✅ Simple to understand
- ❌ Doesn't scale to complex multi-step workflows
- ❌ No state management or retry logic

### Alternative 3: LangChain without LangGraph

- ✅ Simpler than LangGraph
- ❌ No visual graph representation
- ❌ Limited control flow capabilities

### Alternative 4: AutoGen or CrewAI

- ✅ Alternative multi-agent frameworks
- ❌ Less mature ecosystem than LangChain
- ❌ Different abstractions, similar trade-offs

---

## Status

**Active** — LangGraph is the core orchestration layer for all agents.

### Implementation Notes

- Graph checkpointing enabled for long-running tasks
- LangSmith integration for production monitoring
- All agents configured via `server/config/llm-config.ts`

### Next Review

- **When:** After scaling to 10+ agents
- **Trigger:** If performance bottlenecks emerge
- **Action:** Evaluate alternative orchestration patterns or optimizations
