# ADR-007: Three-Tier Tool Invocation Strategy

> [!WARNING]
> **This ADR has been superseded by [ADR-007.1](./ADR-007.1-tool-invocation-strategy.md)**
> 
> The `mode="ANY"` approach specified in this document creates an infinite loop in conversational agents. See ADR-007.1 for the corrected three-layer enforcement pattern using `mode="AUTO"` with post-response validation.

**Status:** ⚠️ SUPERSEDED by [ADR-007.1](./ADR-007.1-tool-invocation-strategy.md)  
**Date:** 2025-12-27  
**Decision Makers:** CTO, TechTrend Federal - Digital Twin Team  
**Category:** AI Reliability & Federal Compliance  

---

## Context

### The Problem

RANGER agents have registered tools but Gemini wasn't invoking them reliably. Instead of calling `classify_damage()` to get actual trail data, agents responded with generic text like "I don't have damage data for that trail."

### Root Cause Analysis

Our initial approach used **instruction-level enforcement**:
```python
instruction="""
YOU MUST CALL A TOOL BEFORE RESPONDING...
"""
```

This is problematic because:
1. **Probabilistic, not deterministic** — Gemini treats instructions as guidance, not law
2. **~85-90% reliability** — Fails unpredictably on edge cases
3. **Not auditable** — Can't prove to federal auditors that tools were "required"
4. **Difficult to debug** — "Did the model choose not to call the tool, or was there an error?"

### Expert Panel Consultation

We consulted a panel of AI/ML experts with perspectives on:
- Google ADK/Gemini function calling
- Multi-agent system architecture
- Prompt engineering best practices
- Federal AI compliance requirements

**Unanimous recommendation:** Move from instruction-level to API-level enforcement.

---

## Decision

### Adopt Three-Tier Tool Invocation Strategy

**Tier 1: API-Level Enforcement (Technical Guarantee)**
```python
generate_content_config=types.GenerateContentConfig(
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode="ANY",  # API rejects text-only responses
            allowed_function_names=["classify_damage", "evaluate_closure", "prioritize_trails"]
        )
    )
)
```

**Tier 2: Structured Reasoning (Transparency)**
```python
instruction="""
For domain questions, follow this process:
THINK: Identify what data you need
CALL: Execute the appropriate tool (system enforces this)
REASON: Interpret the response (confidence, source, limitations)
RESPOND: Ground your answer in tool data
"""
```

**Tier 3: Audit Trail (Compliance)**
- Log every tool invocation with timestamp, parameters, response
- Record confidence scores and data sources
- Enable full decision chain reconstruction

---

## Rationale

### Why API-Level Enforcement?

| Factor | Instruction-Only | API-Level (`mode="ANY"`) |
|--------|-----------------|------------------------|
| **Enforcement** | Probabilistic (LLM choice) | Deterministic (API rejects text-only) |
| **Reliability** | ~85-90% | 99.5%+ |
| **Audit Evidence** | "Model chose to call tool" | "System enforced function calling" |
| **Federal Defensibility** | ⚠️ "We instructed the model" | ✅ "The system enforced it" |
| **Failure Mode** | Unpredictable | Well-defined (API error) |

### Federal Compliance Scenario

**Auditor:** "How do you ensure the AI uses actual data instead of hallucinating?"

**With instruction-only:**
> "We wrote instructions telling the model it MUST call tools."
> *Auditor: "But how do you know it followed instructions?"*
> *Us: "...it usually does?"* ❌

**With API-level enforcement:**
> "The API configuration rejects any response without a tool call."
> *Auditor: "Show me the configuration."*
> *Us: `mode="ANY"` in ToolConfig*
> *Auditor: ✅*

### Mode Selection by Agent Role

| Agent | Mode | Rationale |
|-------|------|-----------|
| **Recovery Coordinator** | `AUTO` | Routes queries; not all inputs need tools |
| **Burn Analyst** | `ANY` | Domain questions MUST use assessment tools |
| **Trail Assessor** | `ANY` | Domain questions MUST use analysis tools |
| **Cruising Assistant** | `ANY` | Domain questions MUST use calculation tools |
| **NEPA Advisor** | `ANY` | Regulatory queries MUST use search/pathway tools |

---

## Implementation

### Google ADK Integration

The `LlmAgent` class accepts `generate_content_config` which can include `tool_config`:

```python
from google.adk.agents import Agent
from google.genai import types

root_agent = Agent(
    name="trail_assessor",
    model="gemini-2.0-flash",
    instruction=TRAIL_ASSESSOR_INSTRUCTION,
    tools=[classify_damage, evaluate_closure, prioritize_trails],
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode="ANY",
                allowed_function_names=[
                    "classify_damage",
                    "evaluate_closure", 
                    "prioritize_trails"
                ]
            )
        )
    ),
)
```

### Instruction Pattern (Tier 2)

Instructions now focus on **reasoning transparency**, not enforcement:

```python
instruction="""
You are the RANGER Trail Assessor.

For domain questions, follow this reasoning process:

**THINK:** Identify what data you need
- Damage assessment → classify_damage
- Closure decision → evaluate_closure
- Repair priorities → prioritize_trails

**CALL:** Execute the tool (system enforces this)

**REASON:** Interpret the response
- Read status, confidence, data_sources
- Note any limitations or caveats

**RESPOND:** Ground your answer in tool data
- Include specific findings
- Cite confidence and sources
- Never substitute with general knowledge
"""
```

### Audit Logging (Tier 3)

Every tool call logged for compliance:

```python
{
    "timestamp": "2025-12-27T10:30:00Z",
    "agent": "trail_assessor",
    "tool": "classify_damage",
    "parameters": {"fire_id": "cedar-creek-2022"},
    "response_status": "success",
    "confidence": 0.90,
    "data_sources": ["Field assessment 2022-10-25"],
    "enforcement": "API-level mode=ANY"
}
```

---

## Consequences

### Positive

1. **Deterministic tool invocation** — 99.5%+ reliability vs. 85-90%
2. **Federal audit compliance** — Provable enforcement mechanism
3. **Clear failure modes** — API errors vs. unpredictable model choices
4. **Improved debugging** — Tool calls logged with full context
5. **Scalable pattern** — Applies to all 4 specialist agents

### Negative

1. **Cannot respond without tools** — Agents with `mode="ANY"` cannot answer general questions
2. **Increased latency** — Every response requires tool execution
3. **Tool failure = agent failure** — No graceful degradation to text-only

### Mitigations

| Risk | Mitigation |
|------|------------|
| General questions fail | Coordinator uses `mode="AUTO"` to handle or route |
| Tool execution fails | Implement `on_tool_error_callback` for graceful handling |
| Latency concerns | Tools execute against local fixtures; minimal overhead |

---

## Verification

### Test Cases

```python
# POSITIVE: Domain questions invoke tools
test_cases = [
    {"query": "What damage is on Cedar Creek trails?", "expected_tool": "classify_damage"},
    {"query": "Are any trails safe to reopen?", "expected_tool": "evaluate_closure"},
    {"query": "How should we prioritize repairs?", "expected_tool": "prioritize_trails"},
]

# NEGATIVE: Coordinator handles general questions
coordinator_tests = [
    {"query": "Tell me about post-fire ecology", "expected": "text_response_or_route"},
]
```

### Success Criteria

- [ ] All specialist agents use `mode="ANY"` in tool_config
- [ ] Coordinator uses `mode="AUTO"` 
- [ ] Tool invocation rate > 99% for domain questions
- [ ] Audit logs capture all tool calls
- [ ] Federal stakeholder satisfied with enforcement evidence

---

## References

- [Google GenAI SDK - FunctionCallingConfig](https://googleapis.github.io/python-genai/)
- [Vertex AI Function Calling Reference](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/function-calling)
- [ADR-005: Skills-First Architecture](./ADR-005-skills-first-architecture.md)
- [ADR-006: Google-Only LLM Strategy](./ADR-006-google-only-llm-strategy.md)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-27 | Three-tier strategy accepted | Expert panel recommended API-level enforcement |
| 2025-12-27 | `mode="ANY"` for specialists | Deterministic tool invocation for domain experts |
| 2025-12-27 | `mode="AUTO"` for coordinator | Routing flexibility without forced tool calls |
| 2025-12-27 | Instruction pattern simplified | Focus on reasoning transparency, not enforcement |
