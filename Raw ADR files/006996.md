---
id: "002"
title: Constitution and Instruction Separation
created: 2025-11-28
status: accepted
scope: philosophy
tags: [constitution, instruction, worker, separation, philosophy]
related: ["001", "003"]
supersedes: null
superseded-by: null
---

# ADR-002: Constitution and Instruction Separation

## Context

While designing the Constitution templates for Workers, we identified a conceptual ambiguity: the difference between "principles Workers must follow" and "responsibilities Workers must fulfill."

In the existing README documentation, Worker files (`.claude/agents/*.md`) were described as "HOW to behave - system prompt," while Constitution files were "WHAT principles." However, this distinction was not clearly defined, leading to potential confusion about what content belongs where.

We needed to establish a clear philosophical foundation that would:

1. Prevent mixing principles with instructions in templates
2. Guide placeholder design for each document type
3. Clarify the relationship between Constitution and Worker files

## Decision

We will **clearly separate Constitution and Instruction as distinct concepts** in the framework philosophy.

### Constitution (Law)

- **Essence**: Laws that Workers must obey
- **Nature**: Declarative (what should be)
- **Scope**: All Workers (global) or specific Workers (worker-specific)
- **Change**: Requires "constitutional amendment" (complex procedure)
- **Violation**: Results in Gate failure, rejection
- **Location**: `blueprint/constitutions/`

### Instruction (Responsibility)

- **Essence**: Responsibilities assigned to specific Workers
- **Nature**: Imperative (what to do, how to do)
- **Scope**: Specific Worker only
- **Change**: Relatively flexible task redefinition
- **Non-fulfillment**: Results in rework request
- **Location**: `.claude/agents/` (Worker definition files)

### Conceptual Model

```
Worker Runtime
├── Constitution (Law to obey)
│   ├── Principles
│   ├── Boundaries
│   ├── Quality Standards
│   └── Violations → Gate Fail
│
├── Instruction (Responsibility to fulfill)
│   ├── Role Definition
│   ├── Workflow
│   ├── Output Format
│   └── Non-fulfillment → Rework
│
└── Gate Validation (Constitution compliance check)
```

### Analogy

| Concept | Real-world Analogy |
|---------|-------------------|
| Constitution | National law that all citizens must follow |
| Instruction | Job description assigning specific duties |
| Worker | Employee who obeys laws AND fulfills duties |
| Gate | Court that judges law compliance |

## Rationale

1. **Prevents Conceptual Mixing**: Without clear separation, Constitution templates might include instruction-like content ("do X this way") and Worker files might include principle-like content ("always follow Y").

2. **Guides Placeholder Design**: Each document type needs different placeholders:
   - Constitution: `[DECIDE: quality-threshold]`, `[INFER: tech-stack]`
   - Instruction: `[DEFINE: workflow-steps]`, `[SPECIFY: output-format]`

3. **Reflects Natural Hierarchy**: Laws are foundational and rarely change; instructions are operational and can be adjusted. This mirrors real-world governance.

4. **Enables Proper Validation**: Gate validates Constitution compliance (binary: pass/fail), while Instruction fulfillment is validated by output quality.

5. **Clarifies Worker Loading**: Workers load both Constitution (for constraints) and Instruction (for behavior), understanding each serves a different purpose.

## Consequences

### Positive

- Clear guidance for template authors on what content belongs where
- Placeholder systems can be designed specifically for each document type
- Workers understand they have two sources: laws to obey, duties to fulfill
- Gate validation scope is clearly defined (Constitution only)
- Framework philosophy is coherent and explainable

### Negative

- Two separate conceptual models to maintain
- Workers must reference two document types
- Potential overhead in ensuring consistency between Constitution and Instruction

### Trade-offs

- **Complexity vs Clarity**: Adding another concept increases framework complexity but significantly improves clarity of purpose for each document type.

## Alternatives Considered

### Single Document Approach

Combine Constitution and Instruction into a single Worker definition file.

**Rejected because**:
- Mixes declarative (principles) with imperative (instructions)
- Makes it unclear what Gates should validate
- Violates separation of concerns

### Constitution-Only Approach

Expand Constitution to include instruction-like content.

**Rejected because**:
- Constitution should remain declarative and stable
- Instructions need more flexibility for operational changes
- Would bloat Constitution files beyond token budget

### Instruction-Only Approach

Put everything in Worker instruction files, treating principles as instructions.

**Rejected because**:
- Principles are not instructions; they are constraints
- Would lose the hierarchical relationship (base + worker-specific)
- Gates need a separate "law" to validate against
