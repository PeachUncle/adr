# ADR-20251011-persona-dashboard

**Status**: Active  
**Date**: 2025-10-11  
**Module**: `management/persona-management`  
**Topic**: Persona Management Dashboard  
**Trace ID**: `adr-persona-mgmt-dashboard`

---

## Context

ScreenGraphVibe uses `.mcp/personas/*.json` to define AI agent personas (Ian, Rino, Jacob, Phil) with distinct workflows, Graphiti protocols, and before/after task procedures. Managing these manually is error-prone. A dashboard is required to:
- Edit persona configs (name, role, thinking patterns)
- Enforce BEFORE/AFTER task requirements (critical for Graphiti workflows)
- Manage module ownership and sync to CODEOWNERS
- Track performance and PR split decisions
- Maintain 40% unit + 30% E2E coverage

---

## Options

### A: Manual JSON editing
**Pros**: Simple, no code  
**Cons**: Error-prone, no validation, no BEFORE/AFTER enforcement

### B: CLI tool
**Pros**: Scriptable, batch operations  
**Cons**: No visual UX, hard to track performance

### C: Web dashboard with TDD
**Pros**: Visual, interactive, validated, E2E tested, performance tracking  
**Cons**: More code to maintain

---

## Decision

**Option C**: Build modular web dashboard under `management/persona-management` (backend package) + `ui/features/management/persona-management` (UI).

**Rationale**:
- Visual editing prevents schema errors; Zod validation enforces contracts
- BEFORE/AFTER toggles ensure Graphiti protocol compliance
- Module ownership + CODEOWNERS sync prevents drift
- Performance analytics inform process improvements
- TDD (40% unit, 30% E2E) ensures reliability

---

## Architecture

```
:management/persona-management (backend package)
├── schema (Zod)
├── adapters (file I/O)
└── tests (5/5 unit)

:backend/features/management
├── personas/routes.ts (CRUD)
└── codeowners/routes.ts (preview/apply)

:ui/features/management/persona-management
├── PersonaList + PersonaEditor
├── ThinkingPatternPanel (BEFORE/AFTER enforcement)
├── FactsAssumptionsPanel (editable rows)
├── ModuleOwnershipPanel (toggles per module)
└── CodeownersPanel (preview/apply)

:tests/e2e
└── persona-management.*.e2e.test.ts (11 passing)
```

---

## Impact

| Module | Impact |
|--------|--------|
| `:data` | None |
| `:backend` | New routes under `/management/*` |
| `:ui` | New page `/management/persona-management` |
| `:agent` | None (reads `.mcp/personas` configs) |
| `:infra` | None |

---

## Next Steps

1. Enhance PersonaEditor with full JSON schema form (all persona fields)
2. Implement analytics retro engine (issue #54)
3. Wire performance dashboard (issue #58)
4. Integrate real-time Graphiti episode writing on save
5. Add CI coverage gates per module

---

**Decided by**: Ian Botts (CTO via AI)  
**Episode ID**: (to be recorded in PR description)

