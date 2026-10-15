# ADR-0002: Adopt Windsurf Workflow System for AI Agent Orchestration

**Status:** Implemented
**Date:** 2025-10-15
**Deciders:** Core Team
**Related:** [Windsurf Documentation](https://docs.windsurf.com/)

---

## Context

AI agents working on the mcp-web project need structured guidance for common operations like planning, implementation, testing, committing, and creating ADRs. Without standardized workflows, agents:

- Repeated similar tasks with inconsistent approaches
- Asked repetitive clarifying questions
- Lacked clear entry points for complex multi-step operations
- Had no systematic way to detect context and resume work

**Key Requirements:**

- Reduce cognitive load on users
- Provide consistent execution patterns
- Enable intelligent context detection
- Support workflow chaining for complex operations

**Constraints:**

- Must work within Windsurf IDE system
- Must be maintainable as markdown files
- Should minimize token usage while providing clarity
- Need balance between comprehensiveness and conciseness

---

## Decision

We will adopt a hierarchical Windsurf workflow system with a central orchestration workflow that intelligently routes to specialized workflows:

### Workflow Architecture

```text
/work (Central Orchestrator)
 ├─→ /plan (Research-based planning)
 ├─→ /implement (Test-first execution)
 ├─→ /commit (Git operations)
 ├─→ /new-adr (Architecture decisions)
 ├─→ /archive-initiative (Completion)
 ├─→ /run-tests (Testing guidance)
 └─→ /meta-analysis (Session review)
```

### Key Design Principles

1. **Single Entry Point:** `/work` as primary workflow, auto-detects context
2. **Intelligent Routing:** Analyze file system state to determine intent
3. **Batch Operations:** Use `mcp0_read_multiple_files()` for efficiency
4. **Focused Search:** Use targeted grep with file filters
5. **Minimal Tool Calls:** ≤5 calls for context detection
6. **Workflow Chaining:** Workflows can invoke each other
7. **Clear Separation:** Each workflow has single responsibility

### Implementation Strategy

- **Central orchestrator** (`/work`): Context detection and routing logic
- **Planning workflow** (`/plan`): Research, decomposition, initiative creation
- **Implementation workflow** (`/implement`): TDD, incremental validation
- **Supporting workflows**: Specialized operations (commit, ADR, tests, etc.)

---

## Alternatives Considered

### Alternative 1: Monolithic Single Workflow

**Approach:** One large workflow with all guidance

**Pros:**

- Simple mental model
- No routing logic needed
- Single source of truth

**Cons:**

- **❌ Token inefficiency:** Load all guidance even for simple tasks
- **❌ Maintenance burden:** Changes require updating massive file
- **❌ Cognitive overload:** Too much information at once
- **❌ No reusability:** Can't compose workflows

**Rejected because:** Token cost too high, not scalable

### Alternative 2: Pure Rule-Based System

**Approach:** Encode all guidance in `.windsurf/rules/`

**Pros:**

- Always loaded automatically
- No invocation needed
- Consistent application

**Cons:**

- **❌ Global token cost:** Rules loaded on every request
- **❌ Not task-specific:** Can't provide step-by-step guidance
- **❌ Limited structure:** Rules are guidelines, not procedures
- **❌ No state management:** Can't track multi-step progress

**Rejected because:** Rules are for standards, workflows are for processes

### Alternative 3: External Tool Integration

**Approach:** Use external tools (GitHub Actions, custom scripts)

**Pros:**

- More powerful
- Can integrate with CI/CD
- Language-agnostic

**Cons:**

- **❌ Not AI-native:** Doesn't integrate with Windsurf
- **❌ Complex setup:** Requires external infrastructure
- **❌ Context loss:** Agent can't directly observe execution
- **❌ Portability:** Depends on external systems

**Rejected because:** Windsurf workflows are AI-native and lightweight

---

## Consequences

### Positive

✅ **Reduced cognitive load:** Users just invoke `/work`, agent handles routing
✅ **Consistent execution:** Standardized approaches for common operations
✅ **Token efficiency:** Only load workflows actually needed
✅ **Composability:** Workflows can chain (plan → implement → commit)
✅ **Maintainability:** Each workflow is independently maintainable
✅ **Discovery:** Users can explore workflows in `.windsurf/workflows/`
✅ **Resumability:** Context detection enables cross-session continuation
✅ **Scalability:** Easy to add new workflows without affecting existing ones

### Negative

⚠️ **Initial complexity:** New users must learn workflow invocation
⚠️ **Routing logic maintenance:** Central workflow requires careful updates
⚠️ **Multiple files:** More files to maintain than monolithic approach
⚠️ **Testing overhead:** Need to validate workflow chaining behavior

### Neutral

🔸 **Markdown limitations:** Workflows are declarative, not executable code
🔸 **IDE dependency:** Only works within Windsurf IDE
🔸 **Documentation burden:** Each workflow needs comprehensive docs

---

## Implementation

### Phase 1: Core Workflows (Completed 2025-10-15)

✅ **Created workflows:**

- `/work` (9.6 KB) - Central orchestration with context detection
- `/plan` (12.2 KB) - Research-driven planning with @web search
- `/implement` (9.3 KB) - Test-first implementation with quality gates
- `/commit` (1.8 KB) - Git operations with validation
- `/new-adr` (2.9 KB) - ADR creation workflow
- `/archive-initiative` (2.2 KB) - Initiative archival
- `/run-tests` (3.7 KB) - Testing guidance
- `/meta-analysis` (8.6 KB) - Session review and improvement
- `/test-before-commit` (8.8 KB) - Incremental testing protocol

### Phase 2: Context Detection Logic

✅ **Implemented intelligent file system analysis:**

- Batch reads of active initiatives
- Git status and recent commit analysis
- TODO/FIXME marker detection
- Test result scanning
- Routing decision matrix

### Phase 3: Workflow Integration

✅ **Enabled workflow chaining:**

- `/work` → `/plan` → `/implement` → `/commit`
- Explicit workflow invocation within workflows
- Context passing between workflows

### Directory Structure

```text
.windsurf/
└── workflows/
 ├── work.md # Central orchestrator ⭐
 ├── plan.md # Research-based planning
 ├── implement.md # Test-first execution
 ├── commit.md # Git operations
 ├── new-adr.md # ADR creation
 ├── archive-initiative.md # Initiative archival
 ├── run-tests.md # Testing guidance
 ├── meta-analysis.md # Session review
 └── test-before-commit.md # Testing protocol
```

---

## Validation

### Success Metrics

**Target:** 70%+ autonomous task initiation from `/work`
**Target:** <30 seconds for context detection
**Target:** ≤5 tool calls for context gathering

### Monitoring

- Track `/work` invocation frequency
- Measure auto-route success rate
- Monitor user feedback on workflow clarity
- Analyze workflow chain patterns

### Review Schedule

- **Weekly:** Monitor usage patterns
- **Monthly:** Review routing accuracy and adjust logic
- **Quarterly:** Evaluate workflow effectiveness and consolidate if needed

---

## References

- [Windsurf Workflows Documentation](https://docs.windsurf.com/)
- [Agentic AI Workflows (2025)](https://devcom.com/tech-blog/ai-agentic-workflows/)
- [Claude Agent SDK Best Practices (2025)](https://skywork.ai/blog/claude-agent-sdk-best-practices-ai-agents-2025/)
- [AI Agent Planning (IBM, 2025)](https://www.ibm.com/think/topics/ai-agent-planning)
- hexacore-command project: Intelligent documentation search patterns

---

## Related ADRs

- **ADR-0003:** Documentation standards and structure
- **ADR-0004:** Testing strategy and workflows (future)

---

**Last Updated:** 2025-10-15
**Supersedes:** None
**Superseded By:** None
