# Monorepo Architecture Decision - Summary

**Date:** 2025-12-21
**Session:** Architecture clarification after Phase P1 completion

---

## What Happened

### User's Question
> "check the dev-tools project for existing doc project/repo. Why creating a new repo? why not storing here in the project"

### Context
During brainstorming, an initial proposal suggested creating separate repositories:
- `nexus/` (documentation)
- `nexus-vault-template/` (template vault - NEW)
- `nexus-mcp/` (MCP server - NEW)

The user questioned this approach, asking why we would create new repositories instead of keeping everything in the current project.

---

## Investigation Results

### Examined dev-tools Patterns

**zsh-configuration/** (Primary reference):
```
zsh-configuration/
├── docs/           # Documentation
├── templates/      # Template content (IN REPO)
├── standards/      # Universal standards (IN REPO)
├── config/         # Configuration
└── cli/            # CLI tools
```

**Key Finding:** Templates and standards are subdirectories, NOT separate repositories.

**Other Examples:**
- `mcp-servers/` - Multiple MCP servers in one repo (monorepo)
- `spacemacs-rstats/` - Config + docs + examples together
- Pattern: Keep related components together

---

## Decision: Monorepo ✅

### Chosen Structure

```
nexus/
├── docs/                # Documentation (moved here)
│   ├── architecture.md
│   ├── quickstart.md
│   └── claude-system-prompt.md
│
├── standards/           # Universal standards ✅ Complete
│   ├── vault/
│   ├── documentation/
│   └── workflow/
│
├── vault-template/      # Template vault 📋 P2
│   ├── .obsidian/
│   ├── 00-INBOX/
│   ├── 10-PROJECTS/
│   └── ...
│
├── scripts/             # Setup scripts 📋 P3
│   ├── setup-vault.sh
│   └── validate-vault.sh
│
├── mcp-server/          # MCP server 📋 P4
│   ├── src/
│   └── package.json
│
└── examples/            # Example content 📋 P3
    └── ...
```

### Rationale

**Why Monorepo:**
1. ✅ **Consistency** - Follows zsh-configuration pattern
2. ✅ **Atomic updates** - Change docs + templates in one commit
3. ✅ **Single source of truth** - No version sync issues
4. ✅ **ADHD-friendly** - One place for everything
5. ✅ **Simpler maintenance** - One repo to clone/update
6. ✅ **Better discoverability** - Users get everything at once

**Why NOT Separate Repos:**
- ❌ Would break dev-tools pattern
- ❌ Creates version sync problems
- ❌ More complex for users (which repo?)
- ❌ More complex for maintainers (coordinate updates)
- ❌ Against ADHD-friendly principles

---

## Actions Taken

### Files Created
1. ✅ **ARCHITECTURE-DECISION-MONOREPO.md**
   - Complete analysis of dev-tools patterns
   - Detailed comparison: monorepo vs multi-repo
   - Benefits for users, maintainers, ADHD workflows
   - Migration path (if ever needed)

### Files Updated
1. ✅ **PROPOSAL-TEMPLATE-VAULT.md**
   - Changed `nexus-vault/` → `nexus/vault-template/`
   - Added architecture decision reference
   - Updated all paths and examples
   - Added monorepo benefits section

2. ✅ **PROPOSAL-MCP-INTEGRATION.md**
   - Added location: `nexus/mcp-server/`
   - Added architecture note at top
   - References ARCHITECTURE-DECISION-MONOREPO.md

3. ✅ **README.md**
   - Added link to ARCHITECTURE-DECISION-MONOREPO.md
   - Listed under "For Contributors" section

4. ✅ **.STATUS**
   - Added ARCHITECTURE-DECISION-MONOREPO.md to completions
   - Updated next actions to reflect monorepo structure
   - Changed recommendations to match new architecture

---

## Impact on Roadmap

### No Change to Phases
- Phase P0: Documentation ✅ Complete
- Phase P1: Standards ✅ Complete
- Phase P2: Template Vault 📋 Next (now as `vault-template/`)
- Phase P3: Example Content 📋 Future
- Phase P4: Distribution 📋 Future

### Changes to Implementation
- ✅ Template vault: `nexus/vault-template/` (not separate repo)
- ✅ MCP server: `nexus/mcp-server/` (not separate repo)
- ✅ Scripts: `nexus/scripts/` (not separate repo)
- ✅ Examples: `nexus/examples/` (not separate repo)

---

## Benefits Realized

### For User (DT)
- ✅ **Consistency** - All dev-tools projects follow same pattern
- ✅ **Familiar** - Same structure as zsh-configuration
- ✅ **Simple** - One repo to track in PROJECT-HUB.md
- ✅ **ADHD-friendly** - No context switching between repos

### For Contributors
- ✅ **One clone** - Get everything at once
- ✅ **One PR** - Change related files together
- ✅ **One issue tracker** - Clear where to file issues
- ✅ **Clear structure** - Subdirectories show relationships

### For Maintenance
- ✅ **Atomic commits** - Change docs + templates + standards together
- ✅ **No sync issues** - Everything versioned together
- ✅ **One CI/CD** - Single pipeline for all components
- ✅ **One release** - Tag everything at once

---

## Validation

### Checked Against dev-tools
- ✅ zsh-configuration: Monorepo with templates/, standards/
- ✅ mcp-servers: Monorepo with multiple servers
- ✅ spacemacs-rstats: Monorepo with config + docs

### Checked Against ADHD Principles
- ✅ Single mental model: "Go to nexus repo"
- ✅ Visual hierarchy: Subdirectories show purpose
- ✅ No context switching: Everything in one place
- ✅ Clear structure: Follows PARA-like organization

### Checked Against Maintenance Goals
- ✅ Easy to update: One `git pull`
- ✅ Easy to contribute: One repo to fork
- ✅ Easy to release: One version, one tag
- ✅ Easy to track: One .STATUS file

---

## Next Steps

### Recommended: Begin P2 (Template Vault Creation)

**Task:** Create `vault-template/` subdirectory with complete Obsidian vault

**Implementation:**
1. Create folder structure (00-INBOX through _SYSTEM)
2. Add .obsidian/ configuration
3. Create template files (project.md, paper-note.md, daily.md, etc.)
4. Add example content
5. Create working dashboards

**Time:** 6-8 hours
**Outcome:** Users can copy `vault-template/` and start using immediately

**Reference:** [PROPOSAL-TEMPLATE-VAULT.md](PROPOSAL-TEMPLATE-VAULT.md)

---

## Alternative: Reorganize Docs First

**Task:** Move existing docs into `docs/` subdirectory

**Quick win:** 20 minutes to clean up root directory

**Implementation:**
```bash
mkdir -p docs/
mv architecture.md docs/
mv quickstart.md docs/
mv claude-system-prompt.md docs/
mv claude-obsidian-system-prompt.md docs/
# Update cross-references
```

**Outcome:** Cleaner root, follows monorepo structure

---

## Conclusion

The user's instinct was **100% correct** - keeping everything in one repository:

1. ✅ **Follows existing patterns** (zsh-configuration, mcp-servers)
2. ✅ **Simpler for everyone** (users, contributors, maintainers)
3. ✅ **ADHD-friendly** (one mental model, no context switching)
4. ✅ **Easier to maintain** (atomic updates, no sync issues)

The architecture decision is now **documented, validated, and implemented** in the proposals.

---

**Status:** ✅ Architecture decision finalized
**Documented in:** ARCHITECTURE-DECISION-MONOREPO.md
**Impact:** Updated 2 proposals, README, .STATUS
**Ready for:** Phase P2 (Template Vault Creation)

---

**Created:** 2025-12-21
**Session:** Post-brainstorm architecture clarification
**Maintainer:** DT
