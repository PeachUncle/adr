# Design: Global Keybindings Viewer

## Context

The nvim-plugin currently provides a `:NvimPluginKeybindings` command that displays only the plugin's own keybindings. This is useful for learning about the plugin itself, but users often need to discover and troubleshoot keybindings from multiple sources:

- **Neovim core**: Built-in commands and default mappings
- **Plugins**: LazyVim, Telescope, LSP, and hundreds of other plugins
- **User configurations**: Custom keymaps defined in init.lua or plugin specs

The current limitation makes it difficult to:
- Discover what keybindings are available
- Debug keymap conflicts (when multiple plugins map the same key)
- Learn how different plugins organize their keybindings
- Understand which mode each binding applies to

### Stakeholders
- **Plugin learners**: Users trying to understand Neovim plugin development patterns
- **Neovim users**: Anyone wanting to discover available keybindings in their session
- **Plugin developers**: Developers debugging keymap conflicts or testing their own plugins

### Constraints
- Must remain educational and simple (this is a teaching plugin)
- Should use modern Neovim APIs (0.8+) 
- No external dependencies
- Must work with LazyVim lazy-loading
- Output should be human-readable, not machine-parseable

## Goals / Non-Goals

### Goals
- Provide a comprehensive view of ALL keybindings in the current Neovim session
- Group keybindings by mode for clarity (normal, insert, visual, etc.)
- Display key, command/action, and description in readable format
- Filter out internal/unnamed mappings to reduce noise
- Include educational comments explaining the Neovim keymap query APIs
- Maintain consistency with existing `:NvimPluginKeybindings` command patterns

### Non-Goals
- Interactive filtering or searching (keep it simple - users can use `/` to search in the buffer)
- Editing or modifying keybindings (read-only display only)
- Detecting or highlighting keymap conflicts (future enhancement)
- Exporting keybindings to files (out of scope)
- Custom sorting or ordering beyond mode grouping
- Syntax highlighting or advanced formatting

## Decisions

### Decision 1: Use `vim.api.nvim_get_keymap()` for Global Keymaps
**What**: Query global keymaps using `vim.api.nvim_get_keymap(mode)` for each mode.

**Why**: 
- This is the standard Neovim API for retrieving keymaps
- Returns structured data (table with `lhs`, `rhs`, `desc`, etc.)
- Supports all modes (n, i, v, s, o, t, c)
- Well-documented and stable API

**Alternatives considered**:
- `vim.api.nvim_buf_get_keymap()`: Only returns buffer-local keymaps, not global ones
- `vim.fn.maplist()`: Older vimscript-style API, less structured output
- Parsing `:map` command output: Fragile, string-based parsing

### Decision 2: Include Buffer-Local Keymaps
**What**: Also query buffer-local keymaps using `vim.api.nvim_buf_get_keymap(0, mode)` for the current buffer.

**Why**:
- Many plugins (like LSP) register buffer-local keymaps
- These are important for users to discover
- Buffer-local keymaps override global ones, so they're relevant

**Trade-offs**:
- Adds complexity (need to query both global and buffer-local)
- Output may be longer
- Mitigation: Clearly label buffer-local keymaps in the output

### Decision 3: Query All Seven Modes
**What**: Query keymaps for modes: `n` (normal), `i` (insert), `v` (visual), `s` (select), `o` (operator-pending), `t` (terminal), `c` (command-line).

**Why**:
- Complete coverage of all possible contexts
- Educational value - users learn about different modes
- Some plugins use less common modes (terminal, operator-pending)

**Alternatives considered**:
- Only query common modes (n, i, v): Incomplete, misses terminal and command-line keymaps
- Query `x` (visual) and `v` separately: `v` includes visual mode already

### Decision 4: Filter Internal/Plugin-Specific Mappings
**What**: Optionally filter out mappings that:
- Have no description (`desc` is nil or empty)
- Start with `<Plug>` (internal plugin mappings)
- Are used for plugin implementation details

**Why**:
- Reduces noise in the output
- Focuses on user-relevant keybindings
- Makes the output more educational

**Trade-offs**:
- May hide some useful information
- Mitigation: Make filtering logic clear in comments; consider making it configurable in future

### Decision 5: Group by Mode with Clear Headers
**What**: Display keybindings grouped by mode, with section headers like:
```
=== Normal Mode (n) ===
=== Insert Mode (i) ===
```

**Why**:
- Makes output scannable and organized
- Helps users understand context for each binding
- Educational - users learn about mode-specific keymaps

**Alternatives considered**:
- Flat list sorted alphabetically: Loses mode context
- Tree structure by plugin: Complex, hard to determine plugin source
- Table with mode column: Less scannable for long lists

### Decision 6: Format as Fixed-Width Columns
**What**: Display keybindings in three columns:
- Key (e.g., `<leader>ph`)
- Command/Action (e.g., `:NvimPluginHello` or Lua function reference)
- Description (e.g., "Show plugin greeting")

**Why**:
- Readable and consistent with `:NvimPluginKeybindings` output
- Easy to scan visually
- Works well in terminal (monospace font)

**Implementation**:
```lua
string.format("%-20s %-40s %s", key, command, description)
```

### Decision 7: Use Scratch Buffer with Unique Name
**What**: Create a scratch buffer named `nvim-plugin://all-keybindings` with:
- `buftype = "nofile"` (not associated with a file)
- `bufhidden = "wipe"` (delete when hidden)
- `modifiable = false` (read-only after content is set)

**Why**:
- Consistent with existing `:NvimPluginKeybindings` implementation
- URI-style name follows Neovim conventions
- Scratch buffer prevents accidental saves

### Decision 8: Add `<leader>pa` Keymap
**What**: Register `<leader>pa` (Plugin All keybindings) as the keymap, respecting `enable_keymaps` config.

**Why**:
- Follows existing pattern: `<leader>ph` (hello), `<leader>pt` (toggle), `<leader>pk` (plugin keybindings)
- Mnemonic: "pa" = "plugin all" or "plugin all keybindings"
- Doesn't conflict with common LazyVim defaults

**Alternatives considered**:
- `<leader>pk` suffix like `<leader>pka`: Too long, not ergonomic
- `<leader>pA`: Requires shift key, less ergonomic
- `<leader>pk` (reuse existing): Confusing, loses plugin-specific keybindings command

## Implementation Architecture

### Module Structure (within `init.lua`)
Since this is a minimal educational plugin, we'll keep everything in `lua/nvim-plugin/init.lua`. The implementation will add:

```lua
-- New helper functions (private, local scope):
local function get_mode_name(mode_char)
  -- Map mode char to human-readable name
end

local function get_all_keymaps()
  -- Query all global and buffer-local keymaps
  -- Returns: { [mode] = { {lhs, rhs, desc}, ... } }
end

local function filter_keymaps(keymaps)
  -- Filter out internal/unnamed mappings
  -- Returns: filtered keymaps table
end

local function format_all_keybindings(keymaps)
  -- Format keymaps into display lines
  -- Returns: array of strings
end

local function show_all_keybindings()
  -- Main function: query, filter, format, display
  -- Creates buffer and shows content
end
```

### Data Flow
```
User invokes :NvimPluginAllKeybindings or <leader>pa
          ↓
show_all_keybindings()
          ↓
get_all_keymaps() → Query vim.api.nvim_get_keymap() for each mode
                   → Query vim.api.nvim_buf_get_keymap() for each mode
                   → Merge results into { [mode] = [keymaps] }
          ↓
filter_keymaps() → Remove <Plug> mappings
                 → Remove keymaps without descriptions (optional)
          ↓
format_all_keybindings() → Group by mode
                          → Format into fixed-width columns
                          → Add headers and separators
          ↓
Create scratch buffer → Set properties (nofile, wipe, read-only)
                      → Set content with vim.api.nvim_buf_set_lines()
                      → Display in current window
```

### API Usage

**Querying Global Keymaps**:
```lua
local modes = { 'n', 'i', 'v', 's', 'o', 't', 'c' }
for _, mode in ipairs(modes) do
  local global_maps = vim.api.nvim_get_keymap(mode)
  -- Returns array of tables: { lhs, rhs, desc, silent, noremap, ... }
end
```

**Querying Buffer-Local Keymaps**:
```lua
local buffer_maps = vim.api.nvim_buf_get_keymap(0, mode)
-- 0 = current buffer
```

**Keymap Table Structure** (returned by APIs):
```lua
{
  lhs = "<leader>ph",           -- Left-hand side (key sequence)
  rhs = "<cmd>NvimPluginHello<cr>", -- Right-hand side (command)
  desc = "Show plugin greeting",    -- Description
  silent = 1,                       -- Silent flag
  noremap = 1,                      -- No-remap flag
  -- ... other fields
}
```

## Risks / Trade-offs

### Risk 1: Large Output Volume
**Risk**: Sessions with many plugins may have 500+ keybindings, making the buffer overwhelming.

**Impact**: High - Users may find the output unusable.

**Mitigation**:
- Filter out `<Plug>` internal mappings (reduces noise significantly)
- Optionally filter unnamed mappings (those without `desc`)
- Users can search within the buffer using `/` (standard Neovim search)
- Future: Add configuration option to control filtering aggressiveness

### Risk 2: Performance with Many Keymaps
**Risk**: Querying and formatting hundreds of keymaps might be slow.

**Impact**: Low - Keymap queries are fast, string formatting is simple.

**Mitigation**:
- Lazy evaluation (only query when command is invoked)
- No complex processing (just iteration and string formatting)
- Acceptable for an on-demand command (users don't expect instant results)

### Risk 3: Buffer-Local Keymaps Change by Buffer
**Risk**: Displayed keymaps are a snapshot of the current buffer; switching buffers changes buffer-local keymaps.

**Impact**: Medium - Users may be confused if they switch buffers.

**Mitigation**:
- Add note in buffer header: "Buffer-local keymaps shown for buffer: [name]"
- Document this behavior in code comments
- This is expected behavior - users can re-run the command in different buffers

### Risk 4: Unclear Command/Action Display
**Risk**: Some keymaps execute Lua functions, which display as `<Lua function>` or memory addresses.

**Impact**: Medium - Users may not understand what the keymap does.

**Mitigation**:
- Display description (if available) as the primary information
- For Lua functions, show "Lua function" as the command
- Most modern plugins provide `desc` field, which is more useful than raw command

### Risk 5: Educational Complexity
**Risk**: Implementation may become too complex for an educational plugin.

**Impact**: Medium - Defeats the plugin's teaching purpose.

**Mitigation**:
- Keep implementation straightforward (no fancy abstractions)
- Add extensive comments explaining each step
- Focus on demonstrating the keymap query APIs
- Accept some repetition (clarity over DRY principle)

## Migration Plan

No migration needed - this is a new feature with no breaking changes.

### Steps
1. Implement new functions in `init.lua`
2. Register new command in `register_commands()`
3. Register new keymap in `register_keymaps()`
4. Update `registered_keymaps` table to include `<leader>pa`
5. Test manually in Neovim
6. Update README.md with usage instructions

### Rollback
If issues arise, simply remove the new command and keymap registrations. No state changes or configuration migrations needed.

## Open Questions

### Q1: Should we filter keymaps without descriptions by default?
**Options**:
- A: Yes, hide unmapped keybindings (cleaner output)
- B: No, show all keybindings (complete information)
- C: Make it configurable via `setup({ show_unnamed_keymaps = false })`

**Recommendation**: Start with Option A (filter by default), add configuration in future if users request it.

### Q2: Should we indicate keymap source (plugin name)?
**Challenge**: Neovim's keymap API doesn't include source information. We'd need to parse `rhs` or `desc` to guess the source.

**Options**:
- A: Don't show source (keep it simple)
- B: Parse `desc` for common patterns like "[Plugin] Description"
- C: Use `vim.fn.maplist()` which includes `script` field (but older API)

**Recommendation**: Option A for now. Source detection is complex and fragile.

### Q3: Should we support filtering by pattern or plugin?
**Example**: `:NvimPluginAllKeybindings Telescope` to show only Telescope keybindings.

**Options**:
- A: Add command argument for filtering (more complex)
- B: Keep it simple - show all keybindings (users can search with `/`)

**Recommendation**: Option B for now. Command arguments add complexity and this is an educational plugin.

### Q4: Should we show global vs buffer-local distinction?
**Options**:
- A: Show separate sections: "Global Keymaps" and "Buffer-Local Keymaps"
- B: Mix them together with a `[B]` prefix for buffer-local
- C: Don't distinguish (simpler, but less clear)

**Recommendation**: Option B (use `[B]` prefix). Balances clarity and simplicity.

### Q5: How to handle very long command strings?
**Example**: Some Lua function definitions in `rhs` can be 100+ characters.

**Options**:
- A: Truncate with `...` at a fixed width (e.g., 40 chars)
- B: Wrap to multiple lines (harder to read in table format)
- C: Show full command (may break column alignment)

**Recommendation**: Option A. Use `string.sub(cmd, 1, 40) .. "..."` for commands longer than 40 chars.
