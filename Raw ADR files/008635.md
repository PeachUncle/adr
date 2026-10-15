# 0001 - Use Dev Container Features

**Status:** Accepted

**Date:** 2025-11-21

**Deciders:** Marcelo Almeida (repository owner)

## Context

DevMagic initially used custom bash scripts to install development tools (Node.js, Git, Docker, Zsh, etc.) in containers. This approach required:

- Maintaining ~200+ lines of bash scripts
- Handling different package managers across base images
- Debugging installation issues across distributions
- Manual version pinning
- Testing across multiple OS variants

The Dev Container Specification provides [official Features](https://containers.dev/features) - pre-built, tested, version-pinned installation modules maintained by Microsoft and the community.

## Decision

Replace custom package installation scripts with official Dev Container Features:

- `common-utils:2` - Zsh, Oh My Zsh, tmux, utilities
- `node:1` - Node.js LTS with pnpm/yarn
- `git:1` - Latest Git
- `git-lfs:1` - Git Large File Support
- `github-cli:1` - GitHub CLI
- `docker-in-docker:2` - Docker with Compose v2
- `homebrew:1` - Homebrew package manager

Keep minimal custom script (`devcontainer-setup.sh`) only for:
- SSH key setup (permission handling)
- AI CLI tools installation
- Dotfiles integration

## Alternatives Considered

### Option 1: Continue with custom bash scripts

**Rejected** because:
- High maintenance burden
- Reinventing the wheel
- No community testing
- Version management complexity

### Option 2: Create custom Dev Container Features

**Rejected** because:
- Official features already exist for our needs
- More overhead to maintain
- Would duplicate existing work

### Option 3: Use Docker base images with pre-installed tools

**Rejected** because:
- Less flexible for users
- Larger image sizes
- Harder to customize per-project

## Consequences

### Positive

- **Less maintenance** - Microsoft/community maintains the features
- **Better reliability** - Features are tested across platforms
- **Version pinning built-in** - Features use semantic versioning (`:2`, `:1`)
- **Easier customization** - Users can add/remove features via JSON config
- **Better documentation** - Each feature has official docs
- **Faster setup** - Features are optimized and cached

### Negative

- **Less control** - Can't modify feature internals easily
- **Dependency on external sources** - Relies on `ghcr.io/devcontainers/features`
- **Learning curve** - Team needs to understand feature system vs plain bash

### Neutral

- Custom script reduced from 200+ lines to ~100 lines
- Configuration moved from bash variables to `devcontainer.json` properties
- Still need custom script for SSH keys and dotfiles (by design)

## Notes

- Full migration documented in `docs/blog-devmagic-refactoring-learnings.md`
- Previous custom scripts archived in git history for reference
- This decision aligns with "simplicity over cleverness" principle
- Related: [0002 - Automatic Dotfiles Installation](0002-automatic-dotfiles-installation.md)

**References:**
- [Dev Container Features Specification](https://containers.dev/features)
- [Official Features Repository](https://github.com/devcontainers/features)
- [Feature Template Repository](https://github.com/devcontainers/feature-starter)
