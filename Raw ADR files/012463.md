# ADR 0004: Configuration Patterns and Best Practices

## Status

Accepted

## Context

Nix expressions can be written in many ways, but inconsistent patterns make the configuration harder to understand and maintain. We need established patterns for writing Nix code that promote readability, reusability, and maintainability across the entire configuration.

## Decision

### Module Structure Pattern

**Standard Module Template**:
```nix
{ pkgs, config, lib, ... }:  # 1. Function parameters
{
  # 2. Imports (if any)
  imports = [
    ./submodule.nix
  ];

  # 3. Options/settings in logical groups
  option.category = {
    setting = value;
  };

  # 4. Comments explain WHY, not WHAT
  # Necessary for using flakes on this system.
  nix.settings.experimental-features = [ "nix-command flakes" ];
}
```

**Rules**:
1. **Parameter declaration**: Always include `{ pkgs, config, ... }` even if unused
2. **Imports first**: Place all imports at the top
3. **Logical grouping**: Group related settings together
4. **Comments for context**: Explain reasoning, not obvious facts

### Parameter Passing Conventions

**Explicit vs Implicit**:
```nix
# ✓ Good: Explicit parameter passing
{ system, nix-darwin, home-manager, ... }:

# ✗ Avoid: Undocumented implicit parameters
{ ... }@inputs:
```

**Let Bindings for Clarity**:
```nix
# ✓ Good: Define reusable values in let
{ system, nix-darwin, home-manager, ... }: let
  userhome = {
    kazukishinohara = import ../home;
  };
in {
  # Use userhome here
}

# ✗ Avoid: Inline complex expressions
modules = [ (import ../home { inherit pkgs config; }) ];
```

**Rules**:
1. **Explicit parameters**: List all parameters by name when possible
2. **Use `let` for reusable values**: Define once, use multiple times
3. **`inherit` for passing through**: Use `inherit` when forwarding parameters
4. **Descriptive names**: `userhome`, not `uh` or `userHomeConfigurations`

### Attribute Set Patterns

**Nested Attributes**:
```nix
# ✓ Good: Hierarchical structure
home = {
  username = "kazukishinohara";
  homeDirectory = "/Users/kazukishinohara";
  stateVersion = "25.05";
};

# ✗ Avoid: Flat structure
home.username = "kazukishinohara";
home.homeDirectory = "/Users/kazukishinohara";
home.stateVersion = "25.05";
```

**List Formatting**:
```nix
# ✓ Good: Multi-line for readability
home.sessionPath = [
  "/Users/kazukishinohara/.nix-profile/bin"
  "/etc/profiles/per-user/kazukishinohara/bin"
  "/run/current-system/sw/bin"
];

# ✗ Avoid: Long single line
home.sessionPath = [ "/Users/kazukishinohara/.nix-profile/bin" "/etc/profiles/per-user/kazukishinohara/bin" "/run/current-system/sw/bin" ];
```

### DRY (Don't Repeat Yourself) Principles

**Extract Common Values**:
```nix
# ✓ Good: Define username once
{ config, ... }: let
  username = "kazukishinohara";
in {
  home.username = username;
  home.homeDirectory = "/Users/${username}";
  home.sessionPath = [
    "/Users/${username}/.nix-profile/bin"
  ];
}

# ✗ Avoid: Hardcoded repetition
home.username = "kazukishinohara";
home.homeDirectory = "/Users/kazukishinohara";
```

**Reusable Modules**:
- Extract repeated patterns into separate modules
- Use functions for parameterized configuration
- Share common settings via imports

### String and Path Conventions

**String Interpolation**:
```nix
# ✓ Good: Use ${} for variables
"/Users/${username}/github"

# ✗ Avoid: String concatenation
"/Users/" + username + "/github"
```

**Path Literals**:
```nix
# ✓ Good: Relative paths for local modules
import ./programs.nix
import ../home

# ✗ Avoid: String paths
import "${./.}/programs.nix"
```

### Error Prevention Patterns

**Explicit Boolean Values**:
```nix
# ✓ Good: Explicit true/false
xdg.enable = true;

# ✗ Avoid: Implicit or unclear
xdg.enable = 1;  # Not valid Nix
```

**Platform Specification**:
```nix
# ✓ Good: Explicit platform
nixpkgs.hostPlatform = "aarch64-darwin";

# ✗ Avoid: Auto-detection without documentation
# (could change between rebuilds)
```

**Allow Unfree Explicitly**:
```nix
# ✓ Good: Document why unfree is needed
nixpkgs.config.allowUnfree = true;  # Required for: VS Code, etc.

# ✗ Avoid: Silent unfree allowance
```

### Configuration Organization

**Order of Declarations**:
1. Platform and system settings
2. Core Nix configuration
3. User/home settings
4. Package installation
5. Program-specific configuration
6. Environment variables and paths

**File Size Guidelines**:
- Single module: < 150 lines
- If larger: Split by logical domain
- Use imports to aggregate

### Version Pinning Pattern

**State Version**:
```nix
# ✓ Good: Document when version was set
home.stateVersion = "25.05"; # Set on initial install: 2025-01-02

# ✗ Avoid: No context
home.stateVersion = "25.05";
```

**Rules**:
- Set `stateVersion` once, rarely change
- Document the date and reason for changes
- Don't chase latest version without reason

## Consequences

### Positive

- Consistent code style across all modules
- Easier code review and maintenance
- Reduced bugs from common mistakes
- New contributors can follow established patterns
- Refactoring is safer with clear patterns

### Negative

- Requires discipline to follow patterns
- May need refactoring of existing code
- Some patterns may feel verbose initially

### Code Review Checklist

When adding/reviewing configuration:
- [ ] Parameters explicitly declared?
- [ ] Let bindings used for repeated values?
- [ ] Comments explain reasoning, not syntax?
- [ ] Lists formatted multi-line?
- [ ] No hardcoded repetition?
- [ ] Platform/version explicitly set?
- [ ] Module size reasonable (< 150 lines)?

## Examples from Current Configuration

**Good Patterns**:
- `nix/home/base.nix:1-26` - Clean module structure
- `nix/darwin/default.nix:8-10` - Let binding for userhome
- `flake.nix:4-22` - Explicit input declarations

**Areas for Improvement**:
- Extract common username from multiple files
- Add comments explaining complex settings
- Document stateVersion with date

## References

- [Nix Language Basics](https://nixos.org/manual/nix/stable/language/)
- [Nixpkgs Manual - Style Guide](https://nixos.org/manual/nixpkgs/stable/#chap-conventions)
- Current implementation: `nix/home/base.nix`, `nix/darwin/nix.nix`
