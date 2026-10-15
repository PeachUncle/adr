# ADR-0007: Unified CLI Tool Architecture

**Status:** Accepted
**Date:** 2025-12-16
**Updated:** 2025-12-16
**Supersedes:** None
**Superseded By:** N/A

---

## Context

The project CLI (`scripts/project_cli/`) and inventory system (`scripts/inventory/`) are being unified and separated from work-prod into their own repository. This decision enables:
- **Backend API-only:** work-prod becomes a pure Flask API
- **Unified CLI:** Single tool for all project/inventory operations
- **Independent evolution:** CLI can develop without affecting API
- **Different cadence:** Inventory refresh (periodic) vs API development (continuous)
- **Technical debt isolation:** Address CLI-specific issues in isolation
- **Potential reusability:** CLI can be shared or open-sourced

**Key Question:** How should the CLI tools be restructured during separation?

**Research Conducted:**
- [Exploration: Inventory Repository Separation](../exploration/inventory-repository-separation/README.md)
- [Research: CLI Tool Architecture](../research/inventory-repository-separation/research-cli-tool-architecture.md)
- [Research: CLI Framework Selection](../research/inventory-repository-separation/research-cli-framework.md)
- [Research: Configuration Management](../research/inventory-repository-separation/research-configuration.md)
- [Research: Technical Debt Prioritization](../research/inventory-repository-separation/research-tech-debt.md)

**Current State (work-prod):**
- `scripts/project_cli/` - `proj` command (talks to API)
- `scripts/inventory/` - 6 separate scripts (Python + Shell)
- Hardcoded paths (non-portable)
- No unified interface for inventory
- No shared configuration management
- 7 known technical debt items

**Constraints:**
- Limited time (target: ~10 hours)
- Should be usable quickly
- Must integrate with work-prod API
- Preserve existing `proj` command muscle memory

---

## Decision

Build a **unified CLI tool** named `proj` as a proper Python package in a separate repository. This CLI unifies:
- **Project management:** Existing `proj` commands (list, get, create, etc.)
- **Inventory management:** New `proj inv` subcommands (scan, analyze, export)

The work-prod repository becomes **API-only** after migration.

### Key Decisions

| Decision Point | Choice | Rationale |
|----------------|--------|-----------|
| **Approach** | Unified CLI tool | Single entry point, better UX |
| **Command Name** | `proj` | Preserves existing muscle memory |
| **Framework** | Typer | Modern, type hints, minimal boilerplate |
| **Configuration** | YAML + Pydantic + XDG | Standard locations, type-safe |
| **Technical Debt** | Fix P0 + P1 during separation | Necessary for portability |
| **Repository** | Separate from work-prod | API-only backend, independent CLI |

### Repository & Package Structure

```
proj-cli/                    # Repository name
├── pyproject.toml           # Modern Python packaging (pip install .)
├── requirements.txt
├── README.md
├── src/
│   └── proj/                # Package name
│       ├── __init__.py
│       ├── __main__.py      # Entry point
│       ├── cli.py           # Typer app (main)
│       ├── config.py        # Pydantic config
│       ├── api_client.py    # work-prod API client
│       ├── commands/        # Command groups
│       │   ├── __init__.py
│       │   ├── projects.py  # list, get, create, update, delete, etc.
│       │   └── inventory.py # scan, analyze, dedupe, export
│       ├── scanners/        # GitHub + local scanning
│       └── utils/           # Shared helpers
└── tests/
```

### CLI Command Structure

```bash
# Project Management (existing functionality, migrated)
proj list                    # List all projects
proj get <id>                # Get project details
proj create "Name"           # Create project
proj update <id> --status X  # Update project
proj delete <id>             # Delete project
proj search "query"          # Search projects
proj import file.json        # Import from JSON

# Inventory Management (new subcommand group)
proj inv scan github         # Scan GitHub repos
proj inv scan local          # Scan local directories
proj inv analyze             # Analyze tech stack + classify
proj inv dedupe              # Deduplicate results
proj inv export json         # Export to JSON file
proj inv export api          # Push to work-prod API
proj inv status              # Show inventory state
```

### Configuration

| Setting | Value |
|---------|-------|
| Config File | `~/.config/proj/config.yaml` |
| Data Directory | `~/.local/share/proj/` |
| Environment Prefix | `PROJ_` |
| Validation | Pydantic |
| API URL Config | `api_url: http://localhost:5000` |

---

## Consequences

### Positive

- **Unified Entry Point:** Single `proj` command for all operations
- **Preserved Muscle Memory:** Existing `proj` users continue using same command
- **Clean Separation:** work-prod becomes API-only (simpler, focused)
- **Professional Tool:** Typer + Rich provides beautiful output, help text, progress bars
- **Portable:** XDG config removes hardcoded paths
- **Foundation:** CLI architecture enables future enhancements
- **Reduces Debt:** CLI tool addresses #5 (orchestrator) and #4 (output consistency)
- **Single Install:** `pip install proj-cli` gives all functionality

### Negative

- **More Initial Work:** ~8-12 hours vs ~4-6 hours for simple separation
- **Migration Effort:** Must move `proj` code from work-prod to new repo
- **New Dependencies:** Adds Typer, Pydantic, PyYAML (but removes ad-hoc solutions)
- **Two Repos:** work-prod (API) + proj-cli (CLI) instead of monorepo

### Deferred

- Shell script conversion to Python (works as-is via subprocess)
- Incremental scanning mode
- Output format standardization (iterate after CLI works)
- Plugin architecture (if needed later)

---

## Alternatives Considered

### Alternative 1: Simple Script Separation

**Description:** Move scripts to new repo as-is, add requirements.txt

**Pros:**
- Fastest implementation (4-6 hours)
- No new dependencies
- Minimal changes

**Cons:**
- Poor UX (6 separate scripts)
- No shared configuration
- Inconsistent interfaces
- Harder to extend

**Why Not Chosen:** The UX improvement from CLI justifies the moderate additional effort.

### Alternative 2: Separate `proj` and `pinv` Commands

**Description:** Keep `proj` in work-prod, create separate `pinv` command for inventory

**Pros:**
- Less migration effort
- Clear separation of concerns
- work-prod stays as-is

**Cons:**
- Two commands to remember
- Duplicate configuration logic
- `proj` stays in work-prod (not API-only)
- No unified experience

**Why Not Chosen:** Unifying under `proj` provides better UX and cleaner architecture (API-only work-prod).

### Alternative 3: Full-Featured CLI (Option C)

**Description:** Build complete CLI with all bells and whistles from day one

**Pros:**
- Professional tool
- All features immediately

**Cons:**
- Higher effort (16-20 hours)
- Scope creep risk
- May over-engineer

**Why Not Chosen:** Option B provides foundation; can evolve to C over time.

### Alternative 4: Keep Everything in work-prod Repository

**Description:** Don't separate; keep CLI and inventory scripts in work-prod

**Pros:**
- No separation effort
- Single repo

**Cons:**
- Different cadences conflict
- Clutters main repo
- Technical debt stays
- work-prod not API-only

**Why Not Chosen:** Decided against in prior reflection; separation enables better organization.

---

## Implementation Notes

### Phase 1: Repository Setup (Day 1, ~2-3 hours)
- Create `proj-cli` repository via `dev-infra/new-project.sh`
- Create package structure with `src/proj/`
- Add pyproject.toml with `proj` entry point
- Create basic Pydantic config with XDG paths
- Add requirements.txt

### Phase 2: Migrate Project Commands (Day 2, ~3-4 hours)
- Move `scripts/project_cli/` code to `src/proj/commands/projects.py`
- Convert from argparse to Typer
- Migrate API client code
- Test all existing `proj` commands work

### Phase 3: Add Inventory Commands (Day 3, ~3-4 hours)
- Create `src/proj/commands/inventory.py`
- Wrap inventory scripts as `proj inv` subcommands
- Add basic error handling
- Test inventory workflows

### Phase 4: Polish & Cleanup (Day 4, ~2-3 hours)
- Testing and documentation
- First-run config creation
- Progress bars and colors
- Remove `scripts/project_cli/` from work-prod
- Update work-prod README to reference new CLI

### Dependencies

```
typer[all]>=0.9.0
pyyaml>=6.0
pydantic-settings>=2.0
requests>=2.28.0           # API client
rich>=13.0.0               # Already included with typer[all]
```

### Requirements Impact

This decision implements or enables:
- FR-1: Single entry point CLI command (`proj`) ✅
- FR-2-5: Scan/Analyze/Process/Export as `proj inv` subcommands ✅
- FR-6-8: Configuration support ✅
- NFR-1: Typer framework ✅
- NFR-2: Rich terminal output ✅
- NFR-3: Pydantic validation ✅
- NFR-4: XDG compliance ✅
- **NEW:** Migration of existing `proj` commands ✅
- **NEW:** work-prod becomes API-only ✅

---

## References

- [Exploration: Inventory Repository Separation](../exploration/inventory-repository-separation/README.md)
- [Research Hub](../research/inventory-repository-separation/README.md)
- [Research Summary](../research/inventory-repository-separation/research-summary.md)
- [Requirements Document](../research/inventory-repository-separation/requirements.md)
- [Existing Transition Plan](../planning/infrastructure/inventory-repository-separation/transition-plan.md)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

### Source Code to Migrate

| Source (work-prod) | Destination (proj-cli) |
|--------------------|------------------------|
| `scripts/project_cli/` | `src/proj/commands/projects.py` |
| `scripts/project_cli/api_client.py` | `src/proj/api_client.py` |
| `scripts/inventory/*.py` | `src/proj/commands/inventory.py` |
| `scripts/inventory/*.sh` | `src/proj/scanners/` (subprocess) |

### Post-Migration Cleanup (work-prod)

After successful migration and testing:
1. Remove `scripts/project_cli/` directory
2. Update `README.md` to reference `proj-cli` package
3. Update any documentation referencing `proj` command
4. work-prod becomes purely `backend/` + `docs/` + `frontend/` (when built)

---

**Last Updated:** 2025-12-16

