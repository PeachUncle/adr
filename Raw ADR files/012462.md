# ADR 0003: Dependency Management Strategy

## Status

Accepted

## Context

Nix flakes provide powerful dependency management through inputs, but also introduce complexity around overlays, version following, and dependency resolution. We need a consistent strategy for managing external dependencies, package versions, and overlays to maintain reproducibility and avoid conflicts.

## Decision

### Flake Inputs Strategy

**Core Principle**: Minimize input divergence by using `follows` to ensure consistent nixpkgs across all dependencies.

**Current Input Structure** (`flake.nix`):
```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  nix-darwin = {
    url = "github:nix-darwin/nix-darwin/master";
    inputs.nixpkgs.follows = "nixpkgs";  # ✓ Prevents duplicate nixpkgs
  };
  home-manager = {
    url = "github:nix-community/home-manager";
    inputs.nixpkgs.follows = "nixpkgs";  # ✓ Consistent package versions
  };
  neovim-nightly-overlay = {
    url = "github:nix-community/neovim-nightly-overlay";
    inputs.nixpkgs.follows = "nixpkgs";  # ✓ Same base packages
  };
  rust-overlay = {
    url = "github:oxalica/rust-overlay";
    inputs.nixpkgs.follows = "nixpkgs";  # ✓ Avoids version conflicts
  };
};
```

**Rules**:
1. **Single nixpkgs source**: Use one nixpkgs input (currently `nixpkgs-unstable`)
2. **Always use `follows`**: All dependencies must follow the main nixpkgs
3. **Pin to branches**: Specify branches/tags for stability (`master`, `nixpkgs-unstable`)
4. **Lock versions**: Commit `flake.lock` to version control

### Overlay Management

**Principle**: Overlays modify package definitions; use sparingly and explicitly.

**Overlay Application** (`nix/darwin/default.nix:22-25`):
```nix
nixpkgs.overlays = [
  neovimOverlay    # Specific tool: bleeding-edge neovim
  rustOverlay      # Specific toolchain: rust versions
];
```

**Rules**:
1. **Explicit overlay declaration**: Apply overlays in `darwin/default.nix` only
2. **Purpose-driven**: Each overlay serves a specific, documented need
3. **Limited scope**: Prefer overlays for:
   - Bleeding-edge tools (neovim-nightly)
   - Toolchain management (rust-overlay)
   - Custom package modifications
4. **Avoid for**: General package installation (use `packages.nix` instead)

### Package Version Strategy

**Default Approach**: Use package versions from `nixpkgs-unstable`

**Version Pinning Rules**:
- **No pinning**: For most packages (get updates via `nix flake update`)
- **Overlay pinning**: For critical development tools requiring specific versions
- **Flake input pinning**: When package not in nixpkgs or needs different source

**Updating Strategy**:
```bash
# Regular updates (weekly/monthly)
nix flake update

# Update specific input
nix flake lock --update-input nixpkgs

# Test before committing
darwin-rebuild switch
```

### Dependency Decision Tree

When adding a new dependency:

```
Need new tool/package?
├─ Available in nixpkgs?
│  ├─ Yes → Add to packages.nix ✓
│  └─ No → Is it in a known overlay?
│     ├─ Yes → Add overlay to flake inputs
│     └─ No → Create custom package or use Homebrew temporarily
│
└─ Need specific version?
   ├─ Available in overlay? → Use overlay
   ├─ Need to track upstream? → Add flake input
   └─ Custom build? → Define in packages.nix with fetchFromGitHub
```

### Lock File Management

**Commit Strategy**:
- Always commit `flake.lock` after changes
- Document reason in commit message
- Review lock file diffs for unexpected changes

**Update Frequency**:
- Minor updates: Every 1-2 weeks (security, bug fixes)
- Major updates: Test in branch first
- Before important work: Update and stabilize

## Consequences

### Positive

- Reproducible builds across machines
- Consistent package versions eliminate "works on my machine"
- Clear dependency graph via `nix flake show`
- Single source of truth for package versions
- Reduced closure size (no duplicate nixpkgs)

### Negative

- Must understand flake inputs and follows
- Updates are all-or-nothing (entire nixpkgs)
- Overlay conflicts require manual resolution
- Lock file merges can be complex

### Validation

Check dependency health:
```bash
# Show dependency graph
nix flake metadata

# Check for multiple nixpkgs (should be 1)
nix flake metadata --json | jq '.locks.nodes | map(select(.original.owner == "NixOS")) | length'

# Verify overlays applied
darwin-rebuild build --dry-run
```

## Migration Path

When changing dependencies:
1. Add/modify input in `flake.nix`
2. Add `inputs.nixpkgs.follows = "nixpkgs"` if applicable
3. Apply overlay in `darwin/default.nix` if needed
4. Run `nix flake lock` to update lock file
5. Test with `darwin-rebuild switch --dry-run`
6. Commit both `flake.nix` and `flake.lock`

## References

- [Nix Flakes Documentation](https://nixos.wiki/wiki/Flakes)
- [Nixpkgs Overlays Manual](https://nixos.org/manual/nixpkgs/stable/#chap-overlays)
- Current implementation: `flake.nix:1-51`, `nix/darwin/default.nix:22-25`
