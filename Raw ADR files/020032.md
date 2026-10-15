---
title: "ADR-048: Session Management CLI Integration"
status: approved
owner: VTM CLI Team
version: 1.0.0
date: 2025-10-30
supersedes: []
superseded_by: null
related_adrs: []
related_specs: []
---

# ADR-048: Session Management CLI Integration

## Status

**Current Status**: APPROVED

**Decision Date**: 2025-10-30

**Supersedes**:

- None

**Superseded By**:

- None

**Related Decisions**:

- None

---

## Context

The VTM CLI includes a `VTMSession` class (`src/lib/vtm-session.ts`) that manages current task state by persisting a task ID to `.vtm-session` file. This enables stateful workflows where users don't need to repeatedly specify task IDs.

### Current Implementation

**What exists:**

- ✅ `VTMSession` TypeScript class with full implementation
- ✅ 17 passing tests covering all functionality
- ✅ Documentation in CLAUDE.md
- ⚠️ `.claude/commands/helpers/session.mjs` - Node.js wrapper script for bash commands

**Current usage pattern:**

```bash
# Bash commands call Node.js helper
node .claude/commands/helpers/session.mjs get
node .claude/commands/helpers/session.mjs set TASK-003
node .claude/commands/helpers/session.mjs clear
```

**Used by:**

- `/vtm:done` (Claude Code slash command) - Reads and clears session
- `/vtm:work` (Claude Code slash command) - **Should set but doesn't** ❌
- `/vtm:start` (Claude Code slash command) - Reads session for smart hints
- `/vtm:context` (Claude Code slash command) - Reads session for current task indicator

### The Problem

The current architecture has several issues:

1. **Inconsistent Interface**: Session management uses a Node.js helper script while all other VTM operations use the main CLI
2. **Developer Experience**: Users cannot manually interact with session state using standard `vtm` commands
3. **Incomplete Integration**: `/vtm:work` doesn't set session state, breaking the promised streamlined workflow
4. **Maintenance Burden**: Separate helper script adds complexity and another file to maintain
5. **Discovery**: Session features are hidden - users don't know they can interact with session state
6. **Architecture Misalignment**: Session is a core VTM feature but accessed through a side-door helper

### Forces

- **Consistency**: All VTM functionality should be accessible through `vtm` CLI
- **Discoverability**: Session commands should appear in `vtm --help`
- **Simplicity**: Fewer moving parts = easier to maintain and understand
- **Type Safety**: TypeScript implementation is robust; bash wrapper is unnecessary
- **Manual Control**: Developers need ability to inspect/manipulate session for debugging
- **Backward Compatibility**: Slash commands must continue working without changes to user-facing behavior

---

## Decision

We will **integrate session management directly into the VTM CLI** by adding three new subcommands under `vtm session`:

```bash
vtm session get           # Get current task ID (exit 0 if set, exit 1 if empty)
vtm session set <id>      # Set current task ID
vtm session clear         # Clear current task and remove session file
```

### Implementation Changes

**1. Add CLI Commands** (`src/index.ts`):

```typescript
const sessionCommand = program
  .command("session")
  .description("Manage current task session")

sessionCommand
  .command("get")
  .description("Get current task ID")
  .action(async () => {
    const session = new VTMSession()
    const currentTask = session.getCurrentTask()
    if (currentTask) {
      console.log(currentTask)
      process.exit(0)
    } else {
      process.exit(1)
    }
  })

// ... set and clear commands
```

**2. Update Slash Commands**:
Replace all `node session.mjs` calls with `vtm session` commands:

```bash
# OLD: node "$SESSION_HELPER" get 2>/dev/null
# NEW: vtm session get 2>/dev/null

# OLD: node "$SESSION_HELPER" set "$TASK_ID" 2>/dev/null
# NEW: vtm session set "$TASK_ID" > /dev/null 2>&1

# OLD: node "$SESSION_HELPER" clear 2>/dev/null
# NEW: vtm session clear > /dev/null 2>&1
```

**3. Remove Helper Script**:
Delete `.claude/commands/helpers/session.mjs` - no longer needed.

**4. Fix Missing Integration**:
Add session tracking to `/vtm:work` after successful task start:

```bash
vtm start "$TASK_ID"
if [[ $? -eq 0 ]]; then
    vtm session set "$TASK_ID" > /dev/null 2>&1
fi
```

### Rationale

**Why CLI integration:**

1. **Consistency**: Matches existing pattern - all VTM operations via `vtm` command
2. **Discoverability**: `vtm --help` shows session management capabilities
3. **Simplicity**: Removes bash/Node.js bridge, uses existing TypeScript implementation directly
4. **Developer Experience**: Manual debugging via `vtm session get` for inspection
5. **Type Safety**: Pure TypeScript path from CLI to implementation
6. **Architecture Alignment**: Session is a first-class VTM feature, not a hidden helper

**Why NOT alternative approaches:**

❌ **Keep helper script**: Maintains architectural inconsistency, poor discoverability
❌ **Inline session logic in bash**: Loses type safety, duplicates logic, harder to test
❌ **Add to existing commands** (e.g., `vtm get-session`): Clutters top-level namespace, doesn't scale
✅ **Subcommand pattern**: Clean namespace, follows Commander.js patterns, extensible

---

## Consequences

### Positive

1. **Unified Interface**: All VTM features accessible through `vtm` CLI
2. **Better DX**: Developers can manually inspect/control session state
3. **Simplified Architecture**: One less helper script, one less bridge between bash/Node
4. **Complete Workflow**: Fixing `/vtm:work` completes the streamlined workflow promise
5. **Discoverability**: Session commands visible in `vtm --help` output
6. **Maintainability**: Single implementation path, easier to understand and modify

### Negative

1. **Breaking Change (Minor)**: `.claude/commands/helpers/session.mjs` removed
   - **Mitigation**: Internal implementation detail, not a public API
   - **Impact**: None - only used by slash commands which are updated in same change

2. **CLI Binary Size**: Marginally increases due to new commands
   - **Mitigation**: Negligible - commands are thin wrappers around existing `VTMSession` class
   - **Impact**: < 1KB

### Neutral

1. **Command Count**: Adds 3 new subcommands under `vtm session`
   - **Note**: Namespaced under `session`, doesn't clutter top-level commands

---

## Implementation Plan

### Phase 1: Add CLI Commands (30 minutes)

- Add `VTMSession` to imports in `src/index.ts`
- Export `VTMSession` from `src/lib/index.ts`
- Implement `vtm session get|set|clear` commands
- Build and test manually

### Phase 2: Update Slash Commands (20 minutes)

- Update `.claude/commands/vtm/work.md` - Add session set
- Update `.claude/commands/vtm/done.md` - Replace helper calls
- Update `.claude/commands/vtm/start.md` - Replace helper calls
- Update `.claude/commands/vtm/context.md` - Replace helper calls

### Phase 3: Cleanup (10 minutes)

- Remove `.claude/commands/helpers/session.mjs`
- Update CLAUDE.md documentation
- Verify no remaining references

### Phase 4: Testing (15 minutes)

- Test `vtm session` commands directly
- Test full workflow: `/vtm:work` → `/vtm:done`
- Test smart hints in `/vtm:start` and `/vtm:context`
- Verify `.vtm-session` file operations

**Total Effort**: ~75 minutes

**Risk Level**: Low (additive changes, internal refactoring only)

---

## Validation

### Acceptance Criteria

**AC1: CLI commands work correctly**

```bash
vtm session set TASK-003
vtm session get                    # Output: TASK-003
vtm session clear
vtm session get                    # Exit code: 1
```

**AC2: Slash commands use CLI**

```bash
/vtm:work TASK-003                 # Sets session
vtm session get                    # Output: TASK-003
/vtm:done                          # Completes TASK-003, clears session
vtm session get                    # Exit code: 1
```

**AC3: Smart hints work**

```bash
/vtm:work TASK-003
/vtm:context TASK-003              # Shows "📌 This is your current task"
/vtm:start TASK-003                # Shows warning about already current
```

**AC4: Helper script removed**

```bash
ls .claude/commands/helpers/session.mjs   # File not found
```

### Testing Strategy

- **Unit Tests**: Existing `vtm-session.test.ts` (17 tests) - no changes needed
- **Integration Tests**: Manual testing of workflows (Phase 4)
- **Regression Tests**: Verify existing session features still work

---

## Migration Path

**Backward Compatibility**: None required - helper script is internal implementation detail.

**Rollout Strategy**:

1. Deploy CLI commands (additive change, no impact)
2. Update slash commands (internal change, no user-facing impact)
3. Remove helper script (cleanup, no user-facing impact)

**Rollback Plan**:

- Revert commit to restore `session.mjs` helper
- No data migration needed (`.vtm-session` file format unchanged)

---

## References

### Related Files

- `src/lib/vtm-session.ts` - Core implementation
- `src/lib/__tests__/vtm-session.test.ts` - Test suite
- `.claude/commands/helpers/session.mjs` - To be removed
- `.claude/commands/vtm/*.md` - Slash commands to update

### Documentation

- CLAUDE.md (lines 229-249) - Session state documentation
- Will add section on new CLI commands

### Prior Art

- Existing VTM CLI follows this pattern for all features
- Git uses similar pattern: `git config get/set`, `git remote add/remove`
- npm uses: `npm config get/set`

---

## Notes

### Design Decisions

**Why exit codes for `vtm session get`?**

- Enables bash conditionals: `if vtm session get > /dev/null; then`
- Standard Unix convention: 0 = success, 1 = not found
- Matches behavior of tools like `git config --get`

**Why separate `get/set/clear` instead of single command with flags?**

- Clearer intent: `vtm session set TASK-003` vs `vtm session --set TASK-003`
- Follows Commander.js subcommand pattern
- More discoverable in help output
- Easier to extend (e.g., future `vtm session list` for history)

**Why not `vtm set-session` / `vtm get-session`?**

- Clutters top-level namespace (currently 10 commands)
- Doesn't scale if we add more session operations
- Subcommand pattern is more extensible

### Future Enhancements

Possible future additions under `vtm session`:

- `vtm session history` - Show recent tasks
- `vtm session switch <id>` - Validation + set in one step
- `vtm session status` - Show current task with details

These can be added later without breaking changes.

---

## Approval

**Approved By**: VTM CLI Team

**Date**: 2025-10-30

**Implementation Priority**: High (fixes incomplete `/vtm:work` integration)
