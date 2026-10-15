# ADR-001: Three-Level Architecture for SDD Toolkit

**Status**: Accepted  
**Date**: 2025-01-05  
**Deciders**: VSALMEID, forge-sdd-toolkit core team  
**Technical Story**: Foundation architecture for forge-sdd-toolkit v0.1.0

---

## Context and Problem Statement

We need to design an architecture for the forge-sdd-toolkit that enables GitHub Copilot to:

1. **Orchestrate** the complete 6-stage SDD lifecycle (IDEATE → ARCHITECT → PLAN → IMPLEMENT → TEST → OPERATE)
2. **Guide users** through Forge-specific decisions (modules, UI approaches, storage, security)
3. **Provide implementations** ranging from abstract patterns to concrete production-ready code
4. **Scale gracefully** as we add more Forge modules and use cases

The challenge: How do we structure knowledge so that Copilot can operate at different levels of abstraction depending on the lifecycle stage and user needs?

**Key Requirements**:
- Support both high-level orchestration and deep technical expertise
- Enable reusability across different Forge modules and products
- Allow progressive disclosure (simple → intermediate → advanced)
- Maintain clear separation between workflow control and domain knowledge

---

## Decision Drivers

### Primary Drivers

1. **Separation of Concerns**: Orchestration logic separate from domain knowledge
2. **Progressive Disclosure**: Users shouldn't be overwhelmed with details upfront
3. **Reusability**: Common patterns should be defined once, referenced many times
4. **Scalability**: Architecture must support 10+ Forge modules × 5+ products
5. **Maintainability**: Changes to one component shouldn't break others
6. **Copilot Effectiveness**: Structure must align with LLM context window optimization

### Secondary Drivers

7. **Discoverability**: Easy to find relevant knowledge for specific use cases
8. **Completeness**: Coverage from "I have an idea" to "deployed in production"
9. **Flexibility**: Support different learning styles and expertise levels
10. **Traceability**: Clear lineage from requirements → decisions → code

---

## Considered Options

### Option 1: Flat Structure (Rejected)

```
prompts/
├── forge-ideate.md
├── forge-architect.md
├── forge-plan.md
├── forge-implement.md
├── forge-test.md
├── forge-operate.md
├── jira-issue-panel-simple.md
├── jira-issue-panel-api.md
├── jira-issue-panel-storage.md
├── confluence-macro-static.md
├── confluence-macro-dynamic.md
└── ... (100+ files as we scale)
```

**Pros**:
- ✅ Simple mental model
- ✅ Easy to navigate initially
- ✅ No hierarchy to understand

**Cons**:
- ❌ Doesn't scale (100+ files in one directory)
- ❌ No clear distinction between orchestration and knowledge
- ❌ Hard to find specific implementations
- ❌ Duplication across similar use cases
- ❌ Difficult to maintain consistency

**Verdict**: ❌ Rejected - Doesn't meet scalability requirements

---

### Option 2: Two-Level (Prompts + Examples) (Rejected)

```
prompts/
├── lifecycle/
│   ├── forge-ideate.md
│   ├── forge-architect.md
│   └── ...
└── examples/
    ├── jira/
    │   ├── issue-panel-example-1.md
    │   ├── issue-panel-example-2.md
    │   └── ...
    └── confluence/
        ├── macro-example-1.md
        └── ...
```

**Pros**:
- ✅ Clear separation: workflows vs examples
- ✅ Better organization than flat
- ✅ Easier to find lifecycle prompts

**Cons**:
- ❌ No middle layer for reusable patterns
- ❌ Examples contain duplicated pattern explanations
- ❌ Hard to reuse common knowledge (e.g., "how to choose UI Kit vs Custom UI")
- ❌ Copilot has to choose between orchestration or deep dive (no middle ground)

**Verdict**: ❌ Rejected - Missing crucial middle layer for patterns

---

### Option 3: Three-Level Architecture (ACCEPTED ✅)

```
structure/
├── Level 1: Prompts (Orchestrators)
│   ├── commands/
│   │   ├── forge-ideate.md      # High-level workflow control
│   │   ├── forge-architect.md   # Decision orchestration
│   │   ├── forge-plan.md        # Backlog generation
│   │   ├── forge-implement.md   # Code generation orchestration
│   │   ├── forge-test.md        # Test suite generation
│   │   └── forge-operate.md     # Deployment orchestration
│   └── base/
│       ├── system-prompt.md     # Core capabilities
│       └── decision-framework.md # Universal decision logic
│
├── Level 2: Templates (Knowledge Base)
│   ├── documents/
│   │   ├── specification-template.md    # IDEATE output
│   │   ├── ADD-template.md              # ARCHITECT output
│   │   ├── implementation-plan-template.md  # PLAN output
│   │   └── test-plan-template.md        # TEST output
│   └── forge-modules/
│       ├── jira/
│       │   ├── issue-panel-template.md  # Patterns, decision matrices
│       │   ├── global-page-template.md
│       │   └── ...
│       ├── confluence/
│       │   ├── macro-template.md
│       │   └── ...
│       └── ...
│
└── Level 3: Specializations (Expert Implementations)
    ├── jira/
    │   ├── issue-panel/
    │   │   ├── github-pr-status.md      # Full implementation
    │   │   ├── deployment-dashboard.md
    │   │   └── ...
    │   ├── global-page/
    │   │   └── analytics-dashboard.md
    │   └── ...
    └── confluence/
        ├── macro/
        │   ├── jira-roadmap-embed.md
        │   └── ...
        └── ...
```

**Pros**:
- ✅ **Clear Separation**: Orchestration (L1) → Patterns (L2) → Implementations (L3)
- ✅ **Progressive Disclosure**: Start broad, drill down as needed
- ✅ **Maximum Reusability**: Common patterns in L2 referenced by many L3 specializations
- ✅ **Scalability**: Can add 100+ L3 specializations without cluttering L1/L2
- ✅ **Copilot-Friendly**: Each level has distinct context size and purpose
- ✅ **Maintainability**: Update pattern once (L2), benefits all specializations (L3)
- ✅ **Discoverability**: Clear path: Lifecycle → Module → Use Case
- ✅ **Completeness**: Covers full spectrum from idea to deployment

**Cons**:
- ⚠️ More complex mental model (3 levels to understand)
- ⚠️ Initial setup effort higher (must populate all 3 levels)
- ⚠️ Risk of cross-level inconsistencies if not careful

**Verdict**: ✅ **ACCEPTED** - Pros far outweigh cons

---

## Decision Outcome

**Chosen Option**: **Three-Level Architecture**

### Level 1: Prompts (Orchestrators)

**Purpose**: Control SDD lifecycle flow and coordinate lower levels

**Content**:
- Executable instructions for GitHub Copilot
- Step-by-step procedures for each lifecycle stage
- References to Level 2 templates and Level 3 specializations
- Quality gates and validation checkpoints

**Characteristics**:
- 300-650 lines per prompt
- "You are..." role definitions
- Procedural (do this, then that)
- References: many → few (orchestrates others)

**Example**: `forge-architect.md` orchestrates module selection, UI decisions, storage strategy by referencing `issue-panel-template.md` (L2)

---

### Level 2: Templates (Knowledge Base)

**Purpose**: Reusable patterns and decision frameworks

**Content**:
- Architecture decision matrices (UI Kit vs Custom UI)
- Implementation patterns (5 patterns per module)
- Performance/security best practices
- Manifest configurations
- Testing strategies

**Characteristics**:
- 400-800 lines per template
- Educational tone
- Decision trees and comparison tables
- References: few → many (referenced by L1 and L3)

**Example**: `jira/issue-panel-template.md` provides 5 implementation patterns used by multiple specializations

---

### Level 3: Specializations (Expert Implementations)

**Purpose**: Production-ready, copy-paste-adapt code for specific use cases

**Content**:
- Complete TypeScript/JavaScript implementations
- Full `manifest.yml` configurations
- Unit and integration tests
- Deployment guides
- Performance metrics
- ROI analysis
- Troubleshooting guides

**Characteristics**:
- 700-1000+ lines per specialization
- Code-heavy (60-70% code, 30-40% docs)
- Specific use case focus
- References: many → none (leaf nodes)

**Example**: `jira/issue-panel/github-pr-status.md` complete app with 490 lines of production TypeScript

---

## Information Flow

### Top-Down (Orchestration Flow)

```
User Request
    ↓
L1: forge-ideate → Specification Document
    ↓
L1: forge-architect → Consults L2: issue-panel-template.md
    ↓
L1: forge-architect → Presents UI Kit vs Custom UI options
    ↓
User decides: Custom UI
    ↓
L1: forge-plan → Creates backlog
    ↓
L1: forge-implement → References L3: github-pr-status.md
    ↓
L1: forge-implement → Generates code based on specialization
    ↓
Working Forge App
```

### Bottom-Up (Knowledge Discovery)

```
Developer needs Jira integration
    ↓
Browses L2: jira/issue-panel-template.md
    ↓
Sees 5 patterns, identifies "External API Integration"
    ↓
Follows reference to L3: github-pr-status.md
    ↓
Copies and adapts production code
```

### Horizontal (Learning Path)

```
Beginner: L1 prompts (guided workflow)
    ↓
Intermediate: L2 templates (understand patterns)
    ↓
Advanced: L3 specializations (production reference)
```

---

## Architectural Principles

### 1. Single Responsibility

Each level has ONE primary purpose:
- L1: Orchestrate
- L2: Educate
- L3: Implement

### 2. DRY (Don't Repeat Yourself)

Common knowledge lives in L2, not duplicated in L3.

**Example**: "UI Kit vs Custom UI" decision matrix is in `issue-panel-template.md` (L2), referenced by all issue panel specializations (L3).

### 3. Progressive Enhancement

Each level adds specificity:
- L1: "What to do" (orchestration)
- L2: "How to do it" (patterns)
- L3: "Here's the code" (implementation)

### 4. Context Optimization

Levels designed for Copilot's context window:
- L1: Large context (orchestrates whole workflow)
- L2: Medium context (pattern reference)
- L3: Narrow context (specific implementation)

### 5. Traceability

Every artifact traces back:
- L3 code → L2 pattern → L1 decision → Specification requirement

---

## Consequences

### Positive

✅ **Scalability**: Can grow to 100+ specializations without chaos  
✅ **Maintainability**: Update pattern once, benefits all implementations  
✅ **Reusability**: Common knowledge shared across use cases  
✅ **Discoverability**: Clear navigation path  
✅ **Completeness**: Coverage from idea to production  
✅ **Quality**: Consistent patterns across all implementations  
✅ **Learning Curve**: Progressive disclosure reduces cognitive load  

### Negative

⚠️ **Complexity**: Contributors must understand 3-level model  
⚠️ **Initial Effort**: Higher setup cost vs flat structure  
⚠️ **Cross-Level Sync**: Risk of inconsistencies if not disciplined  

### Mitigation Strategies

1. **Documentation**: Clear explanation in README.md and CONTRIBUTING.md
2. **Templates**: Provide templates for each level
3. **Validation**: JSON schemas enforce structure
4. **Reviews**: Check cross-level consistency in PR reviews
5. **Examples**: Reference implementations guide contributors

---

## Validation

### Success Metrics (v0.1.0)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| L1 Prompts Created | 6 | 6 | ✅ |
| L2 Templates Created | 5+ | 5 | ✅ |
| L3 Specializations | 1+ | 1 | ✅ |
| Lines of Code (Total) | 5000+ | 7800+ | ✅ |
| Cross-Level References | 10+ | 15+ | ✅ |

### Qualitative Validation

✅ **Copilot Integration**: Prompts successfully orchestrate workflow  
✅ **User Feedback**: Clear separation praised in early testing  
✅ **Maintainability**: Pattern update in L2 automatically improves L3 references  
✅ **Scalability Test**: Adding new Jira module took <2 hours  

---

## Related Decisions

- **ADR-002**: SDD Methodology Adoption (explains WHY we need orchestration)
- **ADR-003**: User-Driven Architectural Decisions (explains HOW L2 presents choices)
- **Future ADR-004**: CLI Design Philosophy (explains WHEN to use CLI vs prompts)

---

## References

### Internal
- [SDD Methodology](../../SDD_METHODOLOGY.md)
- [Lifecycle Stages](../../LIFECYCLE_STAGES.md)
- [Contributing Guide](../../CONTRIBUTING.md)

### External
- [Forge Platform Documentation](https://developer.atlassian.com/platform/forge/)
- [GitHub Copilot Architecture](https://github.blog/2023-05-17-inside-github-building-copilot/)
- [ADR Template by Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)

### Inspiration
- **C4 Model**: Hierarchical architectural diagrams (context → containers → components → code)
- **Information Architecture**: Progressive disclosure in UX design
- **Domain-Driven Design**: Separation between domain logic and application orchestration

---

## Implementation Notes

### Directory Structure

```bash
structure/
├── prompts/
│   ├── commands/          # L1: 6 lifecycle prompts
│   └── base/              # L1: System prompts
├── templates/
│   ├── documents/         # L2: Document templates (4)
│   └── forge-modules/     # L2: Module templates (5+)
└── specializations/
    ├── jira/              # L3: Jira implementations
    ├── confluence/        # L3: Confluence implementations
    └── ...                # L3: Other products
```

### Naming Conventions

- **L1 Files**: `forge-{stage}.md` (e.g., `forge-architect.md`)
- **L2 Module Templates**: `{module}-template.md` (e.g., `issue-panel-template.md`)
- **L3 Specializations**: `{use-case}.md` (e.g., `github-pr-status.md`)

### Cross-Level References

Use relative paths:
```markdown
<!-- L1 referencing L2 -->
See [Jira Issue Panel Template](../templates/forge-modules/jira/issue-panel-template.md)

<!-- L2 referencing L3 -->
For complete example, see [GitHub PR Status](../specializations/jira/issue-panel/github-pr-status.md)

<!-- L3 referencing L2 -->
Based on patterns from [Issue Panel Template](../../templates/forge-modules/jira/issue-panel-template.md)
```

---

## Evolution Path

### v0.1.0 (Current)
- ✅ Foundation: 6 L1 prompts, 5 L2 templates, 1 L3 specialization

### v0.2.0 (Planned)
- 🔄 Add 3 more L3 specializations (Jira Global Page, Confluence Macro, JSM Portal)
- 🔄 Add L2 templates for Bitbucket and Compass

### v1.0.0 (Future)
- 📋 10+ L3 specializations across all Forge products
- 📋 Automated cross-level consistency validation
- 📋 Community contribution guidelines refined

---

**Last Updated**: 2025-01-05  
**Status**: Living Document - Will evolve as toolkit grows  
**Feedback**: Open GitHub issue with label `adr-discussion`
