# ADR-002: Brand Naming Strategy

**Status:** Accepted
**Date:** 2025-12-19
**Decision Makers:** TechTrend Federal - Digital Twin Team
**Category:** Brand & Communications (Strategic)

---

## Context

We are developing an AI-first digital twin platform for post-fire forest recovery targeting the US Forest Service. The platform consists of five specialized AI agents that assist with burn severity assessment, trail damage detection, timber inventory, NEPA compliance, and integrated recovery coordination.

Effective naming is critical for federal technology adoption. The name must:

1. **Resonate with USFS culture** without alienating field staff or leadership
2. **Avoid triggering AI anxiety** (job displacement fears, hallucination concerns, procurement complexity)
3. **Scale beyond the initial use case** (post-fire recovery) to broader forest management
4. **Work in federal acronym culture** without feeling forced
5. **Support natural voice interaction** for the multimodal TimberCruiser agent

### The Naming Challenge

We identified a fundamental tension between two competing priorities:

| Priority | Requirement |
|----------|-------------|
| **Federal Authority** | Names must sound like funded initiatives that leadership can defend in budget justifications |
| **AI Innovation** | The platform's differentiation is its "agent-first" architecture, but foregrounding "AI" creates adoption friction |

### Alternatives Considered

We evaluated five distinct naming strategies:

| Strategy | Platform Name | Core Emphasis | Verdict |
|----------|---------------|---------------|---------|
| **Heritage + AI** | Project RANGER AI | User identity + technology | AI in name creates procurement anxiety |
| **Operations-First** | ForestOps Platform | Mission outcomes | Too generic; sounds like IT operations |
| **Mission-Explicit** | AfterFire Platform | Post-fire recovery | Limits TAM; paints into corner if platform expands |
| **Digital Infrastructure** | Canopy Grid | Digital twin / data fabric | Too Silicon Valley; lacks federal gravitas |
| **Stewardship Metaphor** | Trellis | Support structure for growth | Too subtle; requires explanation |

---

## Decision

We adopt a **three-tier brand architecture** that separates the initiative, platform, and agent layers:

### Brand Architecture

| Layer | Name | Purpose |
|-------|------|---------|
| **Initiative** | Project RANGER | The strategic modernization effort (budget docs, Hill briefings, leadership communications) |
| **Platform** | RANGER | The unified digital twin operating system (the product itself) |
| **Descriptor** | "The USFS Digital Twin" | Technical positioning for enterprise architecture audiences |
| **Agents** | Role-based titles | AI specialists that augment human expertise (see below) |

### Agent Naming Convention

We adopt **professional role titles** instead of product names to frame AI agents as "digital colleagues" rather than replacement technology:

| Old Name | New Name | Rationale |
|----------|----------|-----------|
| FireSight / FireSight Lite | **The Burn Analyst** | Matches "analyst" roles in USFS |
| TrailScan AI | **The Trail Assessor** | Aligns with TRACS assessment methodology |
| TimberScribe | **The Cruising Assistant** | "Assistant" explicitly positions AI as helper, not replacement |
| PolicyPilot | **The NEPA Advisor** | "Advisor" implies counsel you consult, not autopilot |
| RecoveryCoordinator | **Recovery Coordinator** | Already a role-based name; no change needed |

### Presentation Hierarchy

For stakeholder presentations:

> **The Initiative:** Project RANGER
> *The strategic effort to modernize post-fire recovery.*
>
> **The Platform:** RANGER
> *The unified Digital Twin operating system.*
>
> **The Crew (AI Agents):**
> - **Burn Analyst:** Automates severity mapping.
> - **Trail Assessor:** Digitizes damage inventory.
> - **Cruising Assistant:** Transcribes field data.
> - **NEPA Advisor:** Accelerates compliance.

---

## Rationale

### 1. Role Titles Solve the "AI Anxiety" Problem

The shift from **product names** to **role names** is strategic, not cosmetic:

| Product Name | Sounds Like... | Role Name | Sounds Like... |
|--------------|----------------|-----------|----------------|
| FireSight | Software that sees fire for you | Burn Analyst | A specialist on your team |
| TrailScan | App that scans trails | Trail Assessor | Someone who assesses trails |
| TimberScribe | Tool that writes timber data | Cruising Assistant | Helper for the cruiser (human) |
| PolicyPilot | Autopilot for policy | NEPA Advisor | Counsel you consult |

Product framing implies **human replacement**. Role framing implies **human supervision**. In federal adoption, this distinction is critical.

### 2. "RANGER" Enables Natural Voice Interaction

The platform must support voice interaction for the TimberCruiser (now "Cruising Assistant") agent. "RANGER" works as a form of address:

- "Hey Ranger, start a new plot." (natural)
- "Hey ForestOps, start a new plot." (sounds like calling IT support)
- "Hey Canopy Grid, start a new plot." (sounds like a sci-fi movie)

### 3. "RANGER" Doesn't Limit Future Expansion

"AfterFire" would limit the platform's total addressable market. If the pilot succeeds, USFS will want:

- Pre-fire fuel load analysis
- Active fire resource positioning
- Cross-fire pattern recognition
- Climate adaptation planning

"RANGER" covers all phases of forest management. "AfterFire" does not.

### 4. "Digital Twin" is the Technical Differentiator

The term "Digital Twin" positions the platform as:

- **Infrastructure** (not an app)
- **Authoritative** (the official representation)
- **Extensible** (twins can model anything)

This descriptor should be used in technical contexts: "RANGER: The USFS Digital Twin."

### 5. Rejected Alternatives

| Name | Why Rejected |
|------|--------------|
| **ForestOps** | Too generic; sounds like maintenance, not innovation |
| **AfterFire** | Limits TAM; paints into corner for pre-fire/active fire expansion |
| **Canopy Grid** | Too Silicon Valley; requires explanation |
| **Trellis** | Too subtle; federal stakeholders want authority, not gardening metaphors |
| **PULASKI** | Too fire-centric for timber/trail contexts |
| **SYLVA** | Elegant but abstract; doesn't communicate mission |
| **VISTA** | Conflicts with AmeriCorps VISTA; too generic |

---

## Consequences

### Positive

1. **Reduced adoption friction** — Role-based agent names frame AI as augmentation, not replacement
2. **Voice interface ready** — "RANGER" works as a natural address for multimodal interaction
3. **Future-proof** — Platform can expand beyond post-fire recovery without rebranding
4. **Federal culture fit** — "Project RANGER" sounds like a funded initiative; "RANGER" honors USFS identity
5. **Consistent architecture** — Clear hierarchy from initiative to platform to agents

### Negative

1. **Documentation updates required** — All existing docs use old names (FireSight, TrailScan, etc.)
2. **Agent name length** — "The Burn Analyst" is longer than "BurnAnalyst" in code and UI
3. **"The" prefix decision** — Unclear whether to include "The" in all contexts (code: `BurnAnalyst`, speech: "The Burn Analyst")

### Implementation Notes

| Context | Format | Example |
|---------|--------|---------|
| **Code/Technical** | PascalCase, no prefix | `BurnAnalyst`, `TrailAssessor` |
| **UI Labels** | Title case, no prefix | "Burn Analyst", "Trail Assessor" |
| **Speech/Documentation** | "The" prefix | "The Burn Analyst says...", "Ask the Trail Assessor" |
| **Informal** | Shortened | "the analyst", "the assessor" |

---

## References

- [PROJECT-BRIEF.md](../PROJECT-BRIEF.md) — Master project document
- [BRAND-ARCHITECTURE.md](../brand/BRAND-ARCHITECTURE.md) — One-page brand reference
- [STAKEHOLDER-MESSAGING.md](../brand/STAKEHOLDER-MESSAGING.md) — Audience-specific messaging

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-19 | Accepted | Team consensus after competitive analysis and marketing consultation |
