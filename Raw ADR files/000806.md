---
docid: ADR-098
title: ADR 052 Mcp Enhanced Bugfixing
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

---
docid: ADR-052
title: MCP-Enhanced Bugfixing Workflow
status: Proposed
decision_date: 2026-01-07
owner: @TechLead, @Security
tags: ["MCP", "Quality", "Debugging", "Tooling"]
---

# ADR-052: MCP-Enhanced Bugfixing Workflow

## Decision

Integrate Model Context Protocol (MCP) tools into a systematic bugfixing workflow to:
- **Accelerate** root cause analysis via automated diagnostics
- **Improve** fix quality through targeted MCP validation chains
- **Standardize** bug resolution across the organization
- **Capture** lessons learned automatically for knowledge base

## Context

Current bugfixing workflow is manual and fragmented:
- Developers investigate bugs without structured guidance
- Root cause analysis duplicates effort (similar bugs investigated multiple times)
- Lessons learned are optional and rarely documented
- MCP tools exist but are underutilized for debugging tasks

**Available MCP Tools** (from `.vscode/mcp.json`):
- `typescript-mcp` - Type analysis, symbol usage
- `roslyn-mcp` - C# type analysis, diagnostics
- `vue-mcp` - Component validation
- `htmlcss-mcp` - Accessibility, responsive design
- `chrome-devtools-mcp` - Runtime debugging, performance
- `database-mcp` - Query analysis
- `monitoring-mcp` - Error tracking, logs
- `git-mcp` - Blame, commit history
- `security-mcp` - Vulnerability detection
- `performance-mcp` - Code analysis

## Solution

### 1. **Diagnostic MCP Chain by Bug Category**

| Bug Type | MCP Chain | Purpose |
|----------|-----------|---------|
| **Type/Reference Errors** | `typescript-mcp` → `roslyn-mcp` | Validate types at error location |
| **UI Rendering** | `vue-mcp` → `htmlcss-mcp` → `chrome-devtools-mcp` | Component validation + browser state |
| **API Failures** | `database-mcp` → `monitoring-mcp` | Query validation + error logs |
| **Performance** | `performance-mcp` → `chrome-devtools-mcp/lighthouse` | Code analysis + Lighthouse audit |
| **Security** | `security-mcp` → `git-mcp` | Vulnerability check + find when introduced |
| **i18n** | `typescript-mcp` (key validation) | Verify translation keys exist |
| **Async/Race** | `typescript-mcp` (await detection) | Identify missing awaits |

### 2. **Quick Bug-Fix Prompts** (`/bug-quick-*`)

New prompts for common bug patterns:

```
/bug-null-check       → Defensive null/undefined guards
/bug-async-race       → Fix missing awaits and race conditions
/bug-type-mismatch    → Resolve TypeScript type mismatches
/bug-i18n-missing     → Find and add missing translation keys
/bug-lint-fix         → Auto-fix linting violations
```

Each prompt:
- Runs targeted MCP diagnostics
- Applies automatic fixes where safe
- Validates fix quality with post-MCP checks
- Updates lessons.md with pattern captured

### 3. **Chrome DevTools MCP for Runtime Debugging**

**Enable** `chrome-devtools` in `.vscode/mcp.json` for:
- Console error capture
- Network request inspection
- DOM state visualization
- Performance profiling
- Visual regression detection

Integrated into `/debug-runtime` prompt for interactive sessions.

### 4. **Auto-Lessons-Learned Integration**

After bug resolution:
1. Analyze bug pattern (root cause category)
2. Extract prevention pattern
3. Add structured entry to `.ai/knowledgebase/lessons.md`
4. Include: date, files, cause, fix pattern, prevention rule
5. Reference in future bug analysis

Example:
```markdown
## [2026-01-07] Async Race in WidgetConfigurator

**Root Cause**: Data fetch not awaited before render
**Files**: `src/components/WidgetConfigurator.vue`
**Fix Pattern**: Add v-if guard on async data: `v-if="data?.ready"`
**Prevention**: Always check loading state before template refs
**MCP Used**: vue-mcp, typescript-mcp
```

### 5. **Enhanced `/bug-analysis` Prompt**

Update `PRM-008` to run MCP pre-analysis:

```yaml
Steps:
  1. Auto-collect (before human review):
     - get_errors on affected files
     - git-mcp/blame on recent changes
     - typescript-mcp type validation
     - Check lessons.md for similar issues
     
  2. Present consolidated context to developer
  
  3. Developer applies fix
  
  4. Auto-validate with targeted MCP checks
     - Type safety
     - No new linting violations
     - No security regressions
```

## Tradeoffs

| Benefit | Cost |
|---------|------|
| Faster root cause analysis | Initial setup of MCP chains |
| Standardized fixes | Learning curve for new prompts |
| Knowledge capture | Requires discipline to document |
| Reduced duplicate bugs | MCP overhead (5-10s per analysis) |

## Implementation Sequence

1. **Immediate** (Phase 1)
   - Enable `chrome-devtools-mcp` ✅
   - Create `/bug-quick-*` prompt templates ✅
   - Document in [KB-055] Security MCP Best Practices

2. **Sprint 1** (Phase 2)
   - Update `/bug-analysis` prompt with MCP checks
   - Create bug classification system
   - Test with 5 representative bugs

3. **Sprint 2** (Phase 3)
   - Auto-lessons-learned generation
   - Integrate into `/auto-lessons-learned` prompt
   - Train team on workflow

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| MCP tools provide incorrect analysis | Always require human review before fix |
| Performance overhead | Cache MCP results, run async |
| Tool failures block debugging | Graceful fallback to manual investigation |

## Metrics

- **Time to RCA** (Root Cause Analysis): Current ~30min → Target ~10min
- **Duplicate bug reduction**: Track repeat issues, target 70% reduction
- **Lessons captured**: Current ~20% → Target >80% of bugs documented
- **Fix validation**: Automated checks catch regressions, target 100% coverage

## References

- [KB-055] Security MCP Best Practices - Overall MCP usage patterns
- [KB-053] TypeScript MCP Integration
- [KB-054] Vue MCP Integration Guide
- [KB-064] Chrome DevTools MCP Server
- [PRM-008] Bug Analysis Prompt
- [PRM-017 through PRM-021] Quick Bug-Fix Prompts
- [PRM-022] Auto-Lessons-Learned Prompt

## Decision

**Approved** - Proceed with Phase 1 implementation immediately.

Phase 2 and Phase 3 contingent on Phase 1 success metrics.

---

**Status**: ACCEPTED  
**Date**: 2026-01-07  
**Owner**: @TechLead, @Security  
**Reviewers**: @Architect, @Backend, @Frontend
