# ADR-0009: Documentation Architecture Strategy

**Status**: Proposed  
**Date**: 2025-12-14  
**Deciders**: Tony Moores  
**Technical Story**: Phase 0 - Foundation, Standards Gap 1 (P0)

## Context

TJMPaaS has grown to 98+ markdown files (~16,000+ lines) across governance, service designs, standards, best practices, and working documents. The current `doc/internal/` and `doc/external/` structure lacks a clear organizational philosophy for different documentation types, making it increasingly difficult to:

- Navigate and discover relevant documentation
- Understand documentation lifecycle (draft → reviewed → published)
- Separate internal working documents from authoritative standards
- Manage documentation for different audiences (developers, operations, compliance)
- Scale documentation as project grows

### Problem Statement

Establish a documentation architecture that:
- Supports multiple documentation layers with clear purposes
- Provides clear navigation and discoverability patterns
- Enables lifecycle management (draft → review → published → archived)
- Separates concerns (governance vs technical vs process vs compliance)
- Scales from current 98 files to hundreds or thousands
- Maintains manageable complexity for solo developer initially
- Prepares for team collaboration and compliance requirements

### Goals

- Clear 5-layer documentation architecture
- Well-defined directory structure per layer
- Cross-reference strategy across layers
- Documentation lifecycle workflows
- Update processes per layer
- Scalable to team growth and compliance needs

### Constraints

- Must preserve Git history when reorganizing
- Must not break existing cross-references (hundreds of links)
- Solo developer initially (simple processes required)
- Must support AI assistant navigation (Copilot-friendly structure)
- Must work with current tooling (GitHub, Markdown, VS Code)

## Decision

**Adopt a 5-layer documentation architecture** organized by audience, purpose, and lifecycle:

1. **External Documentation** (`doc/external/`) - Public-facing, customer-oriented
2. **Governance Documentation** (`doc/internal/governance/`) - Project-wide decisions and policies
3. **Technical Documentation** (`doc/internal/technical/`) - Architecture, design, implementation
4. **Process Documentation** (`doc/internal/process/`) - Workflows, procedures, guides
5. **Compliance Documentation** (`doc/internal/compliance/`) - Audit, regulatory, retention

Each layer has distinct:
- **Purpose**: Why this documentation exists
- **Audience**: Who reads and maintains it
- **Lifecycle**: How it's created, reviewed, updated, archived
- **Update Frequency**: How often it changes
- **Authority**: What makes it official

## Rationale

### 5-Layer Model

#### Layer 1: External Documentation (`doc/external/`)

**Purpose**: Public-facing documentation for external stakeholders (customers, partners, community)

**Audience**:
- Potential customers evaluating TJMPaaS
- Current customers using services
- Open-source community contributors
- Partners integrating with TJMPaaS

**Content Types**:
- Service catalogs and feature overviews
- API documentation (public APIs)
- Integration guides
- Release notes and changelogs
- Getting started guides
- Tutorials and examples

**Lifecycle**:
- Draft → Marketing Review → Technical Review → Published
- Versioned with service releases
- Maintained for backward compatibility

**Update Frequency**: Quarterly or with major releases

**Authority**: Marketing + Engineering approval required

**Directory Structure**:
```
doc/external/
├── README.md                    # Index of external documentation
├── services/                    # Service catalog (future)
│   └── entity-management.md    # Public overview of Entity Management Service (when production-ready)
├── api/                         # Public API documentation (future)
│   ├── authentication.md
│   ├── multi-tenant.md
│   └── error-handling.md
├── guides/                      # Integration and user guides (future)
│   ├── getting-started.md
│   ├── multi-tenant-setup.md
│   └── event-integration.md
├── tutorials/                   # Step-by-step tutorials (future)
│   └── first-service.md
└── release-notes/              # Release notes and changelogs (future)
    ├── 2025-q4.md
    └── 2026-q1.md
```

**Current Files**: None yet (layer created for future use as services reach production)

---

#### Layer 2: Governance Documentation (`doc/internal/governance/`)

**Purpose**: Project-wide architectural decisions, process decisions, and policies

**Audience**:
- Tony (project owner and architect)
- Future team members
- Compliance auditors (for process verification)

**Content Types**:
- **ADRs** (Architectural Decision Records): Technical/architecture decisions
- **PDRs** (Process Decision Records): Workflow/process decisions
- **POLs** (Policies): Mandatory rules, standards, compliance requirements
- **Templates**: Templates for creating governance documents

**Lifecycle**:
- Proposed → Reviewed → Accepted → Immutable (except corrections)
- Superseded ADRs/PDRs marked with status, link to replacement
- Policies updated with versioning (POL-v2 supersedes POL-v1)

**Update Frequency**: As needed (decision-driven), typically weekly to monthly

**Authority**: Tony (currently), team consensus (future)

**Directory Structure** (current):
```
doc/internal/governance/
├── ADRs/
│   ├── ADR-TEMPLATE.md
│   ├── ADR-0001-gcp-pilot-platform.md
│   ├── ADR-0002-documentation-first-approach.md
│   ├── ADR-0003-containerization-strategy.md
│   ├── ADR-0004-scala3-technology-stack.md
│   ├── ADR-0005-reactive-manifesto-alignment.md
│   ├── ADR-0006-agent-patterns.md
│   ├── ADR-0007-cqrs-event-driven-architecture.md
│   ├── ADR-0008-local-first-development.md
│   └── ADR-0009-documentation-architecture.md (this document)
├── PDRs/
│   ├── PDR-TEMPLATE.md
│   ├── PDR-0001-documentation-standards.md
│   ├── PDR-0002-code-review-process.md
│   ├── PDR-0003-governance-document-lifecycle.md
│   ├── PDR-0004-repository-organization.md
│   ├── PDR-0005-framework-selection-policy.md
│   ├── PDR-0006-service-canvas-standard.md
│   └── PDR-0007-documentation-asset-management.md
├── POLs/
│   ├── POL-TEMPLATE.md
│   ├── POL-security-baseline.md
│   └── POL-quality-code-standards.md
└── templates/
    ├── SERVICE-CANVAS.md
    └── FEATURE-TEMPLATE.md
```

**Current Files**: 26 files (8 ADRs, 7 PDRs, 2 POLs, templates, etc.)

**Changes from Current**: 
- Move standards from `doc/internal/standards/` to `doc/internal/governance/POLs/` (see Gap 4 remediation)
  - MULTI-TENANT-SEAM-ARCHITECTURE.md → POL-multi-tenant-architecture.md
  - EVENT-SCHEMA-STANDARDS.md → POL-event-schema-standards.md
  - API-DESIGN-STANDARDS.md → POL-api-design-standards.md
  - RBAC-SPECIFICATION.md → POL-rbac-specification.md

---

#### Layer 3: Technical Documentation (`doc/internal/technical/`)

**Purpose**: Architecture, design, implementation details for TJMPaaS and services

**Audience**:
- Developers (Tony currently, future team)
- Operations engineers
- Technical architects reviewing system design

**Content Types**:
- Cross-service architecture documentation
- Service designs (before implementation)
- Best practices research
- Technical standards and patterns
- Infrastructure documentation

**Lifecycle**:
- Draft → Technical Review → Published → Updated as needed
- Living documents (updated with system evolution)
- Archived when superseded or obsolete

**Update Frequency**: Weekly to monthly (as services evolve)

**Authority**: Technical lead approval (Tony currently)

**Directory Structure**:
```
doc/internal/technical/
├── README.md                    # Index of technical documentation
├── architecture/                # Cross-service architecture
│   ├── overview.md
│   ├── integration-patterns.md
│   ├── event-driven-architecture.md
│   └── multi-tenant-patterns.md
├── services/                    # Service design documents (before implementation)
│   └── entity-management/      # Entity Management Service design
│       ├── SERVICE-CHARTER.md
│       ├── SERVICE-ARCHITECTURE.md
│       ├── SERVICE-CANVAS.md
│       ├── API-SPECIFICATION.md
│       ├── DEPLOYMENT-RUNBOOK.md
│       ├── TELEMETRY-SPECIFICATION.md
│       ├── ACCEPTANCE-CRITERIA.md
│       ├── SECURITY-REQUIREMENTS.md
│       └── features/           # Feature specifications
│           ├── tenant-provisioning.md
│           ├── tenant-provisioning.feature
│           ├── organization-hierarchy.md
│           ├── organization-hierarchy.feature
│           ├── user-management.md
│           ├── user-management.feature
│           ├── role-permissions.md
│           ├── role-permissions.feature
│           ├── audit-trail.md
│           └── audit-trail.feature
├── best-practices/              # Best practices research
│   ├── BEST-PRACTICE-TEMPLATE.md
│   ├── BEST-PRACTICES-GUIDE.md
│   ├── architecture/
│   │   ├── actor-patterns.md
│   │   ├── cqrs-patterns.md
│   │   ├── event-driven.md
│   │   ├── functional-programming.md
│   │   ├── reactive-manifesto.md
│   │   └── rest-hateoas.md
│   └── development/
│       ├── mill-build-tool.md
│       └── scala3.md
├── infrastructure/              # Infrastructure documentation
│   ├── local-development.md
│   ├── docker-compose-setup.md
│   └── kubernetes-patterns.md
└── examples/                    # Reference implementations
    └── (future service examples as they're created)
```

**Current Files**: ~70 files (Entity Management Service design, Provisioning Service stub, best practices research)

**Changes from Current**:
- Move `doc/internal/services/` → `doc/internal/technical/services/`
- Move `doc/internal/best-practices/` → `doc/internal/technical/best-practices/`
- Move `doc/internal/examples/` → `doc/internal/technical/examples/`

---

#### Layer 4: Process Documentation (`doc/internal/process/`)

**Purpose**: How to work in TJMPaaS - workflows, procedures, guides for team operations

**Audience**:
- Developers (current and future team)
- Operations engineers
- New team members (onboarding)

**Content Types**:
- Developer guides (how to create a service, how to deploy)
- Operational runbooks (incident response, maintenance)
- Onboarding documentation (for future team)
- Tool setup guides (IDE, development environment)
- Workflow documentation (code review, testing, CI/CD)

**Lifecycle**:
- Draft → Team Review → Published → Updated based on feedback
- Living documents (updated frequently as processes improve)
- Versioned when major changes occur

**Update Frequency**: Monthly or as processes change

**Authority**: Team consensus (Tony currently)

**Directory Structure**:
```
doc/internal/process/
├── README.md                    # Index of process documentation
├── development/
│   ├── local-setup.md          # Setting up local development environment
│   ├── creating-service.md     # How to create a new service from template
│   ├── testing-guidelines.md   # Testing strategy and practices
│   └── code-review-checklist.md
├── operations/
│   ├── deployment-process.md   # How to deploy services
│   ├── monitoring-guide.md     # How to monitor services
│   ├── incident-response.md    # Incident handling procedures
│   └── runbooks/               # Service-specific runbooks
│       └── entity-management-runbook.md
├── onboarding/
│   ├── new-developer-guide.md  # First week guide for new developers
│   ├── architecture-overview.md
│   └── key-decisions.md        # Summary of key ADRs/PDRs
└── tools/
    ├── ide-setup.md            # VS Code + Metals setup
    ├── git-workflow.md         # Git branching and PR process
    └── ci-cd-guide.md          # Understanding CI/CD pipelines
```

**Current Files**: ~5 files (CHARTER.md, ROADMAP.md, LOCAL-DEVELOPMENT-GUIDE.md, copilot references)

**Changes from Current**:
- Move `doc/internal/CHARTER.md` → `doc/internal/process/project-charter.md` (or keep at root for prominence)
- Move `doc/internal/ROADMAP.md` → `doc/internal/process/project-roadmap.md` (or keep at root for prominence)
- Move `doc/internal/LOCAL-DEVELOPMENT-GUIDE.md` → `doc/internal/process/development/local-setup.md`
- Move `doc/internal/copilot-references/` → `doc/internal/process/tools/copilot-references/`

**Alternative**: Keep CHARTER.md and ROADMAP.md at `doc/internal/` root for prominence (not buried in process/)

---

#### Layer 5: Compliance Documentation (`doc/internal/compliance/`)

**Purpose**: Audit trails, regulatory compliance, legal requirements, retention policies

**Audience**:
- Compliance officers
- Legal team
- Auditors (internal and external)
- Regulators

**Content Types**:
- Session summaries (audit trail of decisions)
- Standards gaps tracking
- Compliance checklists
- Regulatory documentation (GDPR, SOC2, etc.)
- Data retention policies
- Incident reports

**Lifecycle**:
- Created → Reviewed → Immutable (append-only for audit)
- Never deleted (retained per retention policy)
- Archived after retention period

**Update Frequency**: Per event (session summaries), quarterly (compliance reviews)

**Authority**: Compliance officer approval (Tony currently, legal/compliance future)

**Directory Structure**:
```
doc/internal/compliance/
├── README.md                    # Index and retention policies
├── audit/                       # Audit trail and session summaries
│   ├── SESSION-SUMMARY-TEMPLATE.md
│   ├── session-2025-12-01-entity-management-design.md
│   └── session-2025-12-14-local-first-strategy.md
├── gaps/                        # Standards and compliance gaps tracking
│   ├── STANDARDS-GAPS.md
│   ├── GAPS-REMEDIATION-PLAN.md
│   └── GAPS-EXECUTION-TRACKER.md
├── regulatory/                  # Regulatory compliance documentation
│   ├── gdpr-compliance.md
│   ├── soc2-readiness.md
│   └── pci-dss-scope.md
├── incidents/                   # Incident reports and retrospectives
│   └── template-incident-report.md
└── archive/                     # Archived compliance documents
    └── legacy/
        └── retisio-canvas-templates/
```

**Current Files**: ~5 files (audit trail, gaps tracking, legacy archive)

**Changes from Current**:
- Move `doc/internal/audit/` → `doc/internal/compliance/audit/`
- Move `doc/internal/gaps/` → `doc/internal/compliance/gaps/`
- Move `doc/internal/archive/legacy/` → `doc/internal/compliance/archive/legacy/`

---

### Cross-Layer Patterns

#### Documentation Types Across Layers

| Documentation Type | Layer(s) | Example Files |
|--------------------|----------|---------------|
| **Decision Records** | Governance | ADRs (architecture), PDRs (process), POLs (policies) |
| **Service Documentation** | Technical → External | Service designs (internal), Service catalogs (external) |
| **Standards** | Governance (POLs) | Multi-tenant architecture, Event schemas, API design, RBAC |
| **Research** | Technical | Best practices, technology evaluations |
| **Guides** | Process | Developer guides, onboarding, runbooks |
| **Audit Trails** | Compliance | Session summaries, incident reports, gaps tracking |
| **Templates** | All layers | Templates co-located with usage context |

#### Cross-References

Documents frequently reference across layers:

**Governance → Technical**:
- ADRs reference best practices research: `ADR-0005 → best-practices/architecture/reactive-manifesto.md`
- PDRs reference service examples: `PDR-0006 → examples/CartService-CANVAS-example.md`

**Technical → Governance**:
- Service designs reference ADRs: `Entity Management Architecture → ADR-0006 (agent patterns)`
- Best practices validate ADRs: `actor-patterns.md validates ADR-0006`

**Process → Governance**:
- Onboarding guides reference key ADRs: `new-developer-guide.md → ADR-0004, ADR-0005`
- Runbooks reference POLs: `deployment-process.md → POL-security-baseline.md`

**Compliance → All**:
- Audit trails reference decisions: `session-summary → ADR-0008, PDR-0007`
- Gap tracking references standards: `STANDARDS-GAPS.md → POLs, ADRs, PDRs`

**Cross-Reference Strategy**:
- Use relative paths: `[ADR-0006](../governance/ADRs/ADR-0006-agent-patterns.md)`
- Use descriptive link text: `[Agent-Based Service Patterns](../governance/ADRs/ADR-0006-agent-patterns.md)`
- Validate links with CI/CD (markdown-link-check)
- Update references when files move (automated or manual)

#### Templates Strategy

**Co-Location** (per PDR-0007):
- Templates located near usage context for Copilot optimization
- ADR-TEMPLATE.md in `governance/ADRs/`
- PDR-TEMPLATE.md in `governance/PDRs/`
- POL-TEMPLATE.md in `governance/POLs/`
- BEST-PRACTICE-TEMPLATE.md in `technical/best-practices/`
- SESSION-SUMMARY-TEMPLATE.md in `compliance/audit/`

**Master Index**: `doc/internal/TEMPLATES-GUIDE.md` lists all template locations for human discoverability

### Benefits of 5-Layer Architecture

**Separation of Concerns**:
- External vs internal documentation clearly separated
- Governance (decisions) vs technical (implementation) vs process (how-to) distinct
- Compliance (audit) isolated for regulatory requirements

**Scalability**:
- Each layer scales independently
- External docs grow with customer base
- Technical docs grow with services
- Process docs grow with team
- Compliance docs grow with regulatory requirements

**Clarity**:
- Purpose of each document clear from location
- Audience immediately understood
- Lifecycle appropriate to layer

**Discovery**:
- Developers find technical docs easily
- Operations find process docs easily
- Auditors find compliance docs easily
- Customers find external docs easily

**Maintainability**:
- Update frequency appropriate to layer
- Authority clear per layer
- Lifecycle management per layer

**Compliance**:
- Audit trail separate from working docs
- Retention policies per layer
- Immutable compliance records

**AI Assistant Optimization**:
- Copilot can navigate layers easily
- Templates co-located for discovery
- Clear directory structure for context

## Alternatives Considered

### Alternative 1: Flat Documentation Structure

**Description**: Keep all docs in `doc/internal/` with minimal subdirectories

**Pros**:
- Simple structure
- Easy to find everything
- No deep nesting

**Cons**:
- Doesn't scale past ~50 files
- No separation of concerns
- Hard to understand purpose of documents
- Compliance vs working docs mixed
- External vs internal unclear

**Reason for rejection**: Already experiencing navigation pain at 98 files; won't scale to hundreds

### Alternative 2: 3-Layer Model (External, Internal, Archive)

**Description**: Simpler model with just external, internal, archive

**Pros**:
- Simpler than 5 layers
- Still separates external from internal
- Archive for old docs

**Cons**:
- "Internal" becomes catch-all (governance, technical, process, compliance all mixed)
- No separation between decision records vs technical docs vs guides
- Compliance not isolated for audit
- Doesn't solve navigation problem

**Reason for rejection**: Too coarse; doesn't address separation of concerns needed for scaling

### Alternative 3: Audience-Based (Developer, Operations, Compliance, Public)

**Description**: Organize by audience rather than content type

**Pros**:
- Each audience finds their docs easily
- Clear intended reader

**Cons**:
- Documents often serve multiple audiences (ADRs for developers and auditors)
- Duplicate documents for different audiences
- Governance decisions fit poorly (developer? operation? both?)
- Technical docs used by both developers and operations

**Reason for rejection**: Content type more stable than audience; documents serve multiple audiences

### Alternative 4: Lifecycle-Based (Draft, Review, Published, Archived)

**Description**: Organize by document lifecycle stage

**Pros**:
- Clear lifecycle management
- Draft vs published obvious

**Cons**:
- Documents move directories as lifecycle changes (breaks links)
- Hard to find documents (where is ADR-0005? draft or published?)
- Governance decisions never "draft" (they're accepted or not)
- Technical docs permanently "published" (living documents)

**Reason for rejection**: Lifecycle should be metadata (status field), not directory structure

### Alternative 5: No Reorganization (Status Quo)

**Description**: Keep current structure, improve metadata/indexing only

**Pros**:
- No file moves
- No broken links
- No reorganization effort

**Cons**:
- Doesn't solve navigation problem (already painful at 98 files)
- Doesn't separate concerns (governance, technical, process, compliance mixed)
- Doesn't prepare for team growth
- Doesn't isolate compliance for audit

**Reason for rejection**: Problem will only get worse as project grows; reorganize now while solo developer

## Consequences

### Positive

- **Clear Purpose**: Each document's purpose obvious from location
- **Separation of Concerns**: Governance, technical, process, compliance clearly separated
- **Scalability**: Each layer scales independently to hundreds of documents
- **Discovery**: Easier to find relevant documentation
- **Maintainability**: Update frequency and authority clear per layer
- **Compliance**: Audit trail isolated for regulatory requirements
- **Team Growth**: New team members navigate easily
- **External Readiness**: External docs separated and customer-ready
- **AI Assistant Friendly**: Copilot navigates layers effectively

### Negative

- **Initial Effort**: Must reorganize 98 existing files
- **Link Updates**: Must update hundreds of cross-references
- **Learning Curve**: Team must learn 5-layer model (minimal, clear patterns)
- **More Directories**: Deeper directory structure (mitigated by clear README per layer)

### Neutral

- **Git History**: File moves preserve history with `git mv`
- **Tooling**: No changes to tooling required (still Markdown + GitHub)
- **Maintenance**: More directories but each has clear purpose

## Implementation

### Requirements

**Directory Structure**:
- Create 5 layer directories with README.md per layer
- Define purpose, audience, lifecycle per layer
- Document cross-reference conventions

**File Reorganization**:
- Move 98 existing files to appropriate layers
- Update cross-references (hundreds of links)
- Preserve Git history with `git mv`
- Validate no broken links

**Documentation Updates**:
- Update TEMPLATES-GUIDE.md with new structure
- Update .github/copilot-instructions.md with layer descriptions
- Update CHARTER.md and ROADMAP.md references (if moved)

**Validation**:
- Run markdown-link-check to verify no broken links
- Review sample documents from each layer
- Test Copilot navigation across layers

### Migration Plan

**Phase 1: Create Layer Structure** (2 hours):
1. Create directory structure per 5 layers
2. Create README.md per layer (purpose, audience, lifecycle)
3. Update root `doc/README.md` with layer overview

**Phase 2: Move Files** (4 hours):
1. Move technical docs (services, best-practices, examples) → `technical/`
2. Move process docs (LOCAL-DEVELOPMENT-GUIDE, copilot-references) → `process/`
3. Move compliance docs (audit, gaps, archive) → `compliance/`
4. Move standards → `governance/POLs/` (Gap 4 remediation)
5. External docs remain (mostly empty currently)

**Phase 3: Update Cross-References** (4 hours):
1. Update governance docs (ADRs, PDRs, POLs) cross-references
2. Update Entity Management Service docs cross-references
3. Update best practices cross-references
4. Update TEMPLATES-GUIDE.md
5. Update .github/copilot-instructions.md

**Phase 4: Validation** (2 hours):
1. Run markdown-link-check across all docs
2. Fix any broken links
3. Review sample documents from each layer
4. Test Copilot suggestions across layers

**Total Effort**: ~12 hours (spread across Days 1-3 of Week 1)

### File Move Mapping

**To `doc/internal/technical/`**:
- `doc/internal/services/` → `doc/internal/technical/services/`
- `doc/internal/best-practices/` → `doc/internal/technical/best-practices/`
- `doc/internal/examples/` → `doc/internal/technical/examples/`

**To `doc/internal/process/`**:
- `doc/internal/LOCAL-DEVELOPMENT-GUIDE.md` → `doc/internal/process/development/local-setup.md`
- `doc/internal/copilot-references/` → `doc/internal/process/tools/copilot-references/`
- Consider: `doc/internal/CHARTER.md` → keep at root or move to `process/project-charter.md`
- Consider: `doc/internal/ROADMAP.md` → keep at root or move to `process/project-roadmap.md`

**To `doc/internal/compliance/`**:
- `doc/internal/audit/` → `doc/internal/compliance/audit/`
- `doc/internal/gaps/` → `doc/internal/compliance/gaps/`
- `doc/internal/archive/legacy/` → `doc/internal/compliance/archive/legacy/`

**To `doc/internal/governance/POLs/`** (Gap 4):
- `doc/internal/standards/MULTI-TENANT-SEAM-ARCHITECTURE.md` → `doc/internal/governance/POLs/POL-multi-tenant-architecture.md`
- `doc/internal/standards/EVENT-SCHEMA-STANDARDS.md` → `doc/internal/governance/POLs/POL-event-schema-standards.md`
- `doc/internal/standards/API-DESIGN-STANDARDS.md` → `doc/internal/governance/POLs/POL-api-design-standards.md`
- `doc/internal/standards/RBAC-SPECIFICATION.md` → `doc/internal/governance/POLs/POL-rbac-specification.md`

**Keep at Current Location**:
- `doc/internal/governance/` (ADRs, PDRs, POLs, templates) - already correct layer
- `doc/internal/initial-thoughts.md` - keep at root (historical reference)
- `doc/internal/TEMPLATES-GUIDE.md` - keep at root (master index)
- `doc/internal/BEST-PRACTICES-GUIDE.md` - move to `technical/best-practices/BEST-PRACTICES-GUIDE.md`

### Success Criteria

**After Implementation**:
- [ ] 5 layer directories created with README.md each
- [ ] All 98+ files moved to appropriate layers
- [ ] All cross-references updated (no broken links)
- [ ] TEMPLATES-GUIDE.md updated with new structure
- [ ] .github/copilot-instructions.md updated with layers
- [ ] markdown-link-check passes (zero broken links)
- [ ] Git history preserved for all moved files
- [ ] Copilot navigates layers effectively

**Validation**:
- Run `markdown-link-check` across all files
- Sample 10 documents across layers, verify links work
- Test Copilot: "Show me the actor patterns best practices" → finds `technical/best-practices/architecture/actor-patterns.md`
- Test Copilot: "Show me the service canvas template" → finds `governance/templates/SERVICE-CANVAS.md`

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Broken cross-references | High | Systematic link updates, automated link checking, thorough testing |
| Git history lost | Medium | Use `git mv` for all file moves (preserves history) |
| Too complex for solo developer | Low | Clear README per layer, master index (TEMPLATES-GUIDE.md), simple patterns |
| Copilot confused by new structure | Low | Update copilot instructions, test navigation, layers are logical |
| Team rejects 5-layer model | Low | Clear rationale, industry-standard patterns, improves over time |
| Reorganization takes too long | Medium | Time-boxed to Days 1-3 of Week 1, prioritize high-value moves |

## Validation

Success criteria:

- 5-layer architecture clearly defined and documented
- All 98+ files organized into appropriate layers
- Cross-references updated and validated (zero broken links)
- Copilot navigates layers effectively
- New documents easy to place in correct layer
- Team (when exists) navigates documentation easily
- Compliance documentation isolated for audit

Metrics:
- Time to find a document (subjective improvement)
- Zero broken links (markdown-link-check)
- Number of cross-layer references (should be reasonable)
- Copilot suggestion accuracy (subjective improvement)

## Related Decisions

- [PDR-0007: Documentation Asset Management](../PDRs/PDR-0007-documentation-asset-management.md) - Templates co-location strategy
- [PDR-0001: Documentation Standards](../PDRs/PDR-0001-documentation-standards.md) - Documentation principles
- [ADR-0002: Documentation-First Approach](./ADR-0002-documentation-first-approach.md) - Why document decisions
- Future PDR: Documentation lifecycle workflows (draft → review → published)
- Future PDR: Compliance documentation retention policy

## Related Best Practices

- [Documentation as Code](https://www.writethedocs.org/guide/docs-as-code/) - Write the Docs community
- [Diátaxis Framework](https://diataxis.fr/) - Documentation structure (tutorial, how-to, reference, explanation)
- [Arc42 Template](https://arc42.org/) - Software architecture documentation
- [C4 Model](https://c4model.com/) - Software architecture diagrams

**Note**: This ADR adopts a purpose/audience-based model rather than Diátaxis (tutorial/how-to/reference/explanation) because TJMPaaS documentation spans governance, compliance, and technical concerns beyond user-facing docs.

## References

- [Write the Docs](https://www.writethedocs.org/) - Documentation best practices
- [Diátaxis Documentation Framework](https://diataxis.fr/) - Documentation structure
- [Arc42 Architecture Documentation](https://arc42.org/) - Software architecture documentation
- [Documentation System (Divio)](https://documentation.divio.com/) - 4-layer documentation model
- [Google Developer Documentation Style Guide](https://developers.google.com/style) - Documentation standards
- [Markdown Link Check](https://github.com/tcort/markdown-link-check) - Broken link detection

## Notes

**Why 5 Layers?**

5 layers balance separation of concerns with manageable complexity:
- **External** (customer-facing) vs **Internal** (team-facing) fundamental split
- **Internal** subdivided by purpose:
  - **Governance** (decisions) - project-wide authority
  - **Technical** (implementation) - how system works
  - **Process** (workflows) - how we work
  - **Compliance** (audit) - regulatory requirements

Each layer has distinct purpose, audience, lifecycle, and update frequency.

**Why Not Diátaxis?**

Diátaxis (tutorial, how-to, reference, explanation) excellent for user-facing documentation but doesn't fit TJMPaaS needs:
- Governance decisions don't fit tutorial/how-to/reference/explanation
- Compliance audit trails don't fit Diátaxis categories
- Best practices research is reference+explanation (spans categories)
- Service design docs span multiple Diátaxis categories

TJMPaaS needs purpose/audience-based organization more than content-type-based (Diátaxis).

**CHARTER.md and ROADMAP.md Placement**

Two options:
1. **Keep at `doc/internal/` root** (current): High visibility, accessed frequently, project-level scope
2. **Move to `doc/internal/process/`**: Fits layer definition (project process/planning)

**Recommendation**: Keep at root for visibility and prominence. They're special documents (project charter and roadmap) that transcend layers.

**Standards → POLs Migration**

Gap 4 remediation moves standards to governance/POLs/ because standards ARE policies (mandatory requirements):
- MULTI-TENANT-SEAM-ARCHITECTURE.md → POL-multi-tenant-architecture.md (mandatory pattern)
- EVENT-SCHEMA-STANDARDS.md → POL-event-schema-standards.md (mandatory format)
- API-DESIGN-STANDARDS.md → POL-api-design-standards.md (mandatory conventions)
- RBAC-SPECIFICATION.md → POL-rbac-specification.md (mandatory security model)

This aligns with governance model: POLs are mandatory rules, standards are mandatory rules → standards belong in POLs.

**Future Team Considerations**

As team grows:
- External docs become customer-facing (require marketing review)
- Process docs become team-maintained (require team consensus)
- Governance docs become team-reviewed (require architect approval)
- Compliance docs become audit-ready (require compliance officer approval)

5-layer model scales to team collaboration with clear roles and responsibilities.

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-12-14 | Initial draft (proposed) | Tony Moores |

