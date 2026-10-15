---
id: "004"
title: Marker Convention System
created: 2025-12-05
status: accepted
scope: design
tags: [marker, convention, annotation, directive, framework-wide]
related: ["002", "003"]
supersedes: "003"
superseded-by: null
---

# ADR-004: Marker Convention System

## Context

ADR-003 introduced a Template Annotation System with four markers (`[FIXED]`, `[INFER]`, `[DECIDE]`, `[ADAPT]`) specifically designed for template initialization. However, practical usage revealed limitations:

1. **Scope too narrow**: Markers were confined to "template initialization" but proved useful in broader contexts (specifications, discussions, any document requiring user decisions).

2. **Two marker systems emerged**:
   - Template markers: `[FIXED]`, `[INFER]`, `[DECIDE]`, `[ADAPT]`
   - Annotation markers: `[D-NNN]`, `[C-NNN]`, `[Q-NNN]`, `[A-NNN]`

3. **ADAPT redundancy**: `[ADAPT: condition]` (conditional inclusion) overlaps with `[INFER]` (analyze and fill). Both require analysis; ADAPT's binary include/exclude can be handled by INFER or explicit `[DECIDE]`. No practical usage found in the codebase.

4. **Propagation problem**: ADR documents are not copied to project instances, so marker conventions had no delivery mechanism to target projects.

5. **Unclear ownership**: Which Workers should know which markers? All Workers? Only specific ones?

## Decision

We establish a **Marker Convention System** that:

1. **Renames and simplifies Template Markers to Directive Markers** - three markers usable by any Worker in any context, removing redundant `[ADAPT]`.

2. **Scopes Annotation Markers to Annotator + Orchestrator** - other Workers consume the Reference Section output, not the marker rules.

3. **Embeds Directive Markers in Constitution (base.md)** - ensuring propagation to all project instances.

4. **Keeps Annotation Markers in Worker Instructions** - Annotator holds detailed rules, Orchestrator understands meanings for result interpretation.

### Directive Markers (Framework-wide)

All Workers may use these markers in any document:

| Marker | Purpose | Worker Action |
|--------|---------|---------------|
| `[FIXED]` | Protected content | Do NOT modify without explicit user confirmation |
| `[INFER: topic]` | Derivable from analysis | Analyze and fill without asking user |
| `[DECIDE: topic]` | Requires user judgment | Ask user before proceeding |

**Location**: Constitution `base.md` (Framework Core section)

### Annotation Markers (Scoped)

Used for discussion document refinement:

| Marker | Meaning |
|--------|---------|
| `[D-NNN]` | Decision made |
| `[C-NNN]` | Constraint identified |
| `[Q-NNN]` | Open question |
| `[A-NNN]` | Alternative considered |

**Who knows**:
- **Annotator**: Full rules (creation, numbering, placement)
- **Orchestrator**: Meaning interpretation (for result handling)
- **Other Workers**: Reference Section consumption only (no marker rules needed)

### Cross-usage

Annotator may use `[DECIDE: topic]` when uncertain about classification or intent during annotation. This bridges the two marker systems.

## Rationale

1. **"Context is Precious" alignment**: Directive Markers in Constitution means all Workers load them once. Annotation Markers scoped to 2 Workers reduces unnecessary context loading for others.

2. **Practical propagation**: Constitution is copied to project instances; ADRs are not. Embedding in Constitution solves the delivery problem.

3. **Role clarity**: Annotator creates markers, Orchestrator interprets results, other Workers consume Reference Section. Clear ownership prevents duplication.

4. **Framework-wide utility**: `[DECIDE]` is useful beyond templates - Specifier uses it for ambiguous requirements, Annotator for uncertain classifications, any Worker for user judgment needs.

## Consequences

### Positive

- Directive Markers available to all Workers in any context
- Annotation Markers scoped appropriately (no unnecessary knowledge loading)
- Marker conventions propagate to project instances via Constitution
- Clear ownership: who creates vs who consumes
- `[DECIDE]` becomes a universal "ask user" mechanism

### Negative

- ADR-003 is superseded (requires FrontMatter update)
- Two marker categories to understand (Directive vs Annotation)
- Constitution grows slightly with Directive Markers section

### Trade-offs

- **Scoping vs Uniformity**: We chose scoped knowledge (Annotation Markers to 2 Workers) over uniform knowledge (all Workers know all markers) to preserve context.

## Alternatives Considered

### All Markers in Constitution

Put both Directive and Annotation Markers in base.md.

**Rejected because**: Annotation Markers are specialized for discussion refinement. Other Workers don't need creation rules, only the Reference Section output.

### All Markers in ADR Only

Keep both marker systems documented only in ADR.

**Rejected because**: ADRs don't propagate to project instances. Workers in target projects would have no access to conventions.

### Single Unified Marker System

Merge Directive and Annotation Markers into one system.

**Rejected because**: They serve different purposes. Directive Markers guide Worker actions; Annotation Markers document discussion content. Forcing unification would create awkward hybrid markers.
