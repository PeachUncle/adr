# 0002 - Automatic Dotfiles Installation

**Status:** Accepted

**Date:** 2025-11-26

**Deciders:** Marcelo Almeida (repository owner)

## Context

DevMagic users need personal configuration (shell aliases, editor settings, CLI tools) that differs from the base container infrastructure. Initially, we relied on VS Code's built-in dotfiles support via user settings:

```json
{
  "dotfiles.repository": "username/dotfiles",
  "dotfiles.targetPath": "~/prj/dotfiles"
}
```

**Problem:** VS Code explicitly states this feature doesn't work for remote containers (devcontainers, Codespaces, remote SSH/tunnel hosts). Testing confirmed dotfiles were never cloned in these scenarios, leaving containers without personal configuration.

This violates DevMagic's portability goal - containers should work consistently across all usage modes (local, remote, Codespaces).

## Decision

Implement automatic dotfiles cloning in `devcontainer-setup.sh` using environment variables.

**Key design choices:**

1. **Clone on first run** - Directory presence (`~/prj/dotfiles`) is the marker
2. **Host environment variables** - Users set `DEVMAGIC_DOTFILES_REPO` in their shell config, no devcontainer.json edits needed
3. **`containerEnv` not `remoteEnv`** - Variables must be available during `postCreateCommand` (before VS Code connects)
4. **Shallow clone** - `--depth=1` for speed
5. **Graceful failure** - Log warning and continue if clone fails
6. **Default values in bash only** - Due to a limitation in the devcontainer spec (see below)

### Important: Default Value Limitation

The devcontainer spec's `${localEnv:VAR:default}` syntax uses colons as delimiters, which **breaks when default values contain colons** (like URLs). There is no escape mechanism.

```jsonc
// ❌ BROKEN - evaluates to "https" not the full URL
"DEVMAGIC_DOTFILES_REPO": "${localEnv:DEVMAGIC_DOTFILES_REPO:https://github.com/user/dotfiles.git}"
```

This is a [known spec limitation](https://github.com/devcontainers/spec/issues/565) with no fix as of November 2025.

**Workaround:** Pass variables without defaults in `containerEnv`, handle defaults in bash:

```jsonc
// devcontainer.json - no default value
"DEVMAGIC_DOTFILES_REPO": "${localEnv:DEVMAGIC_DOTFILES_REPO}"
```

```bash
# devcontainer-setup.sh - default handled here
local dotfiles_repo="${DEVMAGIC_DOTFILES_REPO:-https://github.com/user/dotfiles.git}"
```

See [ARCHITECTURE.md](../ARCHITECTURE.md#the-install-script-location) for configuration details and code examples.

## Alternatives Considered

### Option 1: Continue relying on VS Code settings

**Rejected** because:
- Explicitly doesn't work for remote containers
- Non-deterministic behavior
- Breaks portability promise
- Editor-dependent

### Option 2: Complex marker file system

**Rejected** because:
- Over-engineered for the problem
- Would need commit hash tracking, integrity checks, marker files
- Directory presence is sufficient marker
- Violates "simplicity over cleverness"

### Option 3: Dockerfile-baked dotfiles

**Rejected** because:
- Breaks separation of concerns (DevMagic = infrastructure, dotfiles = personal)
- Makes personalization image-specific
- Can't share DevMagic images publicly

### Option 4: postStartCommand integrity checks

**Rejected** because:
- Adds startup overhead
- Unnecessary if install script is idempotent (which it must be anyway)
- Directory presence check is sufficient

## Consequences

### Positive

- **Works everywhere** - Local, remote SSH, tunnels, Codespaces
- **Simple implementation** - ~20 lines of bash
- **User control** - Environment variables for repo/branch
- **Graceful fallback** - Logs warning if clone fails, container still usable
- **Fast** - Shallow clone (`--depth=1`)
- **Idempotent** - Only clones if directory missing
- **No coupling** - Users can disable via `DEVMAGIC_DOTFILES_REPO=""`

### Negative

- **Network dependency** - Requires internet on first container creation
- **User responsibility** - Install script must be idempotent
- **Default repo hardcoded** - Defaults to maintainer's repo (acceptable for personal project)

### Neutral

- Directory presence is the "marker" - no separate marker files needed
- No automatic updates - users rebuild container for fresh clone
- Documentation updated across README, ARCHITECTURE, website

## Notes

- Planning discussion: `docs/archives/2025-11-fix-dotfiles-install-planning.md`
- User dotfiles must have `shell/install.sh` at standard location
- Install script should handle: Homebrew, fzf, zsh plugins, VS Code symlinks
- Related: [0001 - Use Dev Container Features](0001-use-dev-container-features.md)

**Security:**
- Shallow clone minimizes exposure
- Git provides commit verification
- Runs as non-root user (via common-utils feature)
- User controls repo URL

**Testing:**
- Fresh container (no dotfiles) → should clone and install
- Rebuild with existing dotfiles → should skip clone, run install
- Network unavailable → should log warning and continue
- Custom repo → set `DEVMAGIC_DOTFILES_REPO` environment variable
