# ADR 0001: Module Organization Principles

## Status

Accepted

## Context

The nix-darwin configuration manages both system-level settings and user-level environments. Without clear organization principles, the configuration can become difficult to maintain, understand, and extend. We need a structured approach to organize Nix modules that promotes clarity, maintainability, and scalability.

## Decision

We organize modules following a hierarchical, domain-driven structure:

### Directory Structure

```
nix/
├── darwin/          # System-level configurations (nix-darwin)
│   ├── default.nix  # Entry point, defines darwinConfigurations
│   ├── configuration.nix  # Aggregates all darwin modules
│   ├── nix.nix      # Nix daemon and build settings
│   ├── users.nix    # User account definitions
│   ├── fonts.nix    # System font configuration
│   └── macos.nix    # macOS system preferences
└── home/            # User-level configurations (home-manager)
    ├── default.nix  # Entry point, aggregates home modules
    ├── base.nix     # Core home-manager settings
    ├── packages.nix # User package installations
    ├── programs.nix # Program-specific configurations
    └── tex.nix      # LaTeX/TeX environment
```

### Organization Principles

1. **Single Responsibility**: Each module file focuses on a specific domain
   - `fonts.nix` handles only font-related configuration
   - `users.nix` manages only user accounts
   - `programs.nix` configures individual program settings

2. **Aggregation via default.nix**: Use `default.nix` as the single entry point
   - Acts as a module aggregator using `imports = [...]`
   - Handles parameter passing and dependencies
   - Provides clean interface for parent configurations

3. **Flat Module Hierarchy**: Keep modules at one or two levels maximum
   - Avoid deeply nested directory structures
   - If a module grows too large, split by domain, not by hierarchy
   - Example: Split large `programs.nix` into `programs/git.nix`, `programs/shell.nix`

4. **Naming Conventions**:
   - Use lowercase with hyphens for directories: `nix-darwin`
   - Use lowercase with underscores for multi-word files: `system_settings.nix`
   - Keep names descriptive and domain-specific

5. **Module Scope**:
   - System-wide settings → `nix/darwin/`
   - User-specific settings → `nix/home/`
   - Shared utilities → Keep in respective directories, use `lib` if needed

## Consequences

### Positive

- Clear separation between system and user configurations
- Easy to locate specific configuration settings
- Supports incremental changes without affecting unrelated modules
- New modules can be added without restructuring existing code
- Git history shows changes at the right granularity

### Negative

- More files to manage (vs. monolithic configuration)
- Need to maintain imports in aggregation files
- May require refactoring when domains change

### Migration Path

When adding new configuration:
1. Identify if it's system-level (darwin) or user-level (home)
2. Find the appropriate domain module or create a new one
3. Add to the relevant `default.nix` imports list
4. Document the module's purpose in comments

## References

- [Nix Pills - Module System](https://nixos.org/guides/nix-pills/)
- [Home Manager Manual](https://nix-community.github.io/home-manager/)
- Current implementation: `nix/darwin/default.nix:1`, `nix/home/default.nix:1`
