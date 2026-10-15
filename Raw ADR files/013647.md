# ADR: Backlog Structure Migration to Status-Based Organization

**Date**: 2025-10-12
**Status**: Approved
**Decision**: Migrate from category-based task organization to status-based backlog structure

## Context

The project currently has multiple slash commands (`/next`, `/groom`, `/sync`) that expect a status-based backlog structure (`backlog/by-status/`), but the actual context network uses a category-based structure (`tasks/features/`, `tasks/refactoring/`, etc.).

### Current Structure
```
context-network/
├── tasks/
│   ├── features/
│   ├── refactoring/
│   ├── performance/
│   └── task-012-extract-usage-...-2025-09-19.md
├── planning/
│   └── [feature-name]/
│       └── task-breakdown.md
└── processes/
    └── task-planning-and-prioritization.md
```

### Problems
1. **Command mismatch**: Slash commands expect different structure than exists
2. **Task lifecycle unclear**: Hard to see what's ready vs in-progress vs completed
3. **Workflow friction**: Commands like `/next` can't find tasks to work on
4. **Sync integration**: `/sync` creates `sync-state.json` but no structure to update
5. **Status scattered**: Task status information spread across multiple files

## Decision

Implement a status-based backlog structure that aligns with modern agile workflows and existing command expectations.

### New Structure
```
context-network/
├── backlog/
│   ├── by-status/
│   │   ├── ready.md           # Tasks ready for implementation
│   │   ├── planned.md         # Tasks groomed but have dependencies
│   │   ├── in-progress.md     # Tasks currently being worked
│   │   └── completed.md       # Recently completed tasks (archived periodically)
│   ├── by-priority/
│   │   ├── critical.md        # P0 - Critical priority
│   │   ├── high.md            # P1 - High priority
│   │   ├── medium.md          # P2 - Medium priority
│   │   └── low.md             # P3 - Low priority
│   └── archived/
│       └── YYYY-MM/           # Completed tasks by month
│           └── completed-YYYY-MM-DD.md
├── tasks/
│   ├── [TASK-ID].md           # Individual task detail files
│   └── templates/
│       └── task-template.md
└── planning/
    └── [feature-name]/        # Feature-level planning (unchanged)
        └── task-breakdown.md
```

### Task ID Format
- **Feature tasks**: `FEAT-NNN` (e.g., FEAT-001)
- **Infrastructure**: `INFRA-NNN` (e.g., INFRA-004)
- **Refactoring**: `REFACTOR-NNN` (e.g., REFACTOR-012)
- **Bug fixes**: `BUG-NNN` (e.g., BUG-023)
- **Documentation**: `DOCS-NNN` (e.g., DOCS-007)
- **Testing**: `TEST-NNN` (e.g., TEST-015)
- **Performance**: `PERF-NNN` (e.g., PERF-003)

Sequence numbers are zero-padded to 3 digits for sortability.

## Rationale

### Benefits
1. **Command alignment**: Slash commands work without modification
2. **Clear workflow**: Easy to see what's ready to work on
3. **Agile compatible**: Matches Kanban/status-based workflows
4. **Sync integration**: `/sync` can update status files directly
5. **Better visibility**: Status at a glance without searching multiple files
6. **Scalability**: Easy to find next task without scanning hundreds of files

### Why Status-Based > Category-Based
- **Workflow-oriented**: Reflects actual work states, not just categorization
- **Actionable**: "What can I work on now?" is immediately answerable
- **Dynamic**: Tasks move through states, categories are static
- **Tool-friendly**: Commands can easily filter by status
- **Sprint-friendly**: Ready/In-Progress maps directly to sprint boards

## Migration Strategy

### Phase 1: Create Structure (Non-Breaking)
- Create `backlog/` directory structure
- Add status files with documentation
- Create task templates
- Keep existing structure intact

### Phase 2: Task Inventory & ID Assignment
- Scan all existing tasks
- Assign task IDs based on type
- Create individual task detail files in `tasks/[TASK-ID].md`
- Maintain references to old locations

### Phase 3: Populate Status Files
- Analyze each task's actual status
- Add to appropriate status file
- Cross-reference to detail files
- Use sync state data if available

### Phase 4: Update Commands
- `/next` - Update to read from `backlog/by-status/ready.md`
- `/groom` - Update to write to status files
- `/sync` - Update to modify status files directly
- `/plan` - Update to create tasks with proper IDs
- `/implement` - Update to reference task IDs
- `/status` - Update to read from status files
- `/checklist` - Update references

### Phase 5: Validate & Test
- Test each command with new structure
- Verify workflow: plan → groom → next → implement
- Ensure sync integration works
- Check all cross-references

### Phase 6: Deprecate Old Structure
- Move old task files to archive
- Update documentation
- Remove old directory structure
- Clean up references

## Implementation Details

### Status File Format

**`backlog/by-status/ready.md`**:
```markdown
# Ready for Implementation

Tasks that are fully groomed, have no blockers, and are ready to be worked on.

## Critical Priority

### FEAT-042 - Implement V2 minimal agent core
**Priority**: Critical | **Size**: Small | **Effort**: 4-6 hours
**Dependencies**: None
**Description**: Create ~150 line working agent as per V2 minimal-first approach
**Branch**: `feat/v2-minimal-agent`
**Details**: See [tasks/FEAT-042.md](../tasks/FEAT-042.md)

## High Priority

### INFRA-015 - Set up CI/CD pipeline
**Priority**: High | **Size**: Medium | **Effort**: 1-2 days
**Dependencies**: None
**Description**: Automated testing and deployment pipeline
**Branch**: `infra/ci-cd-pipeline`
**Details**: See [tasks/INFRA-015.md](../tasks/INFRA-015.md)

## Medium Priority

[... more tasks ...]

---
*Last updated*: 2025-10-12 by /sync command
*Tasks in ready status*: 12
*Average age in ready*: 3 days
```

### Individual Task File Format

**`tasks/FEAT-042.md`**:
```markdown
# FEAT-042: Implement V2 Minimal Agent Core

**Created**: 2025-10-12
**Status**: ready
**Priority**: Critical
**Size**: Small
**Effort**: 4-6 hours
**Type**: feature

## Description

Create a minimal working agent (~150 lines) as the foundation for V2 architecture, following the minimal-first approach outlined in strategic reset.

## Context

See [decisions/v2_strategic_reset.md](../decisions/v2_strategic_reset.md) for full rationale. This is the first implementation task for V2.

## Acceptance Criteria

- [ ] Agent can accept simple task input
- [ ] Agent can execute basic tool calls
- [ ] Agent returns structured output
- [ ] Core loop is ~150 lines total
- [ ] No enterprise features yet
- [ ] Tests demonstrate basic functionality

## Implementation Notes

**Files to create**:
- `src/v2/agent.ts` - Core agent logic
- `src/v2/agent.test.ts` - Test suite

**Approach**:
1. Simple prompt → LLM → response loop
2. Basic tool call parsing
3. Minimal error handling
4. Focus on working, not sophisticated

## Dependencies

None - this is the first V2 task

## Related

- **Planning**: [planning/v2-minimal-first/task-breakdown.md](../planning/v2-minimal-first/task-breakdown.md)
- **Architecture**: [decisions/v2_strategic_reset.md](../decisions/v2_strategic_reset.md)

## History

- 2025-10-12: Created from backlog migration
```

## Commands Affected

### High Impact (Must Update)
1. **`/next`** - Primary consumer of `ready.md`
2. **`/groom`** - Primary writer to status files
3. **`/sync`** - Updates status files based on reality

### Medium Impact (Should Update)
4. **`/plan`** - Should create tasks with proper IDs
5. **`/implement`** - Should reference task IDs
6. **`/status`** - Should read from status files

### Low Impact (Nice to Update)
7. **`/checklist`** - References task management
8. **`/apply-recommendations`** - May reference backlog

## Risks & Mitigations

### Risk: Breaking Existing Workflows
**Mitigation**: Phased migration keeps old structure during transition

### Risk: Incomplete Migration
**Mitigation**: Clear checklist and validation steps

### Risk: Task ID Collisions
**Mitigation**: Use separate counters per task type (FEAT-001, INFRA-001, etc.)

### Risk: Complex Cross-References
**Mitigation**: Maintain bidirectional links between status files and detail files

### Risk: Command Updates Break Things
**Mitigation**: Test each command after update, keep backups

## Success Criteria

- [ ] All status files exist and are documented
- [ ] All existing tasks have IDs assigned
- [ ] All tasks appear in appropriate status files
- [ ] All slash commands work with new structure
- [ ] Workflow test: `/sync → /groom → /next → /implement` succeeds
- [ ] Old structure is archived, not deleted
- [ ] Documentation updated

## Timeline

- **Phase 1**: 30 minutes (structure creation)
- **Phase 2**: 1-2 hours (task inventory)
- **Phase 3**: 1 hour (populate status files)
- **Phase 4**: 2-3 hours (update commands)
- **Phase 5**: 1 hour (testing)
- **Phase 6**: 30 minutes (cleanup)

**Total estimated time**: 6-8 hours

## Rollback Plan

If migration causes issues:
1. Restore original slash commands from git history
2. Keep new structure but don't enforce its use
3. Gradually fix issues rather than full rollback
4. Old task structure remains in archive for reference

## Approval

**Approved by**: User (2025-10-12)
**Implementation start**: 2025-10-12
**Target completion**: 2025-10-13
