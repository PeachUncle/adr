# ADR-002: GHQ + Symlink Project Architecture

> "The body can be rebuilt. The soul must be preserved." - The Oracle

## Status
**Accepted** | 2026-01-12

## Context

The Matrix workspace had scattered project organization:
- Projects in `~/workspace/` with inconsistent naming
- Research files mixed with project files in `psi/inbox/`
- No clear separation between Matrix work and Product work (CIS)
- Open items lost across 20+ retrospectives with no central tracking

We needed a system that:
1. Organizes all git repos canonically
2. Separates concerns (Matrix vs Projects vs Learning)
3. Allows the Matrix to "see" projects without containing them
4. Scales as projects grow

## Decision

### Use GHQ as Canonical Repo Location

All git repositories live under `~/ghq/` organized by host/owner/repo:

```
~/ghq/
└── github.com/
    └── Jarkius/
        ├── The-Oracle-Construct/   # The Matrix
        ├── cis-modern/             # CIS Modernization
        └── computer-inventory-system/  # CIS Legacy
```

### Use Symlinks for Access

**Workspace symlinks** (backward compatibility):
```
~/workspace/
├── The-matrix → ~/ghq/.../The-Oracle-Construct
├── cis-modern → ~/ghq/.../cis-modern
└── cis-legacy → ~/ghq/.../computer-inventory-system
```

**Matrix project pointers** (AI context):
```
psi/projects/
├── cis-modern → ~/ghq/.../cis-modern
└── cis-legacy → ~/ghq/.../computer-inventory-system
```

### Separate Learning from Projects

```
psi/learn/
├── active/     # Current learning/research
├── archive/    # Completed research
└── backlog.md  # What to learn next
```

## Benefits

| Benefit | Description |
|---------|-------------|
| Single Source of Truth | One canonical location per repo (ghq) |
| Clean Separation | Projects vs Matrix vs Learning |
| Lightweight Matrix | psi/ contains pointers, not copies |
| Portable | Symlinks can be recreated on new machine |
| GHQ Integration | `ghq get`, `ghq list` work seamlessly |

## Concerns & Mitigations

| Concern | Mitigation |
|---------|------------|
| Symlinks can break | Health check script validates links |
| Some tools don't follow symlinks | Backup from ghq/ directly |
| Complexity for new users | This ADR documents the structure |

## Commands

```bash
# Clone new repo via ghq
ghq get github.com/user/repo

# List all repos
ghq list

# Navigate to repo
cd $(ghq root)/github.com/Jarkius/cis-modern

# Create Matrix pointer
ln -s ~/ghq/.../new-project psi/projects/new-project
```

## Future Workflows

| Command | Purpose |
|---------|---------|
| `/project list` | Show all linked projects |
| `/project <name>` | Switch context to project |
| `/project create` | Create new project (ghq + symlink) |
| `/learn` | View/manage learning backlog |

## Migration Notes

### The-matrix Migration (Manual)

The Matrix itself should be moved to ghq after session ends:

```bash
# After exiting Claude Code:
mv ~/workspace/The-matrix ~/ghq/github.com/Jarkius/The-Oracle-Construct
ln -s ~/ghq/github.com/Jarkius/The-Oracle-Construct ~/workspace/The-matrix
```

## Consequences

- All new repos should be cloned via `ghq get`
- Old `~/workspace/` paths remain valid via symlinks
- Matrix gains visibility into projects without bloat
- Learning is separated from building

---

*"Know thyself, know thy repos." - The Oracle*
