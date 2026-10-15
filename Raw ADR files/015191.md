# ADR-005: Skills-First Multi-Agent Architecture

**Status:** Accepted
**Date:** 2025-12-25
**Decision Makers:** TechTrend Federal - Digital Twin Team
**Category:** System Architecture & AI Strategy

---

## Context

### Strategic Background

RANGER is evolving from a demo application to a production-ready AI system for USDA Forest Service post-fire recovery. This architectural decision establishes the foundation for how we structure AI capabilities, with implications for:

1. **RANGER** as the flagship vertical application
2. **TechTrend's federal AI practice** as a repeatable pattern for USDA agencies
3. **Alignment with USDA's GenAI Strategy** and federal IT modernization initiatives

### The "Moving Up the Stack" Paradigm

Recent developments in AI architecture (Anthropic, Google ADK) establish a three-layer model:

| Layer | Computing Analogy | AI Equivalent | Builder Profile |
|-------|-------------------|---------------|-----------------|
| **Models** | Processors | LLMs (Gemini, Claude, GPT) | Few companies (Google, Anthropic, OpenAI) |
| **Agents** | Operating Systems | Agent frameworks, orchestration | Dozens of frameworks (ADK, LangGraph) |
| **Skills** | Applications | Domain expertise packages | **Millions of developers/organizations** |

The strategic insight: **value capture moves outward over time**. Just as application developers captured more value than OS vendors in computing, Skills developers will capture more value than Agent framework builders in AI.

### USDA GenAI Strategy Alignment

USDA's GenAI roadmap emphasizes:

- **Strategic Convergence**: Integrating AI/ML, IT, data, and mission strategies
- **GenAI Operations**: "Factory-like" project development with reusable components
- **GenAI Center of Excellence**: Standardized approaches, evaluation labs, governance
- **Enterprise Skills and Capabilities**: Cross-agency reusability, reduced duplication

Our Skills-First architecture directly implements these objectives:

| USDA GenAI Objective | Skills-First Implementation |
|---------------------|----------------------------|
| Strategic convergence | Skills bridge AI capabilities to mission outcomes |
| GenAI operations factory | Skills library = reusable, testable, versioned components |
| Enterprise capabilities | Foundation Skills shared across agencies |
| Innovation incubator | Vertical applications (RANGER) prove patterns |

### Problem Statement

1. **Domain Expertise Gap** — General LLMs lack USFS-specific knowledge (BAER protocols, MTBS classification, TRACS workflows)
2. **Reusability Challenge** — Custom agent prompts are not portable, testable, or versionable
3. **Multi-Agency Vision** — TechTrend aims to serve multiple USDA agencies; architecture must support expansion
4. **Operational Excellence** — Federal context demands auditability, explainability, and governance controls

---

## Decision

### 1. Adopt Skills-First Architecture

We adopt a **Skills-First** architecture where domain expertise is packaged as portable, testable, versionable **Skills** that enhance **Agents** running on the Google ADK / Gemini runtime.

```
┌─────────────────────────────────────────────────────────────────┐
│                        RANGER STACK                             │
├─────────────────────────────────────────────────────────────────┤
│  UI (Nerve Center)     → React Command Console                  │
│  Agent Pipeline        → Google ADK + Gemini Runtime            │
│  Skills Library        → Domain expertise packages              │
│  MCP Connectivity      → External data and tool integration     │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Multi-Agent + Skills Hybrid Model

We **retain the multi-agent architecture** (Coordinator + Specialists) but **enhance each agent with domain-specific Skills**. This is not "Skills instead of Agents" but "Skills on top of Agents."

```
Recovery Coordinator Agent
├── Skills: Delegation, Portfolio Triage, User Interaction
│
├── Burn Analyst Agent
│   └── Skills: MTBS Classification, Soil Burn Severity, Boundary Mapping
│
├── Trail Assessor Agent
│   └── Skills: Damage Classification, Closure Decision, Recreation Priority
│
├── Cruising Assistant Agent
│   └── Skills: Cruise Methodology, Volume Estimation, Salvage Assessment
│
└── NEPA Advisor Agent
    └── Skills: Pathway Decision (CE/EA/EIS), Documentation, NEPA Library
```

### 3. Skills as Portable Expertise Packages

Skills are **organized folders** containing:

```
skill-name/
├── skill.md              # Instructions, triggers, decision logic
├── scripts/              # Executable tools (Python, bash)
│   └── calculate.py
├── resources/            # Reference data, decision trees
│   └── thresholds.json
└── examples/             # Few-shot examples for the LLM
    └── sample-output.md
```

**Progressive Disclosure**: Only skill metadata is loaded into context initially; full skill content is loaded only when invoked.

### 4. Three-Tier Skills Taxonomy

| Tier | Scope | Examples | Reusability |
|------|-------|----------|-------------|
| **Foundation** | Cross-agency, cross-domain | NEPA Compliance, Geospatial Analysis, Federal Reporting | High |
| **Agency** | Agency-specific but shared | USFS Fire Terminology, NRCS Soil Standards | Medium |
| **Application** | Single application | BAER Assessment, Trail Damage Classification | Low (by design) |

### 5. MCP for Connectivity, Skills for Expertise

- **MCP Servers** provide data connectivity (NIFC API, weather services, GIS)
- **Skills** provide expertise on how to use that data effectively

This separation enables:
- Shared MCP servers across multiple applications
- Skills that can work with different data sources
- Clear testing boundaries

---

## Rationale

### Why Skills-First for Federal Context

| Factor | Traditional Agent | Skills-First Agent |
|--------|-------------------|-------------------|
| **Auditability** | Prompts in code, hard to trace | Skills versioned in Git, full lineage |
| **Governance** | Ad-hoc prompt engineering | Explicit decision logic in skill.md |
| **Testability** | End-to-end only | Unit test individual skills |
| **Reusability** | Copy-paste prompts | Import skill folders |
| **Compliance** | Document behavior after the fact | Behavior documented in skill definition |

### Why Multi-Agent + Skills (Not Skills Replacing Agents)

The strategic review validated: **fire recovery is inherently multi-disciplinary**. BAER assessments involve parallel specialist evaluations (soils, hydrology, wildlife) that integrate into unified recommendations.

| Approach | When to Use | RANGER Fit |
|----------|-------------|------------|
| Single Agent + RAG | Simple Q&A, document retrieval | Too simple |
| Single Agent + Skills | Moderate complexity, single domain | Insufficient for multi-disciplinary |
| **Multi-Agent + Skills** | High complexity, multi-disciplinary | **Correct fit** |
| Swarm / Autonomous Agents | Open-ended exploration | Too unpredictable for federal |

### Why Not Pure Platform Play

The strategic review warned against "big bang" platform strategies in federal IT. Historical failure rates are high (only 6.4% of $10M+ federal IT projects succeed). Our approach:

- **Start vertical**: RANGER proves the pattern in a specific domain
- **Expand incrementally**: Forest Service first, then NRCS, then others
- **Demonstrate ROI**: Use RANGER success to pull strategy change, not push it
- **Test reusability empirically**: Don't assume Foundation Skills transfer; measure it

---

## Implementation

### Monorepo Structure

> **Note:** Agent directory names MUST use underscores (valid Python identifiers) for Google ADK compatibility.

```
ranger/
├── apps/
│   └── command-console/           # UI (Nerve Center)
│
├── agents/                        # Agent Pipeline
│   ├── coordinator/
│   │   ├── agent.py               # ADK agent definition
│   │   ├── config.yaml
│   │   ├── skills/                # Coordinator-specific skills
│   │   │   ├── delegation/
│   │   │   ├── portfolio-triage/
│   │   │   └── user-interaction/
│   │   └── tests/
│   ├── burn_analyst/              # Underscores required!
│   ├── trail_assessor/
│   ├── cruising_assistant/
│   └── nepa_advisor/
│
├── skills/                        # Shared Skills Library
│   ├── foundation/                # Cross-agency
│   │   ├── geospatial-analysis/
│   │   ├── nepa-compliance/
│   │   └── document-generation/
│   └── forest-service/            # Agency-shared
│       └── fire-terminology/
│
├── mcp/                           # MCP Server Implementations
│   ├── nifc/
│   ├── weather/
│   └── gis/
│
├── packages/                      # Shared Libraries
│   ├── skill-runtime/             # Skill loading/execution
│   └── types/
│
└── infrastructure/
    └── terraform/
```

### Feature Branch Strategy

Each agent + its skills developed in isolation:

```
main (production)
└── develop (integration)
    ├── feature/coordinator-agent
    ├── feature/burn-analyst-agent
    ├── feature/trail-assessor-agent
    ├── feature/cruising-assistant-agent
    └── feature/nepa-advisor-agent
```

### Cloud Run Deployment Model

**Hybrid approach** for balance of simplicity and modularity:

- **ranger-orchestrator**: Single Cloud Run service containing all agents + bundled skills
- **mcp-nifc**, **mcp-gis**: Separate Cloud Run services for data connectivity
- **Skills loading**: Agent-specific skills bundled; Foundation skills from Cloud Storage

This enables:
- Fast cold start (single orchestrator)
- Independent scaling for data services
- Skills updates without redeployment (Cloud Storage)

---

## Consequences

### Positive

1. **USDA Strategy Alignment** — Architecture maps directly to GenAI roadmap objectives
2. **Auditability** — Skills provide documentary evidence for FedRAMP, IG oversight
3. **Testability** — Individual skills can be unit tested, evaluated, red-teamed
4. **Reusability** — Foundation Skills potentially shared across USDA agencies
5. **Evolvability** — Skills can be updated, versioned, deprecated independently
6. **Domain Depth** — Each agent becomes genuinely expert through its skills
7. **Practitioner Contribution** — Non-technical domain experts can author/review skill.md files
8. **Repeatable Pattern** — Same architecture applies to NRCS, FSA, other USDA engagements

### Negative

1. **Complexity Overhead** — Multi-agent + skills adds orchestration complexity
2. **Skill Authoring Learning Curve** — Team must develop skill authoring expertise
3. **Reusability Uncertainty** — Foundation Skills may require more customization than expected
4. **Framework Dependency** — Tied to Google ADK patterns (mitigated by skill portability)

### Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Skills don't reuse across agencies | 50% | High | Test empirically in NRCS pilot; don't assume |
| Multi-agent orchestration reliability | 40% | High | Extensive simulation; safety layers; human-in-loop |
| Skill format becomes obsolete | 20% | Medium | Skills are plain files; easy to migrate |
| Team can't author quality skills | 30% | Medium | Develop skill authoring guide; review process |

---

## Alternatives Considered

### Alternative 1: Monolithic Single Agent

**Description**: One agent with a large prompt containing all domain knowledge.

| Factor | Assessment |
|--------|------------|
| Simplicity | High |
| Scalability | Low — prompt grows unbounded |
| Testability | Low — can only test end-to-end |
| Reusability | None |
| **Verdict** | **Rejected** — doesn't scale, can't test |

### Alternative 2: Pure Skills (No Agent Orchestration)

**Description**: Skills invoke skills directly; no coordinator agent.

| Factor | Assessment |
|--------|------------|
| Simplicity | Medium |
| Flexibility | High |
| Control | Low — no central coordination |
| Federal fit | Poor — hard to audit decision flow |
| **Verdict** | **Rejected** — insufficient governance |

### Alternative 3: Microservices per Agent

**Description**: Each agent as a separate Cloud Run service.

| Factor | Assessment |
|--------|------------|
| Isolation | High |
| Complexity | High — network latency, orchestration |
| Cold start | Poor — multiple services to warm |
| Cost | Higher — more services |
| **Verdict** | **Deferred** — revisit if scaling requires |

### Alternative 4: RAG-Only (No Agents or Skills)

**Description**: Pure retrieval-augmented generation over documents.

| Factor | Assessment |
|--------|------------|
| Simplicity | High |
| Reasoning | Low — limited to retrieval |
| Workflow | None — can't orchestrate multi-step |
| Federal proven | Yes — some federal RAG deployments |
| **Verdict** | **Rejected** — insufficient for workflow automation |

---

## USDA GenAI Strategy Terminology Mapping

To align communications with USDA leadership, use this terminology mapping:

| Skills-First Concept | USDA GenAI Roadmap Term |
|---------------------|------------------------|
| Skills Library | Enterprise Skills and Capabilities |
| Coordinator Agent | GenAI Operations Orchestration |
| Foundation Skills | Cross-Mission-Area Shared Services |
| Agent + Skills Testing | GenAI Evaluation Lab |
| skill.md Governance | Explainability and Transparency Controls |
| RANGER | Innovation Incubator Proof-of-Concept |
| MCP Connectivity | Data-Driven Decision Support Infrastructure |

**Recommended framing for stakeholders**:

> "RANGER implements USDA's GenAI strategic vision through a Skills-First architecture that delivers the 'enterprise skills and capabilities' and 'GenAI operations factory' called for in the department's roadmap. Each skill is a testable, auditable unit of domain expertise that can be composed, versioned, and potentially shared across mission areas."

---

## Success Metrics

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Skill invocation accuracy | >95% | Coordinator routes to correct skill |
| Skill test coverage | >80% | Unit tests per skill |
| Foundation Skill reuse | >50% | Skills used in 2+ agents/applications |
| Cold start time | <3s | Cloud Run orchestrator |

### Business Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| RANGER pilot adoption | >50% of pilot regions | 12 months |
| BAER assessment time reduction | 20% | 12 months |
| Second vertical (NRCS or FS expansion) | Initiated | 18 months |
| FedRAMP ATO | Obtained | 18 months |

---

## References

- [USDA GenAI Strategy Report](../research/Transforming_USDA_with_GenAI.pdf) — Department-wide GenAI roadmap
- [Strategic Architecture Review](../research/Strategic%20Architecture%20Review.md) — External evaluation of Skills-First approach
- [Claude Agents and Skills Transcripts](../research/_!_Claude%20Agents%20and%20Skills.md) — Anthropic's skills paradigm
- [Google ADK Documentation](https://google.github.io/adk-docs/) — Agent Development Kit
- [ADR-004: Site Analysis & OpenRouter](./ADR-004-site-analysis-openrouter.md) — Prior LLM integration decision
- [USDA Data Strategy 2024-2026](https://www.usda.gov/sites/default/files/documents/fy-2024-2026-usda-data-strategy.pdf)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-25 | Skills-First architecture accepted | Aligns with USDA GenAI strategy; enables auditability, testability, reusability |
| 2025-12-25 | Multi-Agent + Skills hybrid model accepted | Fire recovery is multi-disciplinary; single agent insufficient |
| 2025-12-25 | Three-tier skills taxonomy accepted | Balances reusability aspiration with pragmatic domain specificity |
| 2025-12-25 | Feature branch per agent strategy accepted | Enables modular development and testing |
| 2025-12-25 | Cloud Run hybrid deployment accepted | Balance of simplicity (single orchestrator) and modularity (separate MCP) |

---

## Appendix: Skill Format Specification

### skill.md Template

```markdown
# [Skill Name]

## Description
Brief description of what this skill does.

## Triggers
When should the agent invoke this skill?
- User asks about X
- Task involves Y
- Data contains Z

## Instructions
Step-by-step instructions for the agent when executing this skill.

1. First, do X
2. Then, evaluate Y
3. Finally, produce Z

## Inputs
| Input | Type | Required | Description |
|-------|------|----------|-------------|
| fire_id | string | Yes | NIFC fire identifier |
| acres | number | Yes | Burned area in acres |

## Outputs
| Output | Type | Description |
|--------|------|-------------|
| severity_classification | string | Low/Moderate/High/Critical |
| confidence | number | 0-1 confidence score |
| reasoning | string | Explanation of classification |

## Resources
- `thresholds.json` — Classification thresholds
- `examples/` — Few-shot examples

## Scripts
- `calculate_severity.py` — Severity calculation tool

## References
- MTBS Classification Protocol v3.2
- USFS Fire Severity Guidelines
```

### Directory Structure

```
skill-name/
├── skill.md              # Core instructions (required)
├── scripts/              # Executable tools (optional)
│   └── tool_name.py
├── resources/            # Reference data (optional)
│   ├── thresholds.json
│   └── decision-tree.json
├── examples/             # Few-shot examples (optional)
│   ├── input-1.json
│   └── output-1.json
└── tests/                # Skill tests (required)
    └── test_skill.py
```
