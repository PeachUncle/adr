# ADR-0004: Adopt Session-Based Context Management with YAML Front-matter

## Status
**Accepted**

## Context

AI agent workflows require persistent state tracking across multiple interactions, phase transitions, and agent handoffs. Traditional approaches face several challenges:

- Context scattered across multiple systems (git, issues, comments, external tools)
- No standardized format for agent state persistence
- Difficulty reconstructing decision history and work progress
- Inconsistent approaches to storing metadata, todos, and session state
- Manual effort required to maintain context across long-running tasks

The AgenticOps Value Train™ requires seamless context handoffs between agents and phases, with traceability of decisions, artifacts, and progress throughout the development lifecycle.

## Decision

We will implement a session-based context management system using structured YAML front-matter in markdown files:

### Core Components
1. **ACTIVE_SESSION.md**: Central session state file with YAML front-matter containing:
   - Session metadata (ID, timestamps, operator, assistant)
   - Current work context (mode, phase, agent, task details)
   - Task context (parent issues, project links)
   - Work progress (TodoWrite integration)
   - Artifacts (created/modified files, dependencies)
   - Session notes (decisions, blockers, next steps, handoff requirements)
   - Git context (repository, branch, working state)
   - Tool access permissions

2. **Structured Schema**: Defined required and optional fields for consistency
3. **Update Requirements**: Clear rules for when and how to update session context
4. **Integration Points**: TodoWrite, git workflow, and agent handoffs

### File Location and Management
- Primary location: `/docs/session-context/ACTIVE_SESSION.md`
- Legacy support: `/docs/session-context/_legacy/` for historical sessions
- Version control: Track changes through git for audit trail

## Consequences

### Positive
- **Persistent Context**: Agent state survives between interactions and handoffs
- **Structured Data**: YAML front-matter enables programmatic processing
- **Audit Trail**: Git history provides complete record of context evolution
- **Tool Integration**: Easy integration with existing markdown and YAML tooling
- **Human Readable**: Context remains accessible to both humans and AI agents
- **Search Capability**: Text-based format supports grep, search, and analysis tools

### Negative
- **Manual Discipline**: Requires consistent updates to remain accurate
- **Merge Conflicts**: Multiple agents updating same file can cause conflicts
- **File Size Growth**: Long sessions may produce large context files
- **Format Validation**: Need tooling to ensure YAML remains valid

### Neutral
- **Single Source Dependency**: Context centralized in one file per session
- **Schema Evolution**: Structure may need updates as requirements change

## Rationale

Session-based context management with YAML front-matter was chosen because:

1. **Agent Continuity**: Enables seamless handoffs between AI agents and human operators
2. **Structured Yet Flexible**: YAML provides structure while remaining human-readable
3. **Version Control Native**: Leverages existing git infrastructure for history and collaboration
4. **Tool Ecosystem**: Excellent support in editors, CI/CD, and automation tools
5. **Incremental Adoption**: Can be implemented gradually without disrupting existing workflows

### Alternatives Considered
- **Database Storage**: More complex setup, harder to version and review
- **JSON Format**: Less human-readable than YAML
- **Separate Metadata Files**: Fragmented context across multiple files
- **Issue Comments**: Limited structure and harder to process programmatically
- **External Systems**: Adds dependency and complexity

### Implementation Strategy
1. Define and document complete schema structure
2. Create validation tools for YAML format checking
3. Integrate with TodoWrite for automatic progress tracking
4. Implement automated updates at key workflow points
5. Establish migration path for legacy context formats

## Related Decisions
- Enables ADR-0001 (AgenticOps Value Train) by providing required session tracking
- Supports ADR-0002 (Auto-Pilot) by maintaining context for autonomous operation
- Integrates with ADR-0003 (Git Hooks) for YAML validation enforcement

## References
- [ACTIVE_SESSION.md Schema](../../session-context/ACTIVE_SESSION.md) for current implementation
- [Session Workflow Rules](../../rules/session-workflow.md) for usage guidelines
- [Value Train Specification](../../agenticops-value-train.md) - Session management section
- [YAML Specification](https://yaml.org/spec/) for format reference