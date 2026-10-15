# ADR-003: TaskMan-v2 Backend API Placeholder Strategy

**Status**: Accepted
**Date**: 2025-01-23
**Authors**: ContextForge Architecture Team
**Context**: TaskMan-v2 Integration Push (Phase 2)

## Context

During the TaskMan-v2 integration from submodule to first-class tracked directory (Phase 1 complete), we needed to decide the fate of the `TaskMan-v2/backend-api/` placeholder directory. This directory was created in earlier development but contains no implementation.

### Current State
- `TaskMan-v2/backend-api/` directory exists in the imported codebase
- Directory contains README.md outlining planned FastAPI + PostgreSQL stack
- No actual implementation code present
- Frontend (React/Vite) is fully implemented and functional
- TypeScript MCP server provides task management functionality

### Decision Factors
1. **Architectural Clarity**: Placeholder signals intent and roadmap
2. **Development Continuity**: Maintains planned architecture visibility
3. **Documentation Value**: README provides technical direction for future implementation
4. **Minimal Overhead**: Empty directory with documentation has negligible cost
5. **Integration Timeline**: Backend implementation will follow Python MCP parity work

## Decision

**Option A: Keep `backend-api/` as Placeholder (SELECTED)**

We will retain the `TaskMan-v2/backend-api/` directory with its README.md documentation as a structural placeholder for the planned FastAPI backend implementation.

### Rationale

1. **Clear Intent Communication**: The placeholder documents our architectural roadmap
2. **Prevents Confusion**: Having the directory prevents developers from creating ad-hoc backend solutions
3. **Documentation Hub**: The README serves as a single source of truth for backend requirements
4. **Minimal Cost**: One directory + README has negligible repository impact
5. **Supports Phased Rollout**: Aligns with Python MCP parity milestone before backend implementation

### Implementation Details

**Directory Structure**:
```
TaskMan-v2/
├── backend-api/
│   ├── README.md              # Architecture and requirements (RETAINED)
│   └── .gitkeep               # Directory persistence marker (ADDED)
├── mcp-server-py/
│   └── README.md              # Python MCP parity plan (ADDED)
└── frontend/                  # Fully implemented React app
```

**README.md Contents** (TaskMan-v2/backend-api/README.md):
- Technology stack: FastAPI + PostgreSQL + Pydantic
- Authentication: JWT integration with Auth0
- API design principles: RESTful, OpenAPI 3.0
- Database schema alignment with PostgreSQL authority
- Performance targets and quality gates
- Integration points with frontend and MCP servers

**.gitkeep Purpose**:
- Ensures directory persists in git even when empty
- Signals intentional placeholder (not accidental empty directory)
- Standard practice for structural directories

## Options Considered

### Option A: Keep Placeholder (SELECTED)
**Pros:**
- Maintains architectural clarity
- Documents technical roadmap
- Zero negative impact on repository
- Prevents ad-hoc solutions
- Aligns with phased development strategy

**Cons:**
- Potentially confusing if not documented (mitigated by this ADR)
- Directory appears "empty" without context

**Decision:** Selected for architectural clarity and documentation value.

---

### Option B: Remove Placeholder Now
**Pros:**
- Cleaner directory structure
- No "empty" directories in repository
- Forces explicit creation when implementation begins

**Cons:**
- Loses architectural documentation hub
- Requires recreation when implementation starts
- No visible signal of planned backend architecture
- May encourage ad-hoc backend solutions

**Decision:** Rejected due to loss of documentation value and architectural clarity.

## Consequences

### Positive
- ✅ Clear architectural roadmap visible in repository structure
- ✅ Backend requirements documented in README.md
- ✅ Prevents duplicate/ad-hoc backend implementations
- ✅ Supports phased development (Python MCP → Backend API)
- ✅ Minimal repository overhead (1 directory, 2 files)

### Neutral
- ⚪ Directory appears in file tree (expected for structural placeholder)
- ⚪ Requires this ADR to explain decision (good documentation practice)

### Negative
- ❌ None identified (placeholder is standard practice with documented intent)

## Success Criteria

1. ✅ `TaskMan-v2/backend-api/` directory retained with README.md
2. ✅ `.gitkeep` file added for directory persistence
3. ✅ README.md documents complete architecture and requirements
4. ✅ ADR created explaining decision rationale
5. ✅ Root documentation updated referencing backend-api status
6. ✅ Python MCP parity roadmap links to backend-api plan

## Related Work

- **Phase 1**: TaskMan-v2 import from submodule (complete, commits c7cace97 + 5dca3962)
- **Phase 2**: Structural placeholders and roadmap documentation (this ADR)
- **Next Phase**: Python MCP parity implementation (see `TaskMan-v2/mcp-server-py/README.md`)
- **Future Phase**: FastAPI backend implementation (see `TaskMan-v2/backend-api/README.md`)

## References

- TaskMan-v2 Integration Plan: `.github/prompts/plan-taskManV2IntegrationPush.prompt.md`
- Integration Checklist: `.github/prompts/TaskMan-v2-Integration-Push-Checklist.md`
- Backend Architecture: `TaskMan-v2/backend-api/README.md`
- Python MCP Roadmap: `TaskMan-v2/mcp-server-py/README.md`
- Commit History:
  - c7cace97: TaskMan-v2 initial import
  - 5dca3962: .gitmodules cleanup
  - [This commit]: ADR creation and .gitkeep addition

## Approval

**Accepted**: 2025-01-23
**Implementation**: Immediate (Phase 2 of TaskMan-v2 integration)
**Review Date**: Upon Python MCP parity completion or backend implementation start
