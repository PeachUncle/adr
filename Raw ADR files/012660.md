# Design: Minimal Neovim Plugin

## Context

This is an educational example plugin for Neovim users learning plugin development. The target audience includes:
- Beginners learning Neovim plugin architecture
- Developers familiar with Lua wanting to understand Neovim APIs
- LazyVim users wanting to create custom plugins

Constraints:
- Must work with Neovim 0.8+ (for modern API support)
- No external dependencies (pure Neovim APIs only)
- Single-file implementation preferred for simplicity
- Must integrate seamlessly with LazyVim's lazy-loading

## Goals / Non-Goals

**Goals:**
- Demonstrate modern plugin structure (`lua/nvim-plugin/init.lua`)
- Show best practices for setup functions, commands, and keymaps
- Provide clear, educational code comments
- Support user configuration with sensible defaults
- Work out-of-the-box with LazyVim

**Non-Goals:**
- Advanced features (LSP integration, async operations, etc.)
- Multiple file architecture (keep it simple)
- Automated testing (manual testing is sufficient for examples)
- Support for other plugin managers beyond LazyVim
- Performance optimization (clarity over performance)

## Decisions

### Decision 1: Single-file architecture
**Choice**: Implement everything in `lua/nvim-plugin/init.lua`

**Rationale**: 
- Easier for learners to understand (one file to read)
- Sufficient for demonstrating plugin basics
- Can be expanded to multi-file later if needed

**Alternatives considered**:
- Multi-file: `init.lua`, `commands.lua`, `config.lua` - Rejected as over-engineering for a minimal example

### Decision 2: Use modern Neovim APIs
**Choice**: Use `vim.api.*`, `vim.keymap.set()`, and Lua tables for config

**Rationale**:
- These are the current recommended APIs (Neovim 0.8+)
- Better type safety and Lua integration
- Future-proof for newer Neovim versions

**Alternatives considered**:
- Legacy `vim.cmd()` and vimscript - Rejected as outdated pattern
- Mixing old and new APIs - Rejected for consistency

### Decision 3: Example commands
**Choice**: Implement `:NvimPluginHello` and `:NvimPluginToggle`

**Rationale**:
- Hello: Simple, stateless command demonstrating basic API
- Toggle: Demonstrates stateful plugin behavior
- Both cover common plugin use cases

### Decision 4: Configuration pattern
**Choice**: Accept optional config table in `setup()`, merge with defaults using `vim.tbl_deep_extend()`

**Rationale**:
- Standard pattern in Neovim plugin ecosystem
- Familiar to LazyVim users
- Demonstrates proper configuration handling

### Decision 5: Keymap registration
**Choice**: Provide example keymaps in setup but let users override via LazyVim config

**Rationale**:
- Shows proper keymap registration
- Respects user's keymap preferences
- Follows LazyVim conventions for keymap configuration

## Architecture

```
lua/nvim-plugin/
└── init.lua              # Main module

Structure of init.lua:
1. Module table creation
2. Default configuration
3. State management (for toggle)
4. Command implementations
5. setup() function
6. Return module
```

## API Surface

```lua
-- User-facing API
require("nvim-plugin").setup({
  greeting = "Hello from nvim-plugin!",  -- Customize greeting message
  enable_keymaps = true,                 -- Enable/disable default keymaps
})

-- Commands
:NvimPluginHello    -- Display greeting using vim.notify()
:NvimPluginToggle   -- Toggle plugin state (example stateful behavior)

-- Keymaps (optional, configurable)
<leader>ph          -- Trigger :NvimPluginHello
<leader>pt          -- Trigger :NvimPluginToggle
```

## Implementation Details

### Module Pattern
```lua
local M = {}

-- Private state
local state = {
  enabled = true
}

-- Private functions
local function do_something()
  -- ...
end

-- Public API
function M.setup(opts)
  -- merge config, register commands/keymaps
end

return M
```

### Command Registration
Use `vim.api.nvim_create_user_command()` for creating commands:
- Supports completion
- Better error handling
- Cleaner than `vim.cmd()`

### Keymap Registration
Use `vim.keymap.set()` over deprecated `vim.api.nvim_set_keymap()`:
- Shorter syntax
- Direct Lua function callbacks
- Better defaults

## Risks / Trade-offs

### Risk: Neovim version compatibility
**Mitigation**: Document minimum version (0.8+) clearly in README

### Trade-off: Single file vs multi-file
**Impact**: Plugin may grow beyond one file if expanded
**Mitigation**: Document how to refactor into multi-file structure in code comments

### Trade-off: Limited features
**Impact**: Not representative of complex real-world plugins
**Mitigation**: Document this as "minimal example" and link to advanced examples

## Migration Plan

N/A (initial implementation, no migration needed)

## Open Questions

None - scope is well-defined for minimal example.
