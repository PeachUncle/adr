# ADR-003: Bundle-Based Tool Distribution

## Status
Accepted

## Context
ToolVault serves as a runtime host for analysis tools, enabling different software deployments (including Debrief) to provide tools without building them directly into their codebase. The system must support predictable, repeatable operation across diverse deployment environments while maintaining a simple workflow for tool contributors.

## Decision
We will implement a bundle-based tool distribution architecture with the following characteristics:

### Bundle Architecture
- **Format**: ZIP archives containing self-contained tool collections
- **Dependencies**: Fully embedded - each bundle includes all required dependencies to eliminate version conflicts and environment variability
- **Structure**: Standardized directory layout enforced by automated tooling
- **Metadata**: Rich `index.json` format describing tool capabilities, input/output schemas, and UI rendering hints

### Versioning Strategy
- **Timestamp-based versioning**: Bundle versions derived from the datetime of the most recent commit in the source repository
- **Deterministic and automatic**: No manual version management required
- **Chronological ordering**: Enables "newer is better" update decisions
- **Traceability**: Direct mapping back to source repository state

### Bundle Creation Workflow
- **Automated indexer tool**: Scans tool repositories and generates compliant bundles with proper metadata
- **Pre-commit validation**: Enforces documentation standards (pyDoc/jsDoc) and structural requirements
- **Quality gates**: Ensures bundle consistency without burdening contributors

### Distribution Mechanism
- **Direct file distribution**: Bundles distributed as files through various mechanisms (local filesystem, network shares, etc.)
- **Deployment flexibility**: Each environment manages bundles through their preferred distribution method
- **No infrastructure dependencies**: Eliminates need for central registry services

## Rationale

### Self-Contained Dependencies
Complete dependency embedding ensures predictable operation across all deployment scenarios. This prevents the "works on my machine" problem and enables true portability between environments like development, testing, and production deployments.

### Rich Metadata for Contextual Discovery
The `index.json` format enables downstream software to offer contextually relevant tools based on user selections without requiring navigation to detailed tool pages. This supports intelligent tool discovery and workflow integration.

### Timestamp Versioning
Using commit timestamps provides automatic, deterministic versioning that maintains chronological ordering while eliminating the complexity of semantic versioning for bundle collections.

### Automated Bundle Creation
The indexer tool ensures structural consistency while pre-commit validation maintains documentation quality. This approach scales contributor onboarding while maintaining bundle standards.

### File-Based Distribution
Direct file distribution maximizes deployment flexibility, allowing organizations to integrate bundles into their existing asset management workflows without requiring additional infrastructure.

## Consequences

### Positive
- **Predictable operation**: Self-contained bundles eliminate environment-specific failures
- **Simple deployment**: Bundles can be managed like any other file asset
- **Scalable contribution**: Automated tooling reduces barrier to entry for tool contributors
- **Flexible integration**: Downstream software can implement contextual tool discovery
- **Infrastructure independence**: No central services required for operation

### Negative
- **Storage overhead**: Dependency duplication across bundles increases storage requirements
- **Bundle size**: Self-contained approach may result in larger bundle sizes
- **Update complexity**: Full bundle replacement required for any changes

### Mitigation Strategies
- Bundle size is not a practical concern for expected tool types
- Storage costs are acceptable trade-off for operational predictability
- Timestamp versioning simplifies update decisions (newer replaces older)

## Implementation Notes
- Pre-commit hooks will validate pyDoc/jsDoc presence and correctness
- Indexer tool development is prioritized for Phase 4 of the project roadmap
- Bundle validation tooling will be provided for deployment environments