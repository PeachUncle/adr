# ADR 002: Directory-Based Persistence Architecture

## Status

**ACCEPTED** - (2025-11-07)

Decision: Adopt flat directory structure with task ID partitioning and symlink-based views (Option 2) with JSON format for task files and automatic migration from legacy single-file format.

## Context

### Problem Statement

The current single-file `todos.json` persistence architecture has several limitations that hinder scalability and feature development:

1. **No Artifact Support**: Cannot store task-related files (images, documents, diagrams) alongside task data
2. **Monolithic Merge Conflicts**: Any concurrent edit creates file-wide merge conflicts, even if tasks don't overlap
3. **Limited Metadata**: Cannot add rich markdown descriptions or project-level planning documents
4. **Poor Scalability**: Loading/parsing entire file becomes slow with >10,000 tasks
5. **Inflexible Organization**: Cannot support multiple views (by project, status, priority) without duplicating data
6. **No Project Structure**: Projects exist only as string fields, no ability to add project-level metadata/plans

### Technical Background

**Current Architecture:**
- **Storage**: Single file `todos.json` at repository root
- **Structure**: `{ "todos": [Todo[], ...] }` JSON array
- **Operations**: Load entire file → modify in-memory → write entire file
- **Git Integration**: Each operation commits single file
- **Conflict Resolution**: Last-Write-Wins (LWW) on field-level timestamps
- **Performance**: ~94% test coverage, <500ms operations for <10,000 tasks

**Root Causes:**
1. Single file design chosen for simplicity during initial MVP
2. No consideration for artifact storage in original design
3. Assumed small-scale usage (<1000 tasks)
4. No multi-dimensional organization requirements initially

**Impact:**
- Users cannot attach screenshots/diagrams to tasks
- Difficult to organize large task sets
- Merge conflicts more frequent as team size grows
- Cannot create project plans or rich task documentation
- Limited query performance as data grows

**Constraints:**
- Must maintain Git-based version control (fundamental architecture)
- Must preserve Last-Write-Wins conflict resolution semantics
- Must support automatic sync with remote repositories
- Must maintain >90% test coverage
- Cannot break existing repositories (need migration path)
- Must support MCP protocol interface (16 tools via stdio)
- Must maintain Web UI performance (Kanban board queries)

## Decision Drivers

1. **Artifact Storage**: Enable storing images, documents, and files with tasks
2. **Scalability**: Handle >10,000 tasks without performance degradation
3. **Conflict Reduction**: Minimize merge conflicts in multi-user scenarios
4. **Organization Flexibility**: Support multiple views (project, status, priority, tags) without duplication
5. **Rich Metadata**: Enable project plans, task descriptions in markdown, metadata files
6. **Query Performance**: Fast access patterns for common operations (list by status, filter by project)
7. **Backward Compatibility**: Existing `todos.json` repositories must continue working
8. **Maintainability**: Keep architecture simple and testable
9. **Git Integration**: Preserve atomic commits and version control benefits
10. **Migration Safety**: Zero data loss during migration from legacy format

## Considered Options

### Option 1: Project-Centric Hierarchy

**Description:**
Organize by project first, then tasks within each project. Projects get their own directory with metadata.

**Structure:**
```
todos/
├── by-project/
│   ├── Ecolab/
│   │   ├── PROJECT.md
│   │   └── tasks/
│   │       ├── {task-id-1}/task.json
│   │       └── {task-id-2}/task.json
│   └── Personal/
│       ├── PROJECT.md
│       └── tasks/...
└── views/
    ├── by-status/...  (symlinks)
    └── by-priority/...
```

**Implementation:**
- Primary structure: `by-project/{project}/tasks/{task-id}/`
- Secondary views via symlinks
- Project-level `PROJECT.md` for planning documents
- Task files remain JSON

**Pros:**
- ✅ Natural organization for project-centric workflows
- ✅ Project metadata easily accessible
- ✅ Clear ownership boundaries
- ✅ Intuitive directory browsing

**Cons:**
- ❌ Tasks without projects need special handling (orphaned directory)
- ❌ Renaming projects requires moving entire directory tree
- ❌ Complex migration logic (need to scan all projects)
- ❌ Harder to iterate all tasks (must traverse project dirs)
- ❌ Symlink updates more complex (nested paths)

**Effort:** Medium-High (4-6 days)
**Risk:** Medium (project rename complexity)

---

### Option 2: Flat Structure with Symlink Views

**Description:**
Single flat directory of tasks partitioned by task ID, with symlink-based views for organization dimensions.

**Structure:**
```
todos/
├── tasks/
│   ├── {task-id-1}/
│   │   ├── task.json
│   │   ├── README.md (optional)
│   │   └── artifacts/
│   │       └── image.png
│   └── {task-id-2}/
│       └── task.json
├── by-project/
│   ├── Ecolab/
│   │   ├── PROJECT.md
│   │   └── {task-id} → ../../tasks/{task-id}/
│   └── Personal/
│       └── {task-id} → ../../tasks/{task-id}/
├── by-status/
│   ├── todo/ → ../../tasks/{task-id}/
│   ├── in-progress/
│   └── done/
├── by-priority/
│   ├── urgent/
│   └── high/
├── by-tag/
│   └── bug/ → ../../tasks/{task-id}/
└── by-assignee/
    └── user/ → ../../tasks/{task-id}/
```

**Implementation:**
- Primary storage: `tasks/{task-id}/task.json`
- All views use symlinks pointing to `tasks/` entries
- DirectoryManager handles task CRUD
- SymlinkManager maintains view integrity
- Project metadata: `by-project/{project}/PROJECT.md`

**Pros:**
- ✅ Simple primary structure (flat by ID)
- ✅ All views are secondary (easy to add/remove)
- ✅ No data duplication (symlinks)
- ✅ Easy to iterate all tasks (single directory)
- ✅ Task operations don't move files (just update symlinks)
- ✅ Project rename is metadata-only change
- ✅ Flexible: can add new views without restructuring
- ✅ Cross-platform symlink support (Windows junction fallback)

**Cons:**
- ❌ Symlink management complexity
- ❌ Windows symlink limitations (need junction fallback)
- ❌ Broken symlinks possible if not careful
- ❌ Need symlink rebuild on sync/conflict resolution

**Effort:** Medium (3-5 days)
**Risk:** Low (symlinks well-understood, fallback strategies available)

---

### Option 3: Hybrid Multi-Dimensional Structure

**Description:**
Multiple organizational dimensions in primary structure before using symlinks.

**Structure:**
```
todos/
├── data/
│   └── {project}/
│       └── {status}/
│           └── {task-id}/
│               └── task.json
└── views/
    ├── by-priority/... (symlinks)
    └── by-tag/... (symlinks)
```

**Implementation:**
- Primary: `data/{project}/{status}/{task-id}/`
- Must move files when status/project changes
- Fewer symlinks needed
- More structure, less flexibility

**Pros:**
- ✅ Fewer symlinks to manage
- ✅ Some organization "baked in"
- ✅ Natural hierarchical browsing

**Cons:**
- ❌ File moves required for status/project changes (Git churn)
- ❌ Complex migration and sync logic
- ❌ Harder to add new organizational dimensions
- ❌ Path-based queries more complex
- ❌ Project/status rename requires directory moves
- ❌ Higher conflict probability (directory structure changes)

**Effort:** High (5-7 days)
**Risk:** Medium-High (complex file move logic)

---

### Option 4: Database-Backed with File Artifacts

**Description:**
Use embedded database (SQLite) for metadata, file system only for artifacts.

**Structure:**
```
todos/
├── todos.db (SQLite)
└── artifacts/
    └── {task-id}/
        └── image.png
```

**Implementation:**
- SQLite database for all todo metadata
- File system only for binary artifacts
- Still commit .db file to Git
- Fast queries via SQL

**Pros:**
- ✅ Fast queries (indexed SQL)
- ✅ Transactional operations
- ✅ Rich query capabilities
- ✅ No symlink complexity
- ✅ Proven technology

**Cons:**
- ❌ Binary database file in Git (poor diffs)
- ❌ Conflict resolution extremely complex (can't merge .db files)
- ❌ Loses human-readable benefits of JSON/markdown
- ❌ Cannot browse/edit tasks with standard tools
- ❌ Breaks "Git as source of truth" philosophy
- ❌ Harder to debug and audit
- ❌ Migration from JSON complex

**Effort:** Very High (8-10 days)
**Risk:** High (Git+SQLite integration problems)

---

### Option 5: Keep Single File + External Artifacts Directory

**Description:**
Minimal change: keep `todos.json`, add separate `artifacts/` directory.

**Structure:**
```
todos.json
artifacts/
  {task-id}/
    image.png
```

**Implementation:**
- Keep current TodoRepository logic
- Add artifact reference fields to Todo type
- Separate artifact upload/download logic
- Symlinks for views if needed

**Pros:**
- ✅ Minimal change to existing code
- ✅ Fast implementation (1-2 days)
- ✅ Low risk
- ✅ Solves artifact storage problem

**Cons:**
- ❌ Doesn't address other limitations (merge conflicts, scalability, organization)
- ❌ Still monolithic JSON file
- ❌ No project-level metadata
- ❌ No rich task descriptions
- ❌ Technical debt remains
- ❌ Will need refactoring later anyway

**Effort:** Low (1-2 days)
**Risk:** Very Low

---

## Comparison Matrix

| Criterion | Option 1: Project | Option 2: Flat+Symlinks | Option 3: Hybrid | Option 4: Database | Option 5: Minimal |
|-----------|------------------|------------------------|------------------|-------------------|------------------|
| **Effort** | Med-High (4-6d) | Medium (3-5d) | High (5-7d) | Very High (8-10d) | Low (1-2d) |
| **Risk** | Medium | Low | Med-High | High | Very Low |
| **Artifact Support** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Conflict Reduction** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ |
| **Organization Flex** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **Git Integration** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Human Readable** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Query Speed** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Maintainability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Future-Proof** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ |

## Decision Outcome

**ACCEPTED**: Option 2 - Flat Structure with Symlink Views

### Rationale

After evaluating all options, **Option 2 (Flat Structure with Symlink Views)** provides the best balance of:

1. **Flexibility**: Easy to add new organizational views without restructuring
2. **Simplicity**: Primary structure is straightforward (flat by ID)
3. **Git-Friendly**: Per-task files minimize merge conflicts
4. **Scalability**: Flat iteration, targeted writes, symlink views don't duplicate data
5. **Maintainability**: Clear separation between data (tasks/) and views (by-*)
6. **Low Risk**: Symlinks are well-understood with fallback strategies
7. **Moderate Effort**: 3-5 days vs. 8-10 for database or 5-7 for hybrid

**Why Not Option 1 (Project-Centric):**
- Tasks without projects are second-class citizens
- Project rename operations more complex
- Less flexible for adding new views

**Why Not Option 3 (Hybrid):**
- File moves on property changes create Git churn
- Less flexible for future organization needs
- Higher complexity in migration and sync

**Why Not Option 4 (Database):**
- Binary files in Git are anti-pattern
- Conflict resolution becomes nearly impossible
- Loses human-readable benefits of plain text

**Why Not Option 5 (Minimal):**
- Doesn't solve core problems (conflicts, scalability, organization)
- Technical debt remains
- Will require refactoring later anyway

### Implementation Plan

**Detailed Implementation Plan**: See [implementation-plan.md](./implementation-plan.md)

**Status**: Phases 1-4 COMPLETED (80 tests passing) | Phases 5-10 PENDING

Following **strict TDD approach** - write failing tests first, then implement to make them pass.

#### Phase 1: ADR Documentation ✅ COMPLETED
- [x] Create `docs/adr/002-directory-based-persistence/decision.md`
- [x] Create `docs/adr/002-directory-based-persistence/implementation-plan.md`

#### Phase 2: DirectoryManager (TDD Cycle) ✅ COMPLETED

**RED - Write Failing Tests**
- [x] Create `tests/unit/data/DirectoryManager.test.ts`
- [x] Write tests for `ensureDirectoryStructure()`
- [x] Write tests for `getTaskPath()`
- [x] Write tests for `readTask()` (JSON + README.md)
- [x] Write tests for `writeTask()` (atomic writes)
- [x] Write tests for `deleteTask()`
- [x] Write tests for `listAllTasks()`
- [x] Run tests → All fail ✗

**GREEN - Implement Minimal Code**
- [x] Create `src/data/DirectoryManager.ts`
- [x] Implement each method to pass tests
- [x] Use atomic write pattern from GitManager
- [x] Run tests → All 36 pass ✓

**REFACTOR - Clean Up**
- [x] Extract common patterns
- [x] Add JSDoc comments
- [x] Improve error messages
- [x] Run tests → Still pass ✓

**Result**: 36 tests passing, full implementation with README extraction and artifact support

#### Phase 3: SymlinkManager (TDD Cycle) ✅ COMPLETED

**RED - Write Failing Tests**
- [x] Create `tests/unit/data/SymlinkManager.test.ts`
- [x] Write tests for `updateSymlinks()` (all view types)
- [x] Write tests for `removeSymlinks()`
- [x] Write tests for `rebuildAllSymlinks()`
- [x] Write tests for cross-platform compatibility
- [x] Run tests → All fail ✗

**GREEN - Implement**
- [x] Create `src/data/SymlinkManager.ts`
- [x] Implement symlink operations (Unix + Windows junction fallback)
- [x] Run tests → All 30 pass ✓

**REFACTOR**
- [x] Extract VIEW_DIRECTORIES constant
- [x] Add comprehensive JSDoc
- [x] Run tests → Still pass ✓

**Result**: 30 tests passing, cross-platform symlink support with intelligent update strategy

#### Phase 4: Migration Logic (TDD Cycle) ✅ COMPLETED

**RED - Write Failing Tests**
- [x] Add migration tests to `tests/unit/data/TodoRepository.test.ts`
- [x] Test `isLegacyFormat()`
- [x] Test `migrateLegacyToDirectory()` (backup, convert, commit)
- [x] Test edge cases (empty, special chars, no project, rollback)
- [x] Run tests → Migration tests fail ✗

**GREEN - Implement Migration**
- [x] Add DirectoryManager and SymlinkManager to TodoRepository
- [x] Add `isLegacyFormat()` to TodoRepository
- [x] Add `migrateLegacyToDirectory()` to TodoRepository
- [x] Run tests → All 14 migration tests pass ✓

**REFACTOR**
- [x] Add comprehensive JSDoc
- [x] Improve error messages with backup path
- [x] Run tests → Still pass ✓

**Result**: 14 tests passing, automatic migration with backup and data integrity preservation

#### Phase 5: Update TodoRepository CRUD (TDD Cycle) 🚧 PENDING

**RED - Update Existing Tests**
- [ ] Modify `tests/unit/data/TodoRepository.test.ts`
- [ ] Update tests for directory-based loading
- [ ] Add tests for directory-specific behavior
- [ ] Run tests → Some fail ✗

**GREEN - Refactor TodoRepository**
- [ ] Replace file operations with DirectoryManager calls
- [ ] Integrate SymlinkManager for view updates
- [ ] Keep existing logic for filters/search (in-memory)
- [ ] Run tests → All pass ✓

**REFACTOR**
- [ ] Simplify code using new abstractions
- [ ] Remove redundant operations
- [ ] Run tests → Still pass ✓

**Next**: This phase will integrate DirectoryManager and SymlinkManager into all CRUD operations

#### Phase 6: Update Conflict Resolution (TDD Cycle) 📋 PENDING

**RED - Write Failing Tests**
- [ ] Update `src/git/__tests__/ConflictResolver.test.ts`
- [ ] Add tests for directory-based conflicts
- [ ] Test LWW semantics across files
- [ ] Run tests → Conflict tests fail ✗

**GREEN - Update ConflictResolver**
- [ ] Add directory-aware conflict detection
- [ ] Support per-file resolution
- [ ] Maintain LWW algorithm
- [ ] Run tests → All pass ✓

**REFACTOR**
- [ ] Extract conflict detection logic
- [ ] Run tests → Still pass ✓

#### Phase 7: Update SyncManager (TDD Cycle) 📋 PENDING

**RED - Update Tests**
- [ ] Update `src/git/__tests__/SyncManager.test.ts`
- [ ] Remove todos.json hardcoding assumptions
- [ ] Run tests → Sync tests fail ✗

**GREEN - Update SyncManager**
- [ ] Remove hardcoded 'todos.json' at line 149
- [ ] Detect conflicts in todos/ directory
- [ ] Batch commit multiple file changes
- [ ] Run tests → All pass ✓

**REFACTOR**
- [ ] Optimize batch operations
- [ ] Run tests → Still pass ✓

#### Phase 8: Integration Tests (TDD Cycle) 📋 PENDING

**RED - Write Integration Tests**
- [ ] Create `src/__tests__/integration/directory-persistence.integration.test.ts`
- [ ] Test full CRUD cycle
- [ ] Test concurrent operations
- [ ] Test sync with remote
- [ ] Test migration
- [ ] Run tests → Fail ✗

**GREEN - Fix Integration Issues**
- [ ] Address integration bugs
- [ ] Ensure all components work together
- [ ] Run tests → All pass ✓

#### Phase 9: Performance Tests (TDD Cycle) 📋 PENDING

**RED - Write Performance Tests**
- [ ] Create `src/__tests__/performance/directory-performance.test.ts`
- [ ] Benchmark: load 1000 tasks <500ms
- [ ] Benchmark: write task <100ms
- [ ] Benchmark: list by status <50ms
- [ ] Run tests → Check benchmarks ✓

**GREEN - Optimize if Needed**
- [ ] Add caching if performance issues
- [ ] Optimize directory scanning
- [ ] Run tests → Meets criteria ✓

#### Phase 10: Documentation & Cleanup 📋 PENDING

- [ ] Update `README.md` with new directory structure
- [ ] Update `QUICKSTART.md` for new users
- [ ] Create `docs/MIGRATION.md` guide for existing users
- [ ] Update `CLAUDE.md` project instructions
- [ ] Run full test suite → All pass ✓
- [ ] Check coverage → >90% ✓
- [ ] Manual testing with MCP server and Web UI
- [ ] Git commit with all changes

### Success Criteria

- [ ] All existing tests passing (maintain >90% coverage)
- [ ] New DirectoryManager and SymlinkManager tests passing
- [ ] Migration from `todos.json` works flawlessly (zero data loss)
- [ ] All MCP tools continue working
- [ ] Web UI Kanban board maintains performance
- [ ] Symlinks work on both Unix and Windows
- [ ] Can store artifacts (images, files) in task directories
- [ ] Can add PROJECT.md files to project directories
- [ ] Can add README.md to individual tasks
- [ ] Performance meets criteria: <500ms loads, <100ms writes, <50ms queries
- [ ] Git commits remain atomic
- [ ] Conflict resolution maintains LWW semantics
- [ ] Documentation updated and comprehensive

## Consequences

### Positive

- ✅ **Artifact Support**: Can store images, documents, diagrams with tasks
- ✅ **Reduced Conflicts**: Per-task files minimize merge conflict scope
- ✅ **Flexible Organization**: Easy to add new views (by-tag, by-assignee, custom)
- ✅ **Scalability**: Handles 10,000+ tasks efficiently
- ✅ **Rich Metadata**: PROJECT.md for projects, README.md for tasks
- ✅ **Human Readable**: Plain text files browsable with any tool
- ✅ **Git-Friendly**: Granular diffs, clear history, atomic operations
- ✅ **Maintainable**: Clear separation of concerns (data vs. views)
- ✅ **Query Performance**: Fast list/filter operations via symlink views
- ✅ **Future-Proof**: Easy to extend with new organizational dimensions

### Negative

- ⏱️ **3-5 days implementation**: Requires significant refactoring and testing
- 📚 **Symlink Complexity**: Need to manage symlink lifecycle (create, update, remove)
- 🪟 **Windows Compatibility**: Need junction fallback for Windows symlink limitations
- 🔄 **Migration Risk**: Must ensure zero data loss during migration
- 📝 **Documentation Debt**: Need comprehensive docs for new structure
- 🧪 **Test Expansion**: Need extensive tests for DirectoryManager, SymlinkManager, migration
- ⚠️ **Broken Symlinks**: Possible if not careful with symlink management
- 💾 **Disk Usage**: More inodes used (one per task directory vs. one file)
- 🔍 **Debugging**: More files to inspect when issues occur

### Neutral

- Directory structure more complex but better organized
- File system becomes the "index" (no separate index file)
- Git repository grows in file count but shrinks in conflict scope
- Symlinks may confuse users unfamiliar with the concept
- Need to educate team on new structure and conventions

## Related Decisions

- ADR 001: Svelte 5 Runes Testing Strategy (testing patterns)
- ADR 003: (Future) Comment System Architecture (Git vs. file system)
- ADR 004: (Future) Large-Scale Archiving Strategy (>10,000 tasks)

## References

- [Git Data Model](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- [Symlinks in Git](https://git-scm.com/docs/git-symbolic-ref)
- [Data Lake Architecture Patterns](https://docs.aws.amazon.com/whitepapers/latest/building-data-lakes/data-lake-storage-layers.html)
- [Node.js fs.symlink()](https://nodejs.org/api/fs.html#fssymlinkpath-target-type-callback)
- [Windows Junction Points](https://learn.microsoft.com/en-us/windows/win32/fileio/junctions)
- Related Todos:
  - `019a2ca6-82cd-7dca-a456-09876040c617` - Explore partitioning strategies
  - `019a2cd8-707d-7cca-a10a-3290789ebdab` - Support persistence of artifacts

## Notes

- Symlinks are well-supported in Git since version 1.6 (2009)
- Windows symlinks require admin privileges, but junctions do not
- Most modern development environments handle symlinks transparently
- Directory-based structures are common in modern tools (e.g., Notion, Obsidian, Logseq)
- "Everything is a file" Unix philosophy applies well here
- This refactoring enables future features: comments, attachments, project plans, custom views

---

## Summary

We've decided to adopt a **flat directory structure with symlink-based views (Option 2)** for task persistence. This architecture addresses all identified limitations of the single-file approach while maintaining Git integration, testability, and performance. The implementation follows strict TDD principles with comprehensive test coverage throughout.

**Key Benefits:**
- Artifact storage (images, files) alongside tasks
- Reduced merge conflicts (per-task granularity)
- Flexible multi-dimensional organization (project, status, priority, tags, assignee)
- Scalable to 10,000+ tasks
- Rich metadata support (PROJECT.md, README.md)

**Implementation Approach:**
Following TDD (Test-Driven Development):
1. Write failing tests first (RED)
2. Implement minimal code to pass (GREEN)
3. Refactor while keeping tests green (REFACTOR)
4. Maintain >90% test coverage throughout

The 3-5 day effort provides a robust, maintainable solution that enables future feature development and scales with growing usage.

---

**Last Updated:** 2025-11-07
**Decision Date:** 2025-11-07
**Author:** Claude Code + User
**Status:** ACCEPTED
**Implementation:** TDD approach with 10 phases
