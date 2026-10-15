# Design: Keybindings Display Feature

## Context

This feature adds a command to display all plugin keybindings in a dedicated buffer. The plugin is an educational example demonstrating Neovim plugin development basics, so the implementation should be simple, well-commented, and illustrate fundamental concepts like buffer manipulation and data formatting.

**Background:**
- Current state: Keybindings are only discoverable via `:map <leader>p*` or README
- Users learning Neovim plugins benefit from seeing registered keymaps in-app
- Buffer display is a common pattern in Neovim plugins (e.g., `:help`, `:messages`, Telescope)

**Constraints:**
- Must remain minimal and educational (avoid over-engineering)
- Single-file implementation in `lua/nvim-plugin/init.lua`
- No external dependencies
- Compatible with Neovim 0.8+

**Stakeholders:**
- Plugin users (learning Neovim)
- Developers using this as a reference example

## Goals / Non-Goals

### Goals
- Provide an in-editor way to view all plugin keybindings
- Demonstrate buffer creation and manipulation in Neovim
- Show how to format and display structured data
- Maintain educational code quality with clear comments
- Keep implementation simple and maintainable

### Non-Goals
- Interactive buffer features (navigation, search, filtering)
- Syntax highlighting or fancy formatting
- Exporting keybindings to other formats
- Integration with external keymap plugins
- Showing keybindings from other plugins

## Decisions

### Decision 1: Store Keybinding Metadata
**What:** Create a local table to track registered keybindings with their metadata (key, command, description)

**Why:**
- Neovim's keymap API doesn't provide easy access to all metadata after registration
- Tracking our own keymaps allows complete control over display format
- Simple data structure (array of tables) is easy to understand for learners

**Implementation:**
```lua
local registered_keymaps = {
  { key = "<leader>ph", command = "NvimPluginHello", desc = "Show plugin greeting" },
  { key = "<leader>pt", command = "NvimPluginToggle", desc = "Toggle plugin state" },
  { key = "<leader>pk", command = "NvimPluginKeybindings", desc = "Show plugin keybindings" },
}
```

**Alternatives considered:**
- Query `vim.api.nvim_get_keymap()`: Complex filtering, lacks our custom descriptions
- Parse keymap definitions: Fragile, harder to maintain
- Hardcode display text: Less maintainable, duplicates information

### Decision 2: Buffer Type and Naming
**What:** Use a scratch buffer with a unique buffer name `nvim-plugin://keybindings`

**Why:**
- Scratch buffers (`buftype=nofile`) are ideal for temporary display
- URI-style naming (`plugin://name`) is a Neovim convention
- Not saved to disk, appropriate for generated content
- Easy to identify and reuse if already open

**Buffer properties:**
```lua
vim.bo.buftype = "nofile"      -- Not associated with a file
vim.bo.bufhidden = "wipe"      -- Delete when hidden
vim.bo.swapfile = false        -- No swap file needed
vim.bo.modifiable = false      -- Read-only after content is set
```

**Alternatives considered:**
- Regular buffer: Would prompt to save, not appropriate
- Floating window: More complex, harder for learners to understand
- Split window: Let user decide how to open buffer

### Decision 3: Display Format
**What:** Simple columnar format with header and aligned columns

**Format example:**
```
nvim-plugin Keybindings
=======================

Key             Command                   Description
---             -------                   -----------
<leader>ph      :NvimPluginHello          Show plugin greeting
<leader>pt      :NvimPluginToggle         Toggle plugin state
<leader>pk      :NvimPluginKeybindings    Show plugin keybindings

Note: <leader> is typically <Space> in LazyVim (or \ by default)
```

**Why:**
- Easy to read and understand
- Demonstrates string formatting in Lua
- Shows all relevant information at a glance
- Educational note helps newcomers understand leader key

**Alternatives considered:**
- Table format with borders: More complex, harder to implement in plain text
- JSON/YAML output: Not human-friendly for quick reference
- List format: Less structured, harder to scan

### Decision 4: Function Organization
**What:** Add three new local functions:
1. `get_keybindings()` - Returns array of keybinding metadata
2. `format_keybindings(bindings)` - Formats data into display text
3. `show_keybindings()` - Creates buffer and displays content

**Why:**
- Separation of concerns: data, formatting, display
- Each function has a single responsibility
- Easy to test and understand individually
- Demonstrates good Lua function organization

**Function signatures:**
```lua
local function get_keybindings()
  -- Returns: array of { key, command, desc }
end

local function format_keybindings(bindings)
  -- Returns: array of strings (lines to display)
end

local function show_keybindings()
  -- Creates buffer, calls get/format, sets content
end
```

### Decision 5: Conditional Keybinding Display
**What:** Show which keymaps are registered based on `enable_keymaps` setting

**Why:**
- User might have disabled default keymaps
- Display should reflect actual state
- Educational: shows how plugin state affects behavior

**Implementation:**
- `get_keybindings()` checks if keymaps are enabled
- If disabled, returns only command information (no key bindings)
- Display includes note: "Default keymaps are disabled"

## Risks / Trade-offs

### Risk: Keybinding Tracking Synchronization
**Risk:** If keymaps are registered but not added to tracking table, display will be incomplete

**Mitigation:**
- Keep registration and tracking adjacent in code
- Add comments warning developers to update both
- Since this is a minimal example with few keymaps, risk is low

### Trade-off: Hardcoded vs Dynamic Keybindings
**Trade-off:** Using a static table vs dynamically querying Neovim's keymap API

**Chosen:** Static table (simpler for educational purposes)

**Impact:**
- Pro: Easier to understand, maintain, and explain
- Pro: Full control over displayed metadata
- Con: Requires manual updates when adding keymaps
- Con: Doesn't show user-defined custom keymaps

**Justification:** For a minimal example plugin with 3 keymaps, simplicity wins

### Trade-off: Buffer Reuse vs New Buffer
**Trade-off:** Reuse existing keybindings buffer vs create new one each time

**Chosen:** Create new buffer each time (or reuse if found)

**Impact:**
- Pro: Simpler implementation for learning purposes
- Pro: Always shows current state
- Con: Multiple invocations could create multiple buffers
- Mitigation: Check if buffer exists with same name, reuse if found

## Migration Plan

N/A - This is a new feature with no breaking changes.

**Rollout:**
1. Implement feature in `lua/nvim-plugin/init.lua`
2. Update README with new command and keymap documentation
3. Test manually with keymaps enabled and disabled
4. No version bump needed (still educational example)

**Rollback:**
- If issues arise, simply remove the new command registration
- No data migration or user configuration changes needed

## Open Questions

### Q1: Should we show user-overridden keymaps?
**Context:** Users can define custom keymaps in their LazyVim config

**Options:**
1. Show only plugin's default keymaps (current design)
2. Query Neovim to show all keymaps pointing to plugin commands
3. Add configuration option to control behavior

**Recommendation:** Option 1 (show only defaults) for simplicity. Can revisit if users request this feature.

### Q2: Should buffer support syntax highlighting?
**Context:** Could add colors/highlighting for better readability

**Options:**
1. Plain text (current design)
2. Add basic syntax highlighting with `vim.api.nvim_buf_add_highlight()`
3. Use help-style syntax

**Recommendation:** Option 1 (plain text) for this iteration. Syntax highlighting adds complexity beyond the core learning goal. Can be added in a future enhancement to demonstrate highlighting APIs.

### Q3: Should we include commands without keymaps?
**Context:** Plugin has commands (`:NvimPluginHello`) that are also accessible via keymaps

**Current design:** Show keybindings only (key → command mapping)

**Alternative:** Show all commands with a note if no keymap exists

**Recommendation:** Current design is sufficient. The feature is specifically for keybindings discovery. Commands are documented in README and via `:command NvimPlugin*`.

---

## Implementation Notes

### Code Location
All new code goes in `lua/nvim-plugin/init.lua` to maintain single-file simplicity.

### Comment Style
Following existing pattern, add:
- Section headers with `====` separators
- Function-level comments explaining purpose
- Inline comments for non-obvious Neovim API usage
- Educational notes about why certain approaches are chosen

### Testing Approach
Manual testing scenarios:
1. Default setup → verify all keymaps shown
2. `enable_keymaps = false` → verify appropriate message
3. Multiple invocations → verify buffer behavior
4. Check buffer properties with `:lua vim.inspect(vim.bo)`
