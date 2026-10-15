# Lifecycle Hook Architecture Decision

## Purpose
Document the decision to add lifecycle hook infrastructure to Patinox V2 architecture, enabling event-driven middleware patterns without premature implementation.

## Classification
- **Domain:** Architecture Decision
- **Stability:** Static (architectural foundation)
- **Abstraction:** Structural
- **Confidence:** High (validated by external experience)

## Decision

**APPROVED**: Add lifecycle hook architecture as Layer 2.5
**Date**: 2025-10-16
**Authorized By**: Project lead
**Status**: APPROVED - Implementation scheduled for Week 4 (late October)

## Context

### External Catalyst

LangChain V1 announced agent middleware with 6 lifecycle hooks:
- `📂 before_agent` — Load files, validate input
- `✂️ before_model` — Summarize conversations, trim messages
- `♻️ wrap_model_call` — Dynamic prompts, model, tools
- `🛠️ wrap_tool_call` — Tool retries, error handling
- `🧑 after_model` — Human in the loop
- `🛡️ after_agent` — Save results, final guardrails

### Validated Pain Points

**Project lead has experienced pain in other agent frameworks** where lack of intervention points caused:
- Inability to add retry logic without rewriting core loops
- No clean way to add human-in-the-loop approval
- Difficult to add telemetry/logging across all operations
- Hard to implement context window management
- Challenge adding safety validations post-response

**This is validated pain from production use**, not speculative features.

### Current V2 Architecture State

**Layer 1 Complete** (Week 1):
- ~200 line minimal agent core
- Builder pattern API
- Working agents with real LLM providers

**Layer 2 In Progress** (Weeks 2-3):
- Real usage validation (2 agents built)
- First plugin designed (Tool Context Helper)
- Pain point analysis driving features

**Current Risk**: V2 minimal architecture might ossify before adding hook points, requiring significant refactoring later.

## The Problem

### Without Lifecycle Hooks

Current `Agent::run()` method (src/agent.rs:105-181) is monolithic:
```rust
async fn run(&self, input: String) -> Result<String> {
    // Direct provider call - no interception point
    let response = provider.complete(messages, tools).await?;

    // Direct tool execution - no interception point
    let result = tool.execute(args)?;

    // Direct return - no post-processing point
    Ok(result)
}
```

**Consequences:**
- Can't add retry logic without modifying core
- Can't add HITL approval without rewriting loop
- Can't add context trimming without forking messages
- Can't add telemetry without touching every call site
- Can't add safety validation without result interception

### Known Use Cases (From External Experience)

**before_agent**: Input sanitization, rate limiting, context loading
**before_model**: Context window management, prompt injection, message compression
**wrap_model_call**: Retry with backoff, fallback providers, caching, telemetry, **bicameral refinement loops**
**after_model**: HITL approval, safety validation, response formatting, **bicameral critic evaluation**
**wrap_tool_call**: Tool retry logic, permission checks, audit logging, dry-run mode
**after_agent**: Result persistence, notifications, metrics collection

**Key Architectural Pattern Enabled**: **Bicameral Mind (Creator-Critic Separation)**
- Validated production pattern: Separate creator (generates) from critic (evaluates)
- Critical insight: Critic must NOT have created the work (requires separate model/context)
- Result: Significantly better quality than combined creator+critic prompt to single model
- Implementation: `after_model` hook intercepts creator output, separate critic model evaluates
- Use cases: Code review, content writing, decision making, creative work
- See [lifecycle-hook-use-cases.md UC-4.5](../planning/lifecycle-hook-use-cases.md) for full pattern

## The Solution

### Layer 2.5: Lifecycle Hook Architecture

**Scope**: Define hook infrastructure, **not** implementations

**What Gets Built (Week 4)**:
1. `AgentLifecycle` trait with 6 hook points
2. Agent hook registration (`.with_lifecycle()`)
3. Hook calling infrastructure in `run()`
4. Default implementations (zero-cost passthrough)

**What Doesn't Get Built**:
- No concrete hook implementations (deferred to Layer 3+)
- No specific middleware (retry, HITL, telemetry)
- No complex hook composition (wait for need)

### Architecture Design

#### 1. Lifecycle Trait (src/lifecycle.rs)

```rust
/// Agent lifecycle hooks - all methods optional with default passthroughs
#[async_trait]
pub trait AgentLifecycle: Send + Sync {
    /// Called before agent starts processing
    async fn before_agent(&self, input: &str) -> Result<String> {
        Ok(input.to_string()) // Default: passthrough
    }

    /// Called before sending messages to model
    async fn before_model(&self, messages: Vec<Message>) -> Result<Vec<Message>> {
        Ok(messages) // Default: passthrough
    }

    /// Wraps the model call (retry, logging, fallback)
    async fn wrap_model_call<F, Fut>(&self, f: F) -> ProviderResult<ProviderResponse>
    where
        F: FnOnce() -> Fut + Send,
        Fut: Future<Output = ProviderResult<ProviderResponse>> + Send,
    {
        f().await // Default: direct call
    }

    /// Called after model responds, before tool execution
    async fn after_model(&self, response: &ProviderResponse) -> Result<HookAction> {
        Ok(HookAction::Continue) // Default: continue
    }

    /// Wraps each tool call (retry, logging, validation)
    async fn wrap_tool_call<F, Fut>(&self, name: &str, f: F) -> ToolResult
    where
        F: FnOnce() -> Fut + Send,
        Fut: Future<Output = ToolResult> + Send,
    {
        f().await // Default: direct call
    }

    /// Called after agent completes
    async fn after_agent(&self, result: &str) -> Result<String> {
        Ok(result.to_string()) // Default: passthrough
    }
}

/// Action to take after a hook
pub enum HookAction {
    Continue,               // Proceed normally
    Approve,                // Explicit approval (HITL)
    Reject(String),         // Reject with reason
    Modify(ProviderResponse), // Modify the response
}
```

#### 2. Agent Update (src/agent.rs)

```rust
pub struct Agent {
    config: AgentConfig,
    tools: HashMap<String, Arc<dyn Tool>>,
    provider: Option<Box<dyn LLMProvider>>,
    lifecycle: Vec<Arc<dyn AgentLifecycle>>, // NEW: Hook chain
}

impl Agent {
    /// Add a lifecycle hook (builder pattern)
    pub fn with_lifecycle(mut self, hook: impl AgentLifecycle + 'static) -> Self {
        self.lifecycle.push(Arc::new(hook));
        self
    }
}
```

#### 3. Hook Integration in run() Method

```rust
async fn run(&self, input: String) -> Result<String> {
    // Hook 1: before_agent
    let mut input = input;
    for hook in &self.lifecycle {
        input = hook.before_agent(&input).await?;
    }

    // Build messages...
    let mut messages = vec![system_prompt, user_message];

    for iteration in 0..max_iterations {
        // Hook 2: before_model
        for hook in &self.lifecycle {
            messages = hook.before_model(messages).await?;
        }

        // Hook 3: wrap_model_call
        let response = if self.lifecycle.is_empty() {
            // Fast path: no hooks
            provider.complete(messages.clone(), tool_defs.clone()).await?
        } else {
            // Call through hook chain
            self.call_with_model_wrapper(|| {
                provider.complete(messages.clone(), tool_defs.clone())
            }).await?
        };

        // Hook 4: after_model
        for hook in &self.lifecycle {
            match hook.after_model(&response).await? {
                HookAction::Reject(reason) => return Err(reason.into()),
                HookAction::Modify(new_resp) => response = new_resp,
                _ => {}
            }
        }

        // Tool execution...
        match response {
            ProviderResponse::ToolCalls(calls) => {
                for call in calls {
                    let tool = self.tools.get(&call.name)?;

                    // Hook 5: wrap_tool_call
                    let result = if self.lifecycle.is_empty() {
                        tool.execute(call.arguments)?
                    } else {
                        self.call_with_tool_wrapper(&call.name, || {
                            tool.execute(call.arguments.clone())
                        }).await?
                    };

                    messages.push(tool_result_message);
                }
            }
            ProviderResponse::Text(text) => {
                result = text;
                break;
            }
        }
    }

    // Hook 6: after_agent
    for hook in &self.lifecycle {
        result = hook.after_agent(&result).await?;
    }

    Ok(result)
}
```

### Performance Considerations

**Zero-cost when unused:**
- Empty lifecycle vec → direct calls (fast path)
- No heap allocations if no hooks
- No virtual dispatch overhead for simple agents

**Minimal cost when used:**
- One vec iteration per hook point
- Arc clone for hook reference (cheap)
- Async overhead only for hooks that need it

**Benchmark target**: < 5% overhead with 1 hook, < 10% with 5 hooks

## Why Layer 2.5 (Not Layer 3)?

### Justification for Early Addition

**Validated Need**:
- ✅ External production experience confirms pain
- ✅ Known use cases from real agent development
- ✅ LangChain validation (industry leader chose this model)

**Low Cost**:
- ✅ ~200-300 lines of code (trait + integration)
- ✅ 1-2 days implementation effort
- ✅ No external dependencies
- ✅ No breaking changes to existing API

**Prevents Regret**:
- ✅ Adding later requires refactoring monolithic run()
- ✅ Better to add injection points before code ossifies
- ✅ Traits are cheap, implementations are expensive
- ✅ Opt-in design doesn't violate minimal-first

**Still Minimal-First Compliant**:
- ✅ Default implementations (agents work without hooks)
- ✅ No concrete middleware until pain validated
- ✅ Zero runtime cost if unused
- ✅ Doesn't complicate simple agent creation

### Why Not Wait for Layer 3?

**Refactoring Cost**: Current `run()` is monolithic. Adding hooks later means:
- Breaking up method into smaller pieces
- Risk of regression bugs
- Potential API changes
- Testing overhead

**Architecture Validation**: Better to validate hook points now with Layer 2 agents than discover they're wrong in Layer 3.

**V1 Import Path**: When importing V1 Tower middleware (Layer 4), hook architecture needs to exist.

## Implementation Plan

### Week 4 (October 24-31, 2025) - Task V2-ARCH-001

**Deliverables**:
1. Create `src/lifecycle.rs` with `AgentLifecycle` trait
2. Update `src/agent.rs` with hook registration and calling
3. Add comprehensive tests for hook execution order
4. Document hook architecture in rustdoc
5. Create examples showing hook usage patterns
6. Benchmark zero-hook vs multi-hook overhead

**Acceptance Criteria**:
- [ ] All 6 hooks defined with default implementations
- [ ] Can register hooks via `.with_lifecycle(hook)`
- [ ] Agent works identically with 0 hooks (regression tests pass)
- [ ] Hook chain execution order verified (integration test)
- [ ] < 5% overhead with 1 hook (benchmark)
- [ ] Examples compile and run

### Layer 3+ (November - Q1 2026) - Implement Concrete Hooks

Build **specific hooks** only when validated pain emerges:

**Priority 1** (Layer 2/3 - pain likely soon):
- Retry logic wrapper (wrap_model_call, wrap_tool_call)
- Logging/telemetry wrapper (all hooks)
- Input validation (before_agent)
- **Bicameral critic hook (after_model)** - validated high-value pattern

**Priority 2** (Layer 3 - Month 2+):
- Context window management (before_model)
- HITL approval workflow (after_model)
- Result formatting (after_agent)
- **Bicameral refinement loops (wrap_model_call)** - advanced iteration

**Priority 3** (Layer 4 - Q1 2026):
- Import V1 Tower middleware as hooks
- MAPE-K monitoring via hooks
- OpenTelemetry integration via hooks
- Multi-critic systems with consensus mechanisms

## Import Path from V1 Archive

V1 research phase already explored middleware patterns:

**Available for Import**:
- `archive/v1-research/elements/architecture_overview.md` - Tower patterns
- `archive/v1-research/implementations/tower-validation-pipeline-implementation.md`
- `archive/v1-research/elements/async_human_in_loop.md` - HITL via hooks
- `archive/v1-research/elements/monitoring_strategy.md` - MAPE-K hooks

**Import Strategy**:
1. V2 Layer 2.5 establishes hook architecture
2. Layer 3 builds simple hook implementations (retry, logging)
3. Layer 4 imports proven V1 Tower middleware as sophisticated hooks
4. Hooks compose naturally (Tower layers map to AgentLifecycle impls)

## Alternatives Considered

### Alternative 1: Wait Until Layer 3

**Rejected because**:
- Refactoring `run()` later is riskier
- External experience validates need now
- Trait definition is cheap insurance

### Alternative 2: Build Concrete Hooks Immediately

**Rejected because**:
- Violates minimal-first philosophy
- Don't know which hooks needed most
- Better to wait for Layer 2+ usage data

### Alternative 3: Use Tower Middleware Directly

**Rejected for now because**:
- Too sophisticated for Layer 2
- Learning curve for users
- Can still import Tower in Layer 4 as hook implementations

### Alternative 4: Event Bus Architecture

**Rejected because**:
- More complex than needed
- Runtime overhead (message passing)
- Harder to reason about control flow

## Risks and Mitigation

### Risk: Hooks Used Prematurely

**Likelihood**: Medium
**Impact**: Medium (complexity creep)
**Mitigation**:
- Document "don't use unless you feel pain"
- Examples show simple agents first
- Hook implementations gated to Layer 3+

### Risk: Hook API Needs Changes Later

**Likelihood**: Low
**Impact**: Medium (breaking changes)
**Mitigation**:
- Start with proven pattern (LangChain validation)
- Use external experience to validate hook points
- Version hooks as experimental until Layer 3

### Risk: Performance Overhead

**Likelihood**: Low
**Impact**: Low (benchmark targets established)
**Mitigation**:
- Fast path for zero hooks
- Benchmark regression tests
- Profile before/after

## Success Criteria

### Week 4 (Architecture Completion)
- [ ] Trait compiles with all 6 hooks
- [ ] Integration tests pass (hook order, defaults)
- [ ] Zero regression in no-hook case
- [ ] Performance benchmarks pass (< 5% overhead)
- [ ] Documentation complete

### Layer 3+ (Hook Utilization)
- [ ] First concrete hook solves validated pain
- [ ] Hook reduces boilerplate in 3+ agents
- [ ] No architectural regret
- [ ] V1 imports fit cleanly

## Documentation Impact

### Files to Create
- `context-network/decisions/lifecycle-hook-architecture.md` (this file)
- `context-network/planning/lifecycle-hook-use-cases.md` (use case catalog)
- `src/lifecycle.rs` (trait definition with rustdoc)
- `examples/lifecycle_hooks.rs` (usage example)

### Files to Update
- `context-network/planning/roadmap.md` (add Layer 2.5)
- `context-network/backlog/by-status/ready.md` (add V2-ARCH-001 task)
- `CLAUDE.md` (reference hook architecture pattern)

## Relationships
- **Inspired By**: LangChain V1 agent middleware announcement
- **Validates**: External agent framework production experience
- **Enables**: Layer 3 reasoning patterns, Layer 4 V1 imports
- **Supports**: `context-network/planning/roadmap.md` - adds Layer 2.5
- **Follows**: V2 minimal-first philosophy (traits before implementations)

## Metadata
- **Created**: 2025-10-16
- **Decision Type**: Architecture Addition
- **Impact**: Medium (new capability, opt-in)
- **Effort**: Low (~2-3 days implementation)
- **Risk**: Low (default implementations, zero-cost if unused)
- **Status**: APPROVED - Ready for Week 4 implementation

## Change History
- 2025-10-16: Created decision record based on LangChain V1 middleware and external experience validation
- 2025-10-16: Added bicameral mind pattern as key architectural use case (UC-4.5) - validated production quality improvement
