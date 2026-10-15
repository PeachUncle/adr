# ADR-028: Choice of Custom YAML Workflow Engine Over OpenAI Agents SDK

**Status**: Accepted
**Date**: 2025-06-XX
**Deciders**: Engineering Team
**Related**: ADR-026 (Superseded), ADR-027

---

## Context

We implemented custom YAML-driven workflow engines for our quote and triage agents (~500 lines each). After implementation, we evaluated whether the **OpenAI Agents SDK** (ChatKit) could replace our custom code and reduce complexity.

### The Question
> "Should we replace our custom YAML workflow engine with the OpenAI Agents SDK?"

### The Hypothesis
The OpenAI Agents SDK might provide:
- Fewer lines of code (SDK abstracts complexity)
- Built-in session management
- Official support and maintenance
- Best practices from OpenAI

### The Experiment
We created a branch (`experiment/chatkit-agents-sdk`) to test the SDK side-by-side:

**What We Built:**
1. **YAML → ChatKit Agent Transformer** (`yaml-to-chatkit-agent.mjs`, ~150 lines)
   - Converted YAML nodes to ChatKit "tools"
   - Generated agent instructions from workflow structure
   - Attempted to map deterministic flows to SDK patterns

2. **ChatKit Netlify Function** (`quote-agent-chatkit.mjs`, ~220 lines)
   - Used `@openai/agents` SDK
   - Implemented `run(agent, messages)` pattern
   - Maintained same external API contract

3. **Frontend Component** (`QuoteAgentModal-ChatKitSDK.tsx`, ~260 lines)
   - Simplified chat interface
   - Side-by-side comparison toggle in UI

**What We Discovered:**
- ❌ **SDK Error**: `"Unsupported tool type: hosted_tool"`
- ❌ **Architectural Mismatch**: SDK designed for function calling, not conversation flow control
- ❌ **Loss of Determinism**: SDK expects AI to drive conversation, not pre-defined YAML structure
- ❌ **YAML Benefits Lost**: Could not preserve non-technical editing capability

---

## Decision

**We will continue with our custom YAML workflow engine.**

The OpenAI Agents SDK is not suitable for our use case.

---

## Rationale

### Why the SDK Failed

1. **Fundamental Architecture Mismatch**
   - **SDK Design**: AI-driven conversations with function calling
   - **Our Requirement**: Deterministic, structured question flows
   - **Conflict**: SDK expects tools to be actions (e.g., "check_weather"), not conversation nodes

2. **Tool Type Incompatibility**
   - SDK threw: `"Unsupported tool type: hosted_tool"`
   - SDK expects: `function` tools that execute and return data
   - Our nodes: Conversation states that ask questions and collect answers
   - **No workaround available** - SDK fundamentally incompatible

3. **Loss of YAML Benefits**
   - **Original Goal**: Non-technical users can edit workflows in YAML
   - **With SDK**: YAML becomes just configuration for code that SDK controls
   - **Result**: Lost simplicity and maintainability advantages

4. **Complexity Doesn't Decrease**
   - Custom approach: ~500 lines (workflow engine + agent logic)
   - SDK approach: ~150 (transformer) + ~220 (handler) + SDK complexity = higher total complexity
   - **SDK adds abstraction layer** without solving our core problem

### Why Custom YAML Is Correct

1. **Perfect Fit for Use Case**
   - Structured intake questions with branching logic
   - Deterministic flow with clear state transitions
   - No need for AI to "decide" next steps - workflow defines them

2. **Non-Technical Editing**
   ```yaml
   question: "What type of property is this?"
   options:
     - text: "Residential"
       next: residential_questions
     - text: "Commercial"
       next: commercial_questions
   ```
   - Product managers can modify workflows
   - No code changes required for new questions
   - Version control provides audit trail

3. **Full Control**
   - We control session management
   - We control node traversal
   - We control validation and error handling
   - No SDK constraints or limitations

4. **OpenAI Still Used (Where Appropriate)**
   - We use OpenAI for **dynamic follow-up questions** (`generateFollowUpQuestions()`)
   - We use OpenAI for **triage analysis** (job complexity, urgency scoring)
   - **Best of both worlds**: Deterministic structure + AI-powered insights

5. **No Vendor Lock-In**
   - YAML is portable and language-agnostic
   - Could switch to Anthropic, Gemini, or local models for follow-ups
   - Not tied to OpenAI's SDK versioning or deprecation policies

---

## Consequences

### Positive
- ✅ **Validated our architecture**: Experiment proved custom approach is correct
- ✅ **Clear decision**: No future questioning of "should we use SDK?"
- ✅ **Maintainable**: ~500 lines is reasonable for the functionality provided
- ✅ **Flexible**: Can extend workflow engine with new node types as needed
- ✅ **Non-technical editing**: YAML remains accessible to product team

### Negative
- ⚠️ **Maintenance responsibility**: We own the workflow engine code
- ⚠️ **Feature parity**: Must implement features ourselves (session persistence, error recovery)
- ⚠️ **Testing burden**: Must test workflow engine thoroughly

### Neutral
- 📝 **Documentation**: Must document YAML schema and workflow patterns (already done)
- 📝 **Examples**: Must provide clear examples for new agents (already exists)

---

## Alternatives Considered

### 1. OpenAI Agents SDK (ChatKit) ❌
**Rejected**: Architectural mismatch, tool type incompatibility, loss of YAML benefits

### 2. Langchain / LlamaIndex ❌
**Rejected**: Similar issues - designed for AI-driven conversations, not deterministic flows

### 3. State Machine Libraries (XState) ⚠️
**Deferred**: Could work, but adds complexity for non-technical editing
- YAML → XState would require abstraction layer
- Not clear benefit over current approach
- Could revisit if workflows become significantly more complex

### 4. Custom YAML Engine (Current) ✅
**Accepted**: Perfect fit for structured intake workflows with non-technical editing

---

## Implementation

### Cleanup Completed
- ✅ Deleted experiment branch (`experiment/chatkit-agents-sdk`)
- ✅ Removed `@openai/agents` SDK dependency (46 packages removed)
- ✅ Removed `@openai/chatkit-react` UI library
- ✅ Deleted test scripts using SDK (`test-agent-sdk.mjs`, `test-agent.mjs`)
- ✅ Updated `tests/manual/README.md` to reflect findings

### Architecture Preserved
- ✅ `packages/backend/netlify/functions/quote-agent.mjs` (~500 LOC)
- ✅ `packages/backend/netlify/functions/triage-agent.mjs` (~400 LOC)
- ✅ YAML configuration: `agents/quote-agent.yaml`, `agents/triage-agent.yaml`
- ✅ Custom workflow engine with node traversal and session management
- ✅ OpenAI used only for `generateFollowUpQuestions()` and triage analysis

---

## Related Documentation

- [ChatKit Experiment Results](../docs/CHATKIT_EXPERIMENT.md) - Detailed findings and error logs
- [ADR-027](027-self-contained-agent-functions.md) - Self-contained agent architecture
- [ADR-026](026-agent-runner-local-first-strategy.md) - **Superseded**
- [Quote Agent Maintenance Guide](../docs/QUOTE_AGENT_MAINTENANCE.md)

---

## Lessons Learned

1. **Not all AI frameworks fit all use cases**
   - Evaluate based on your requirements, not industry hype
   - "AI-powered" doesn't mean "better for AI-related tasks"

2. **Fewer lines of code ≠ better solution**
   - ~500 lines of custom code is reasonable and maintainable
   - SDK abstraction can add complexity, not reduce it

3. **Experimentation validates decisions**
   - Building the comparison proved our approach was correct
   - Now we have evidence, not just opinions

4. **YAML-driven workflows are valid**
   - Not every conversational flow needs AI to drive it
   - Deterministic structures have advantages: predictability, testability, auditability

---

## Future Considerations

### When to Reconsider
- If OpenAI releases a "structured workflow" SDK mode
- If workflows become so complex that YAML becomes unwieldy (100+ nodes)
- If we need AI to dynamically generate questions based on context (not just follow-ups)

### When to Keep Custom Approach
- Structured intake forms with branching logic ✅
- Workflows that require deterministic behavior ✅
- Non-technical team needs to edit flows ✅
- Audit trail and version control requirements ✅

---

**Conclusion**: The OpenAI Agents SDK is a powerful tool for AI-driven conversations with function calling. However, our YAML-driven workflow engine is the **architecturally correct choice** for structured, deterministic question flows with non-technical editing requirements.

**Status**: Accepted and validated through experimentation.
