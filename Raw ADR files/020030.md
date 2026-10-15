# ADR-046: Plan-to-VTM Bridge Architecture

## Status

Proposed

## Context

VTM CLI is a token-efficient task management system designed for AI-assisted development with Claude Code. It achieves 99% token reduction by providing surgical access to task manifests instead of loading entire project contexts.

The Plan domain creates Architecture Decision Records (ADRs) and Technical Specifications during the research and planning phase. These documents contain valuable implementation details, acceptance criteria, and task breakdowns. However, they currently exist as standalone documents that require manual transformation into executable VTM tasks.

### Current State

1. **Planning Phase**: Developers use the Plan domain to create:
   - ADRs documenting architectural decisions and rationale
   - Technical specifications with implementation details and task breakdowns

2. **Execution Phase**: Developers use VTM CLI to:
   - Track task progress with `vtm next`, `vtm start`, `vtm complete`
   - Generate minimal context for Claude Code with `vtm context`
   - Manage dependencies and blocked tasks

3. **The Gap**: No automated bridge between planning artifacts and VTM tasks. Developers must:
   - Manually copy task descriptions from ADRs/specs
   - Infer and encode task dependencies
   - Risk misalignment between plan and execution

### Key Requirements

1. **Semantic Understanding**: Dependencies should be based on semantic relationships (e.g., "database schema must exist before API implementation"), not just document order
2. **Token Efficiency**: Must align with VTM's core principle of minimal context
3. **Safety**: Preview-first workflow to prevent incorrect task ingestion
4. **Maintainability**: Must not duplicate VTM CLI logic or create competing implementations
5. **Flexibility**: Should handle varying document formats and structures
6. **Composability**: Should integrate with existing VTM CLI commands

## Decision

We will implement a **Plan-to-VTM Bridge** using an agent-based extraction approach with VTM CLI extensions.

### Architecture Components

#### 1. VTM CLI Extensions

Extend the VTM CLI with two new commands:

**`vtm summary --incomplete`**

- Returns JSON summary of tasks with status='pending' or 'in-progress'
- Enables token-efficient context sharing with agents
- Example output:

```json
{
  "incomplete_tasks": [
    {
      "dependencies": [],
      "id": "TASK-001",
      "status": "pending",
      "title": "Set up database schema"
    },
    {
      "dependencies": ["TASK-001"],
      "id": "TASK-002",
      "status": "in-progress",
      "title": "Create API endpoints"
    }
  ]
}
```

**`vtm ingest <file>`**

- Accepts JSON file containing new tasks to merge into vtm.json
- Validates task structure, assigns sequential IDs
- Performs dependency validation and conflict detection
- Generates preview showing before/after state
- Requires confirmation before committing changes
- Updates stats atomically (leverages existing VTMWriter)

#### 2. Agent-Based Extraction

Create a specialized agent prompt that:

1. **Extracts Tasks**: Reads ADR + Technical Spec and identifies implementation tasks
2. **Pulls Context**: Calls `vtm summary --incomplete` to get existing VTM state
3. **Analyzes Dependencies**: Performs semantic analysis to determine which new tasks depend on:
   - Other new tasks (e.g., "API implementation" depends on "schema design")
   - Existing incomplete tasks (e.g., "integration tests" depend on existing "TASK-002: API endpoints")
4. **Generates JSON**: Outputs structured task list in VTM-compatible format

#### 3. Orchestration Command

Create `.claude/commands/plan-to-vtm.md` that:

1. Validates inputs (ADR + spec exist, vtm.json exists)
2. Launches agent with planning documents and VTM context
3. Agent outputs tasks.json
4. Calls `vtm ingest tasks.json` to generate preview
5. Prompts user for confirmation
6. Commits changes if approved

### Workflow Example

```bash
# User has created ADR and spec during planning
# ls: adr/ADR-045-new-feature.md, specs/new-feature-spec.md

# Run bridge command
/plan-to-vtm adr/ADR-045-new-feature.md specs/new-feature-spec.md

# Agent analyzes documents + pulls incomplete VTM tasks
# Generates tasks.json with intelligent dependencies

# vtm ingest shows preview:
# ┌─────────┬──────────────────────────┬──────────────┐
# │ Task ID │ Title                    │ Dependencies │
# ├─────────┼──────────────────────────┼──────────────┤
# │ TASK-008│ Design database schema   │ []           │
# │ TASK-009│ Implement API layer      │ [TASK-008]   │
# │ TASK-010│ Add integration tests    │ [TASK-002,   │
# │         │                          │  TASK-009]   │
# └─────────┴──────────────────────────┴──────────────┘
#
# Depends on existing: TASK-002 (Create API endpoints - in-progress)
#
# Confirm ingestion? (y/n)

# User types 'y', tasks committed to vtm.json
# Stats automatically recalculated via VTMWriter
```

## Rationale

### Why Agent-Based Extraction?

1. **Semantic Understanding**: Agents can understand _why_ tasks depend on each other, not just parse structure
   - Example: Agent recognizes "API endpoints need database schema" even if not explicitly stated
   - Can infer dependencies across existing and new tasks

2. **Format Flexibility**: Works with any ADR/spec structure
   - No brittle regex patterns or hardcoded parsers
   - Adapts to different writing styles and document formats

3. **Maintainability**: Agent prompts are easier to update than complex parsers
   - Can add new extraction rules via prompt refinement
   - No code changes needed for new document patterns

4. **Composability**: Agent can leverage multiple data sources
   - Reads ADR + spec together for complete context
   - Pulls existing VTM state via CLI commands
   - Makes holistic decisions about dependencies

### Why Extend VTM CLI?

1. **Single Source of Truth**: All VTM operations go through one codebase
   - No competing implementations of task validation
   - No drift between .claude/lib utilities and core VTM logic

2. **Testability**: VTM CLI has comprehensive test coverage
   - New commands inherit existing test infrastructure
   - Type safety via TypeScript

3. **Atomicity**: Leverages existing VTMWriter's atomic write operations
   - Crash-safe via write-to-temp + rename pattern
   - Automatic stats recalculation

4. **Reusability**: CLI commands can be used independently
   - `vtm summary` useful for other automation needs
   - `vtm ingest` enables manual task import workflows

### Why Preview-First?

1. **Safety**: Prevents incorrect task ingestion
   - User reviews dependencies before commit
   - Catches agent mistakes in dependency analysis

2. **Transparency**: User sees exactly what changes will occur
   - Clear diff of before/after state
   - Highlights dependencies on existing tasks

3. **Control**: User maintains final authority
   - Can reject and refine agent output
   - Can manually edit tasks.json before re-ingestion

### Why Token-Efficient Context?

1. **Aligns with VTM Principles**: Only passes incomplete tasks to agent
   - Completed tasks irrelevant for dependency analysis
   - Reduces context size by ~70% on mature projects

2. **Scalability**: Works on projects with hundreds of tasks
   - Agent only sees pending/in-progress tasks
   - Prevents token budget exhaustion

## Alternatives Considered

### 1. Parser-Based Extraction (Rejected)

**Approach**: Write regex/string parsers to extract tasks from ADRs and specs.

**Reasons for Rejection**:

- **Brittle**: Breaks when document format changes
- **Unmaintainable**: Complex regex patterns hard to debug
- **No Semantic Understanding**: Can't infer dependencies intelligently
- **Format-Locked**: Each new document style requires new parser code

### 2. Manual Transformation (Rejected)

**Approach**: Developers manually copy tasks from ADRs to vtm.json.

**Reasons for Rejection**:

- **Not Scalable**: Time-consuming for large features
- **Error-Prone**: Easy to miss dependencies or introduce typos
- **Defeats Purpose**: VTM aims to reduce manual overhead

### 3. Utilities in .claude/lib (Rejected)

**Approach**: Create bash/TypeScript utilities in .claude/lib to handle task ingestion.

**Reasons for Rejection**:

- **Duplicates Logic**: Would reimplement VTMWriter's validation and atomic writes
- **Divergence Risk**: Two codebases handling VTM operations could drift
- **No Test Coverage**: .claude/lib utilities harder to test than VTM CLI
- **Not Reusable**: Limited to this specific use case

### 4. Dumb Append (Rejected)

**Approach**: Simply append tasks from ADR/spec to vtm.json without dependency analysis.

**Reasons for Rejection**:

- **Breaks Workflow**: Tasks start prematurely without proper blockers
- **Loses Intelligence**: Doesn't leverage semantic understanding of relationships
- **Poor UX**: Forces developers to manually fix dependencies later

## Consequences

### Positive

1. **Seamless Planning-to-Execution Flow**
   - Planning artifacts directly feed into execution
   - No manual copying or reformatting needed

2. **Intelligent Dependency Management**
   - Agent understands semantic relationships between tasks
   - Properly blocks tasks that depend on incomplete work

3. **Maintains Token Efficiency**
   - Only incomplete tasks passed to agent
   - Aligns with VTM's core value proposition

4. **Single Source of Truth**
   - All VTM operations centralized in VTM CLI
   - No competing implementations or logic duplication

5. **Safe by Default**
   - Preview-first workflow prevents mistakes
   - User reviews all changes before commit

6. **Extensible Architecture**
   - New CLI commands useful for other automation
   - Agent prompts easy to refine and improve

### Negative

1. **Agent Reliability**
   - Agents can make mistakes in dependency analysis
   - **Mitigation**: Preview-first workflow catches errors before commit

2. **Requires Claude Code**
   - Bridge depends on agent execution environment
   - **Mitigation**: Acceptable given VTM's design for AI-assisted development

3. **Learning Curve**
   - Developers must understand bridge workflow
   - **Mitigation**: Document common patterns and provide examples

4. **Agent Token Costs**
   - Each bridge execution consumes tokens
   - **Mitigation**: Token-efficient context via `vtm summary --incomplete`

## Implementation Notes

### Phase 1: VTM CLI Extensions

1. **Add `vtm summary` command**
   - Implement in `src/index.ts` using Commander.js
   - Add `--incomplete` flag to filter by status
   - Output JSON to stdout for easy piping
   - Add unit tests in `src/__tests__/`

2. **Add `vtm ingest` command**
   - Implement validation logic (task structure, dependencies)
   - Generate preview with table formatting (use chalk + cli-table3)
   - Require user confirmation via readline
   - Use VTMWriter for atomic writes and stats recalculation
   - Add integration tests

### Phase 2: Agent Prompt

1. **Create `.claude/commands/plan-to-vtm.md`**
   - Instructions for reading ADR + spec files
   - Template for calling `vtm summary --incomplete`
   - Guidelines for dependency analysis (semantic relationships)
   - JSON output format specification
   - Example tasks.json structure

2. **Dependency Analysis Guidelines**
   - Infrastructure before application code
   - Schema/data models before business logic
   - Business logic before tests
   - Tests before deployment tasks
   - Cross-reference with existing incomplete tasks

### Phase 3: Validation & Testing

1. **Test Cases**
   - Valid task ingestion (sequential IDs, proper dependencies)
   - Invalid dependency references (non-existent task IDs)
   - Circular dependency detection
   - Conflict with existing tasks (duplicate IDs)
   - Empty vtm.json (first ingestion)

2. **End-to-End Testing**
   - Create test ADR + spec in examples/
   - Run full bridge workflow
   - Verify tasks appear in vtm.json with correct dependencies
   - Verify stats recalculated correctly

### Phase 4: Documentation

1. **Update CLAUDE.md**
   - Add bridge workflow section
   - Document new CLI commands
   - Provide usage examples

2. **Create Examples**
   - Example ADR with task breakdown
   - Example technical spec
   - Example tasks.json output
   - Example preview output

### Technical Considerations

1. **ID Assignment**: `vtm ingest` must assign sequential IDs (TASK-XXX) starting after highest existing ID
2. **Dependency Validation**: Must validate all dependency IDs exist (either in vtm.json or new tasks)
3. **Atomic Writes**: Leverage VTMWriter's write-to-temp + rename pattern
4. **Stats Recalculation**: Automatically happens via VTMWriter.updateTask() after ingestion
5. **Error Handling**: Clear error messages for validation failures

## Related ADRs

- **ADR-001**: VTM Token-Efficient Architecture (establishes core principles)
- **ADR-XXX**: Plan Domain Architecture (if exists - defines ADR/spec structure)

## References

- VTM CLI Source: `src/index.ts`, `src/lib/vtm-reader.ts`, `src/lib/vtm-writer.ts`
- Example VTM: `examples/vtm-example.json`
- Existing ADR Example: `examples/adr/adr-001-task-manager.md`
- Technical Spec Example: `examples/specs/spec-task-manager-cli.md`
