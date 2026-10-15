# ADR-008: AgentTool Pattern for Multi-Agent Orchestration

**Date:** 2025-12-27
**Status:** ✅ **ACCEPTED** (Replaces previous sub_agents approach)
**Deciders:** Expert Panel, Claude Code
**Related:** ADR-005 (Skills-First Architecture)

---

## Context

RANGER's Recovery Coordinator must orchestrate responses from four domain specialists:
- Burn Analyst (fire severity)
- Trail Assessor (infrastructure damage)
- Cruising Assistant (timber salvage)
- NEPA Advisor (regulatory compliance)

Initially, we implemented this using ADK's `sub_agents` parameter, which transfers conversation control to specialists. This caused critical failures:

1. **Specialists received queries directly** → Refused out-of-scope queries
2. **No multi-domain synthesis** → "Recovery briefing" queries failed
3. **Coordinator lost control** → Could not orchestrate multiple specialists

**Root Cause (Identified by Expert Panel):**
We were using the WRONG ADK multi-agent pattern. `sub_agents` is for sequential handoffs, not orchestration.

---

## Decision

**Use `AgentTool` wrappers to call specialists as callable functions**, not `sub_agents`.

### Pattern: AgentTool Wrappers
```python
from google.adk.agents import Agent
from google.adk.tools import AgentTool

# Wrap each specialist as an AgentTool
burn_analyst_tool = AgentTool(agent=burn_analyst)
trail_assessor_tool = AgentTool(agent=trail_assessor)
cruising_assistant_tool = AgentTool(agent=cruising_assistant)
nepa_advisor_tool = AgentTool(agent=nepa_advisor)

# Coordinator retains control, calls specialists as tools
root_agent = Agent(
    name="coordinator",
    model="gemini-2.0-flash",
    tools=[
        burn_analyst_tool,
        trail_assessor_tool,
        cruising_assistant_tool,
        nepa_advisor_tool,
        portfolio_triage,
    ],
    # NO sub_agents parameter
)
```

### System Prompt Strategy
Explicitly describe WHEN to use each specialist tool:

```
## Query Handling Protocol

### Single-Domain Queries
- **burn_analyst**: Call for burn severity, fire impact, MTBS classification
- **trail_assessor**: Call for trail damage, infrastructure, closures
- **cruising_assistant**: Call for timber salvage, volume estimates
- **nepa_advisor**: Call for NEPA compliance, CE/EA/EIS pathways

### Multi-Domain Queries
For "recovery briefing" or "status update":
1. Call ALL FOUR specialist tools sequentially
2. Synthesize outputs into coherent briefing
3. Highlight cross-domain dependencies
```

---

## Consequences

### ✅ Positive

1. **Coordinator Retains Control**
   - Can call multiple specialists in one turn
   - Synthesizes outputs before responding
   - No transfer of conversation ownership

2. **Multi-Domain Synthesis Works**
   - "Recovery briefing" triggers all 4 specialists
   - Coordinator combines burn severity + trail damage + timber + NEPA
   - Cross-domain insights ("bridge repair unlocks timber access")

3. **Confidence Preservation**
   - Tool results include specialist confidence values
   - Coordinator instructed to preserve exact values
   - Users see dynamic confidence (85-98%) instead of static 75%

4. **No Specialist Refusals**
   - Specialists are called as functions, not conversation owners
   - They process inputs and return results
   - No "I cannot help with that" errors

### ⚠️ Trade-offs

1. **System Prompt Complexity**
   - Must explicitly describe when to use each tool
   - LLM decides routing based on prompt, not delegation skill
   - Relies on Gemini's tool-calling intelligence

2. **Loss of Delegation Routing Logic**
   - Previous keyword-based routing (0.1-0.98 confidence) unused
   - Gemini makes routing decisions internally
   - Can't see routing confidence scores anymore

3. **Tool Calling Overhead**
   - Each specialist call is a tool invocation (API cost)
   - Multi-domain queries = 4 tool calls per turn
   - Sequential execution (can't parallelize)

---

## When to Use sub_agents vs AgentTool

### Use `sub_agents` When:
- **Sequential workflows** where each agent owns a step
- **Handoff patterns** (e.g., sales → support → billing)
- Each agent needs FULL conversation context
- Specialists decide when to return control

**Example:** Customer service chatbot routing to specialists

### Use `AgentTool` When:
- **Orchestration patterns** where coordinator synthesizes
- **Multi-domain queries** requiring specialist combination
- Coordinator remains conversation owner
- Specialists are consulted, not delegated to

**Example:** RANGER recovery briefings (our use case)

---

## Implementation

### Files Modified
- `agents/coordinator/agent.py` - Refactored to use AgentTool pattern

### Key Changes
1. Import `AgentTool` from `google.adk.tools`
2. Wrap specialists: `burn_analyst_tool = AgentTool(agent=burn_analyst)`
3. Add to tools list (not sub_agents)
4. Update system prompt with explicit tool usage guidance
5. Remove `delegate_query()` function (no longer needed)

### Testing Strategy
```bash
# Test single-domain
"What is the burn severity at Cedar Creek?"
→ Should call burn_analyst tool

# Test multi-domain
"Give me a recovery briefing for Cedar Creek"
→ Should call all 4 specialist tools
→ Should synthesize outputs

# Test portfolio
"Which fires need BAER assessments?"
→ Should call portfolio_triage tool
```

---

## Alternatives Considered

### Alternative 1: Keep sub_agents, Add Delegation Layer
**Approach:** Use delegation skill to route queries before sub_agents.

**Rejected because:**
- Still transfers control to specialists
- Can't call multiple specialists in one turn
- Doesn't solve multi-domain synthesis

### Alternative 2: Flatten to Single Agent
**Approach:** Remove specialists, give coordinator all domain skills directly.

**Rejected because:**
- Violates Skills-First Architecture (ADR-005)
- Loses specialist expertise modularity
- Single agent would be too complex

### Alternative 3: Sequential Agent Chain
**Approach:** Use SequentialAgent to chain specialists.

**Rejected because:**
- Not all queries need all specialists
- Can't dynamically select which specialists to call
- Forces sequential execution even when parallel would work

---

## Lessons Learned

### 1. ADK Patterns Matter
The choice between `sub_agents` and `AgentTool` is **architectural**, not cosmetic.
- `sub_agents` = handoff pattern (transfer control)
- `AgentTool` = orchestration pattern (retain control)

### 2. System Prompt is Critical
With AgentTool, the LLM decides which tools to call.
Explicit guidance required: "Call burn_analyst for burn severity queries"

### 3. Multi-Domain Synthesis is Core to RANGER
Recovery operations are inherently cross-functional.
Burn severity affects trail safety, which affects timber access, which affects NEPA pathways.
AgentTool enables this synthesis.

### 4. Confidence Transparency
Specialist confidence values (0.85-0.98) are essential for user trust.
AgentTool preserves these through tool results.
System prompt must instruct coordinator to relay them.

---

## References

- [Google ADK Docs: Sub-Agents vs Agents as Tools](https://cloud.google.com/blog/topics/developers-practitioners/where-to-use-sub-agents-versus-agents-as-tools)
- [ADK Multi-Agent Patterns](https://google.github.io/adk-docs/agents/multi-agents/)
- ADR-005: Skills-First Multi-Agent Architecture
- Previous Audit: `docs/reports/AGENT-ARCHITECTURE-AUDIT-2025-12-27.md` (Root cause was incorrect)
- Refactor Report: `docs/reports/AGENTTOOL-REFACTOR-2025-12-27.md`

---

## Review

**Expert Panel Feedback:** ✅ **APPROVED**
Pattern correctly identified, implementation aligned with ADK best practices.

**Next Review Date:** Post-deployment validation (TBD)

---

**Supersedes:** Previous sub_agents implementation (agents/coordinator/agent.py prior to 2025-12-27)
