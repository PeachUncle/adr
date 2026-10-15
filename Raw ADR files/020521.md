# ADR-020: Sibling Dependency Law

## Status

Accepted

## Date

2025-12-03

## Context

As Xentri grows, we need to prevent dependency spaghetti while maintaining the "Decoupled Unity" architecture. Unrestricted cross-module dependencies create hidden coupling and make silos meaningless.

The BMAD Builder proposed a hierarchical requirement ID scheme that encodes ancestry (e.g., `SYS-002-STR-001-PUL-001`). However, a concern was raised about multi-parent inheritance—what if a module needs to depend on two different branches of the hierarchy?

After architectural review, we determined that:

1. Multi-parent **inheritance** is indeed problematic and should be avoided
2. Multi-parent **dependency** is different—it's natural for modules to _use_ interfaces from multiple sources
3. The solution is to separate inheritance (identity) from dependency (usage)

## Decision

We adopt the **Sibling Dependency Law** with three core principles:

### 1. Single-Parent Inheritance

Every requirement has exactly one parent. Identity flows down a single chain encoded in the requirement ID.

```
SYS-001                    → Constitution: Platform must have Shell
SYS-002                    → Constitution: Platform must have Strategy category
SYS-002-STR-001            → Strategy inherits from Constitution, must have Pulse
SYS-002-STR-001-PUL-001    → Pulse inherits from Strategy, needs Dashboard
```

The ID **is** the ancestry chain. Parsing `SYS-002-STR-001-PUL-001` reveals:

- Parent: `SYS-002-STR-001`
- Grandparent: `SYS-002`
- Root: `SYS`

### 2. Sibling-Only Dependencies

A node may only declare `requires_interfaces` on **siblings** (nodes sharing the same parent).

```yaml
# ✅ VALID - Pulse depending on sibling within Strategy
id: SYS-002-STR-001-PUL-001
requires_interfaces:
  - id: IC-STR-002          # Strategy's Event Bus - sibling at STR level
    reason: "Subscribe to metric events"

# ❌ INVALID - Pulse reaching across to Shell branch
id: SYS-002-STR-001-PUL-001
requires_interfaces:
  - id: IC-SHL-001          # Shell Navigation - NOT a sibling
    reason: "Display in nav"
```

### 3. Inherited Access

Cross-branch interface access must be declared by a **common ancestor**. Descendants inherit that access automatically.

```yaml
# At Strategy level (SYS-002), declare sibling dependency on Shell (SYS-001)
id: SYS-002
requires_interfaces:
  - id: IC-SHL-001          # Shell Navigation
    reason: "All Strategy modules need Shell integration"

# At Pulse level, inherited access is computed (read-only)
id: SYS-002-STR-001-PUL-001
inherited_interfaces:        # Computed, not declared
  - id: IC-SHL-001
    inherited_from: SYS-002  # Strategy declared this
```

## Dependency Resolution Algorithm

For any node N to access interface I:

1. **Provide**: N itself provides I → direct access
2. **Sibling**: A sibling of N provides I → declare `requires_interfaces`
3. **Inherit**: An ancestor of N has access to I → use via `inherited_interfaces`
4. **Denied**: None of above → **architectural violation**, redesign required

## Requirement File Format

```yaml
---
# Identity
id: SYS-002-STR-001-PUL-001
type: FR # FR, PR, IC, ADR
title: 'Real-time Metrics Dashboard'
status: draft # draft, approved, implemented, deprecated

# Single-parent inheritance (derived from ID, explicit for clarity)
parent: SYS-002-STR-001
ancestry: # Auto-generated from ID parsing
  - SYS
  - SYS-002
  - SYS-002-STR-001

# Sibling dependencies (ONLY siblings allowed)
requires_interfaces:
  - id: IC-STR-002
    reason: 'Subscribe to metric events'

# Inherited access (read-only, computed from ancestry)
inherited_interfaces:
  - id: IC-SHL-001
    inherited_from: SYS-002
  - id: IC-API-001
    inherited_from: SYS

# The actual requirement
description: |
  The Pulse dashboard displays real-time business metrics
  with configurable refresh intervals and drill-down capability.

acceptance_criteria:
  - Metrics refresh within 2 seconds of source event
  - Dashboard loads in under 500ms
---
```

## Consequences

### Positive

- **Dependency graph is always a tree**, never a web
- **Silo isolation is enforceable** and verifiable via CI
- **Forces architectural decisions to appropriate level**—if a low-level module needs something from another branch, the decision bubbles up
- **Teams only need to understand their branch**—parent chain + siblings
- **Matches event-driven architecture**—events bubble up, so should dependencies

### Negative

- **More ceremony** to add cross-branch dependencies (requires ancestor-level declaration)
- **May require restructuring** existing requirements that assume multi-parent
- **Escape hatch needed** for legacy/third-party integrations

### Neutral

- Requires validation tooling (acceptable investment, see `scripts/validation/validate-dependencies.ts`)
- Hierarchical IDs can get long at depth (e.g., 35 chars for 4 levels)—acceptable trade-off for encoded ancestry

## Escape Hatch

For genuine exceptions (legacy systems, third-party integrations, temporary bridges):

```yaml
requires_interfaces:
  - id: IC-LEGACY-001
    exception: true
    approved_by: 'ADR-021'
    justification: 'Legacy billing system, migration planned Q3'
```

**Exception requirements:**

1. Must reference an approving ADR
2. Must include justification
3. Must be reviewed in Architecture Review
4. Should include remediation plan with timeline

## Enforcement

| Layer          | Mechanism                                     | Behavior                         |
| -------------- | --------------------------------------------- | -------------------------------- |
| **CI**         | `scripts/validation/validate-dependencies.ts` | Block PR if sibling law violated |
| **Pre-commit** | Husky hook (optional)                         | Local validation before commit   |
| **Review**     | Architecture Review process                   | New sibling dependencies flagged |

## Related ADRs

- **ADR-001**: Universal Soul Orchestration (Knowledge Hierarchy)
- **ADR-002**: Event Envelope & Schema
- **ADR-014**: Module Registration Architecture

## References

- Discussion between Carlo and BMAD Builder on requirement ID schemes
- "Decoupled Unity" architecture principle from Xentri PRD
- Single Responsibility Principle applied to dependency management
