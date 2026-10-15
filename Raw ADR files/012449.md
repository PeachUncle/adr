## Context

Two AI coding assistants (Claude Code and OpenCode) need to share coding rules and specialized instructions. Neither tool supports environment variable interpolation in markdown files, preventing simple ENV-based sharing.

Current state uses direct symlinks for flexibility, but this prevents content sharing since tools have different frontmatter formats.

## Goals

- Share coding rules and instructions across both tools
- Maintain flexibility for experimentation (edit files directly, then "nixify" to share)
- Keep configuration organized in separate home-manager submodule

## Decisions

### Directory Structure

`experimental.md` here is an example. Actual files will vary in names.

```
hm/
  development-environment.nix       # Imports ai-tooling submodule
  development-environment/
    ai-tooling.nix                  # AI tooling configuration submodule
    ai-tooling/
      commit-instructions.md        # Commit instruction content for generation
      review-instructions.md        # Review instruction content for generation

dotfiles/
  ai-shared/                        # Content shared "as is" between tools
    coding-rules.md                 # Shared coding rules (out-of-store, editable)
  claude/
    commands/
      experimental.md               # Example: experimental command (out-of-store, editable)
    settings.json                   # Mutable config (out-of-store, directly editable)
  opencode/
    agent/
      experimental.md               # Example: experimental agent (out-of-store, editable)
    command/
      experimental.md               # Example: experimental command (out-of-store, editable)
    opencode.jsonc                  # Mutable config (out-of-store, directly editable)

# Home directory after build:
~/.claude/
  CLAUDE.md                         # Direct symlink to dotfiles/ai-shared/coding-rules.md
  settings.json                     # Direct symlink to dotfiles/claude/settings.json
  commands/
    commit.md                       # Nix-generated, symlinked from store
    review.md                       # Nix-generated, symlinked from store
    experimental.md                 # Out-of-store symlink to dotfiles/claude/commands/experimental.md

~/.config/opencode/
  AGENTS.md                         # Direct symlink to dotfiles/ai-shared/coding-rules.md
  opencode.jsonc                    # Direct symlink to dotfiles/opencode/opencode.jsonc
  command/
    commit.md                       # Nix-generated, symlinked from store
    experimental.md                 # Out-of-store symlink to dotfiles/opencode/command/experimental.md
  agent/
    review-staged.md                # Nix-generated, symlinked from store
    experimental.md                 # Out-of-store symlink to dotfiles/opencode/agent/experimental.md
```

**Three-tier system:**
- Content shared "as is": `dotfiles/ai-shared/` → direct symlinks (editable)
- Content for generation: `hm/development-environment/ai-tooling/` → Nix-generated with tool-specific frontmatter (immutable)
- Experimental files: tool-specific directories → direct symlinks (editable, rebuild to discover new files)

### Mixed Directories

Helper function `mkDotfilesDirectoryEntriesSymlinks` creates individual symlinks for each file in a directory, allowing generated files (Nix store) and experimental files (out-of-store symlinks to dotfiles) to coexist in the same home directory location (e.g., `~/.claude/commands/` contains both `commit.md` from Nix and `experimental.md` from dotfiles).

**Why not symlink entire directory?** Would conflict with generated files.

### Desired Workflow

1. **Experiment**: Create in tool-specific directory (e.g., `dotfiles/claude/commands/experimental.md`), rebuild once, then edit freely
2. **Share**: If needed for both tools:
   - Identical content → move to `dotfiles/ai-shared/`
   - Needs tool-specific frontmatter → extract to `hm/development-environment/ai-tooling/`, generate in `ai-tooling.nix`

## Trade-offs

- Rebuild required for shared instruction changes (files in `dotfiles` don't need rebuild after initial discovery)
