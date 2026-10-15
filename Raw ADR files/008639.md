# DevMagic Refactor Plan — DevContainer Features First

Date: 2025-11-20
Status: ✅ Complete (2025-11-21)

---

## Recent Architecture Decisions (2025-11-25)

Key decisions made during architecture review. For full details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

1. **Separation of concerns**: DevMagic = container infrastructure, Dotfiles = personal preferences
2. **`install.sh` stays in dotfiles** (not DevMagic) - no coupling between repos
3. **Homebrew over Conda** for CLI tools - better availability, no licensing issues
4. **Custom forks for security** - `marcelocra/fzf`, `marcelocra/zsh-*`
5. **VS Code configs from dotfiles** - symlinked by `install.sh`
6. **No shared `utils.sh`** - each script self-contained (simplicity > DRY)

---

## Goals

- Reduce maintenance by replacing bespoke bash setup with official Dev Container Features/Templates.
- Keep security posture (pin versions, allow optional forks for specific tools).
- Move all devcontainer-related files under `.devcontainer/`.

## Requirements

- ✅ Use official Features from `ghcr.io/devcontainers/features/*` when possible
- ✅ Pin versions to prevent unexpected updates
- ✅ Maintain read-only credential mounts for security
- ✅ Support idempotent setup (safe to rebuild)
- ✅ Keep minimal container-setup.sh for custom needs (SSH keys)

## Constraints

- ✅ Must work with existing mounts (SSH, GitHub, Claude, Gemini, shell histories)
- ✅ Must preserve MCRA_HISTORY_DIR for persistent shell history
- ✅ Must handle SSH key permissions (copied from read-only mount)
- ✅ User dotfiles handle history/editor configuration

## Step-by-step Plan

### 1. ✅ Analyze Current Setup

- ✅ Reviewed `setup/devcontainer-setup.sh` for what needs Features
- ✅ Identified: common-utils, node, git, git-lfs, github-cli, docker-in-docker, homebrew
- ✅ Determined SSH keys still need custom script (permissions)

### 2. ✅ Add Official Features

- ✅ Added `common-utils:2` (zsh, oh-my-zsh, tmux, utilities)
- ✅ Added `node:1` with pnpm support (LTS version)
- ✅ Added `git:1` for latest Git
- ✅ Added `git-lfs:1` for Git Large File Support
- ✅ Added `github-cli:1` for GitHub CLI
- ✅ Added `docker-in-docker:2` with Compose v2
- ✅ Added `homebrew:1` for additional package management

### 3. ✅ Create Minimal Container Setup Script

- ✅ Created `setup/devcontainer-setup.sh` with only SSH key handling
- ✅ Added AI CLI tools installation (aider, GitHub Copilot CLI, Gemini CLI, Claude CLI)
- ✅ Used main() function pattern for better structure
- ✅ Removed package installation (now handled by Features)
- ✅ Noted that history/editor config is in dotfiles

### 4. ✅ Update devcontainer.json

- ✅ Added `features` property with all official Features
- ✅ Kept essential environment variables (MCRA_HISTORY_DIR, WORKSPACE_FOLDER, locale, OLLAMA_HOST)
- ✅ Updated `postCreateCommand` to run setup script via curl
- ✅ Added VS Code extensions for AI tools (Cline, Continue.dev)
- ✅ Verified all credential mounts still work

### 5. ✅ Update Website Routes

- ✅ Updated `/setup` endpoint to serve `devcontainer-setup.sh`
- ✅ Kept `/install` endpoint serving `devmagic.sh`
- ✅ Verified script downloads work correctly

### 6. ✅ Update Installer Script

- ✅ Updated `setup/devmagic.sh` to download from correct paths
- ✅ Downloads `.devcontainer/devcontainer.json`
- ✅ Downloads `.devcontainer/docker-compose.yml`

### 7. ✅ File Organization

- ✅ Consolidated setup in `.devcontainer/` directory
- ✅ Removed duplicate `container-setup.sh`
- ✅ Kept `devcontainer-setup.sh` as the single source of truth

### 8. ✅ Documentation Updates

- ✅ Updated `README.md` with Features information
- ✅ Updated `www/README.md` with correct endpoint info
- ✅ Documented AI CLI tools included

### 9. ~~Option C: Fork-based customization~~ (Cancelled)

- Decided against fork-based approach - using Features-only is simpler

## What Was Implemented

### Dev Container Features

All package installation now handled by official Features:

- `common-utils:2` - Zsh, Oh My Zsh, tmux, core utilities
- `node:1` - Node.js LTS with pnpm (10.18.3+) and yarn support
- `git:1` - Latest Git from official sources
- `git-lfs:1` - Git Large File Support
- `github-cli:1` - GitHub CLI (`gh`) with authentication
- `docker-in-docker:2` - Docker daemon with Compose v2

### Container Setup Script

Minimal `setup/devcontainer-setup.sh`:

- SSH key copying from read-only mount (`~/.ssh-from-host` → `~/.ssh`)
- Proper permissions (700 for directory, 600 for files)
- AI CLI tools installation:
    - `aider` via pipx (AI pair programming)
    - GitHub Copilot CLI via npm
    - Gemini CLI via pnpm
    - Claude CLI via pnpm (if not already installed)
- Structured with main() function pattern
- Color-coded logging (info, success, warning, error)

### VS Code Extensions

Added AI development extensions:

- `saoudrizwan.claude-dev` - Cline (AI coding assistant)
- `continue.continue` - Continue.dev (AI code completion and chat)

### Files Removed

- Legacy `setup/container-setup.sh` (duplicate)
- Old `.devcontainer/devcontainer-setup.conf` (no longer needed)

## Architecture Summary

**Official Features handle:**

- Language runtimes (Node.js)
- Development tools (Git, GitHub CLI, Docker)
- Shell environment (Zsh with Oh My Zsh)
- Package managers (Homebrew, pnpm, yarn)

**Container setup script handles:**

- SSH key copying and permissions
- AI CLI tools installation

**User dotfiles handle:**

- Shell history configuration (`~/prj/dotfiles/shell/init.sh`)
- Editor configuration
- Additional shell customizations

## Environment Variables

Essential variables preserved in `devcontainer.json`:

- `MCRA_HISTORY_DIR` - Persistent shell history location
- `WORKSPACE_FOLDER` - For history file naming
- `TZ`, `LC_ALL`, `LANG` - Locale and timezone
- `OLLAMA_HOST` - Local LLM development

## AI CLI Tools Included

- **Claude CLI** (`claude`) - Anthropic's Claude via pnpm
- **Aider** (`aider`) - AI pair programming via pipx
- **GitHub Copilot CLI** (`github-copilot-cli`) - GitHub's AI assistant via npm
- **Gemini CLI** (`gemini`) - Google's Gemini via pnpm
- **Cline** - VS Code extension (not CLI)
- **Continue.dev** - VS Code extension (not CLI)
