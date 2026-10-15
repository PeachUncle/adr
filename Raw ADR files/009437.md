# 0016. File Ignore System for Coding Tools

**Status:** Proposed
**Date:** 2025-11-10
**Deciders:** Development Team
**Technical Story:** Implement ignore functionality to prevent file operations on unwanted files (node_modules, .git, .env, etc.)

---

## Context

The Forge coding agent provides file operations (read, list, search) that recursively traverse directories. Without filtering, these operations include large dependency directories (node_modules, vendor), version control metadata (.git), environment files (.env), and other files that clutter results and can be massive in size.

### Background

Current file tools ([`list_files.go`](../../pkg/tools/coding/list_files.go), [`search_files.go`](../../pkg/tools/coding/search_files.go), [`read_file.go`](../../pkg/tools/coding/read_file.go)) operate on all files within workspace boundaries without content filtering. This creates several issues:

1. **Performance**: Scanning node_modules or vendor directories is extremely slow
2. **Token Usage**: Including massive files in context wastes tokens
3. **UX**: Results are cluttered with irrelevant files
4. **Security**: Accidentally exposing .env or secrets in file listings

### Problem Statement

We need a flexible, user-configurable system to filter files from tool operations while maintaining workspace security boundaries and providing sensible defaults.

### Goals

- Filter common problematic paths (node_modules, .git, .env) by default
- Support standard .gitignore pattern syntax for familiarity
- Allow per-project customization via .forgeignore
- Maintain performance for large codebases
- Provide clear feedback when ignored files are accessed

### Non-Goals

- Implementing full gitignore spec (some advanced features may be simplified)
- Supporting ignore patterns for specific tools (system-wide only)
- Providing UI for managing ignore patterns (file-based only)

---

## Decision Drivers

* **Developer Experience**: Users expect .gitignore-style patterns
* **Performance**: Must handle large directory trees efficiently
* **Security**: Should not bypass workspace boundaries
* **Flexibility**: Allow per-project customization
* **Maintainability**: Simple, testable implementation

---

## Considered Options

### Option 1: Hardcoded Patterns Only

**Description:** Maintain a fixed list of ignore patterns in code.

**Pros:**
- Simple implementation
- No parsing complexity
- Predictable behavior

**Cons:**
- No user customization
- Requires code changes for new patterns
- May ignore files users want to access

### Option 2: Parse .gitignore Only

**Description:** Reuse existing .gitignore file from workspace root.

**Pros:**
- No additional configuration needed
- Familiar to developers
- Automatically synced with git

**Cons:**
- Git-specific patterns may not match tool needs
- No way to override without modifying .gitignore
- Missing when .gitignore doesn't exist

### Option 3: Separate .forgeignore Only

**Description:** Create Forge-specific ignore file.

**Pros:**
- Tool-specific customization
- Independent from git configuration
- Clear ownership

**Cons:**
- Requires user setup
- Not leveraging existing .gitignore
- Additional file to maintain

### Option 4: Layered Approach (Defaults + .gitignore + .forgeignore)

**Description:** Combine hardcoded defaults, .gitignore parsing, and optional .forgeignore override.

**Pros:**
- Works out of the box with sensible defaults
- Respects existing .gitignore patterns
- Allows project-specific overrides
- Maximum flexibility

**Cons:**
- Most complex implementation
- Multiple sources of truth
- Need clear precedence rules

---

## Decision

**Chosen Option:** Option 4 - Layered Approach

### Rationale

The layered approach provides the best developer experience by:

1. **Working immediately** with sensible defaults (node_modules, .git, etc.)
2. **Respecting existing patterns** from .gitignore (most projects have this)
3. **Allowing customization** via .forgeignore when needed
4. **Being non-invasive** - no required configuration

Pattern precedence (highest to lowest):
1. `.forgeignore` patterns (if file exists)
2. `.gitignore` patterns (if file exists)  
3. Hardcoded default patterns

This matches user expectations: project-specific overrides beat shared config beats defaults.

---

## Consequences

### Positive

- File operations automatically skip node_modules, .git, .env without configuration
- Projects with .gitignore get automatic filtering
- Power users can fine-tune with .forgeignore
- Clear, predictable behavior with well-defined precedence
- Performance improvement on large codebases

### Negative

- Complexity in ignore pattern parsing and merging
- Need to handle parse errors gracefully
- Three sources to check for each file (slight overhead)
- Users need to understand pattern precedence

### Neutral

- Additional file (.forgeignore) in workspace (optional)
- Pattern syntax must be documented
- Test coverage requirements increase

---

## Implementation

### Architecture

Create new `IgnoreMatcher` component in [`pkg/security/workspace/ignore.go`](../../pkg/security/workspace/ignore.go):

```go
type IgnoreMatcher struct {
    patterns []ignorePattern // Compiled patterns with precedence
}

func (m *IgnoreMatcher) ShouldIgnore(path string) bool
func (m *IgnoreMatcher) LoadPatterns(workspaceDir string) error
```

Integrate into [`workspace.Guard`](../../pkg/security/workspace/guard.go):

```go
type Guard struct {
    workspaceDir string
    ignoreMatcher *IgnoreMatcher // New field
}

func (g *Guard) ShouldIgnore(path string) bool
```

Update file tools to check before processing:
- [`list_files.go`](../../pkg/tools/coding/list_files.go): Skip ignored entries in directory scan
- [`search_files.go`](../../pkg/tools/coding/search_files.go): Skip ignored files in walk
- [`read_file.go`](../../pkg/tools/coding/read_file.go): Return error if file is ignored

### Default Patterns

```
node_modules/
.git/
.env
.env.*
*.log
.DS_Store
vendor/
__pycache__/
*.pyc
.vscode/
.idea/
dist/
build/
tmp/
temp/
coverage/
.next/
.nuxt/
target/
```

### Pattern Syntax

Support gitignore-style patterns:
- `dir/` - Directory-only patterns
- `*.ext` - Glob patterns
- `!exception` - Negation patterns
- `#comment` - Comments (ignored)
- Blank lines (ignored)

### Error Handling

- Parse errors: Log warning, skip invalid pattern, continue
- Missing files: Silent (graceful degradation)
- Ignored file access: Return clear error message

### Migration Path

No migration needed - feature is additive and backward compatible.

---

## Validation

### Success Metrics

- File listing operations complete 10x faster on projects with node_modules
- Zero .env files appear in search results by default
- 95%+ of users don't need custom .forgeignore
- No performance regression on small projects

### Monitoring

- Track patterns loaded per workspace
- Log pattern parse errors
- Measure file operation performance before/after
- Monitor user feedback on ignored file errors

---

## Related Decisions

- [ADR-0011](0011-coding-tools-architecture.md) - Coding Tools Architecture
- [ADR-0010](0010-tool-approval-mechanism.md) - Tool Approval Mechanism

---

## References

- [gitignore documentation](https://git-scm.com/docs/gitignore)
- [Go filepath.Match](https://pkg.go.dev/path/filepath#Match)
- [doublestar library](https://github.com/bmatcuk/doublestar) - Potential implementation reference

---

## Notes

**Case Sensitivity**: Patterns are case-sensitive (matching gitignore behavior on Unix systems).

**Performance**: Pattern matching happens after workspace boundary checks but before file I/O, minimizing overhead.

**Future Enhancement**: Could add per-tool ignore patterns (e.g., search_files_ignore) if needed.

**Last Updated:** 2025-11-10