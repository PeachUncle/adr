# Design: Enhanced Built-in Keybindings Discovery

## Context
Neovim has two types of keybindings:
1. **Registered keymaps** - Explicitly registered via `vim.keymap.set()`, `nvim_set_keymap()`, or legacy `:map` commands. These are queryable via `vim.api.nvim_get_keymap()`.
2. **Built-in commands** - Core Neovim functionality handled directly by the command processor (e.g., `dd`, `yy`, `<C-w>h`, `gg`, `G`, etc.). These are NOT exposed through keymap APIs.

The current implementation only shows registered keymaps, leaving users unaware of hundreds of built-in commands. This change aims to provide comprehensive visibility while maintaining educational clarity.

## Goals / Non-Goals

**Goals:**
- Show ALL active keybindings including built-in Neovim commands
- Clearly distinguish between built-in, plugin, and user keybindings
- Maintain educational value by explaining the different sources
- Keep implementation simple and maintainable for this example plugin

**Non-Goals:**
- Create a production-grade keybinding manager (this is an educational example)
- Support dynamic help file parsing (too complex for minimal example)
- Provide keybinding conflict resolution (out of scope)
- Support all possible Neovim edge cases (focus on common patterns)

## Decisions

### Decision 1: Approach for Built-in Keybindings
**Chosen: Programmatic parsing of Neovim's runtime index.txt**

**Rationale:**
- **Authoritative source**: Uses Neovim's own official documentation, not third-party sources
- **Always accurate**: Automatically matches the installed Neovim version
- **Maintainable**: No hardcoded lists to manually update when Neovim changes
- **Educational**: Teaches users how to access runtime help files programmatically
- **Complete coverage**: Access to all ~1,264 documented built-in keybindings

**Implementation approach:**
1. Use `vim.api.nvim_get_runtime_file('doc/index.txt', false)` to locate the help file
2. Parse structured entries using pattern matching (format: `|tag|\t\tkey\t\tdescription`)
3. Extract mode prefix from tag (e.g., `i_CTRL-A` → insert mode)
4. Cache parsed results for performance (only parse once per session)

**Alternatives considered:**
1. **Hardcoded reference list** - Becomes outdated, requires manual maintenance, incomplete coverage
2. **Parse `:map` output** - Only shows registered keymaps, not true built-ins like `dd`, `gg`, etc.
3. **Runtime API discovery** - No such API exists for built-in commands
4. **Published online documentation** - Often outdated, version mismatches, not programmatically reliable

### Decision 2: Data Structure
Parse index.txt into a Lua table indexed by mode, matching the structure from `vim.api.nvim_get_keymap()`:

```lua
-- Parsed from index.txt
local builtin_keymaps = {
  n = {  -- Normal mode
    { lhs = "dd", desc = "delete N lines [into register x]" },
    { lhs = "<C-W>h", desc = "go to Nth left window (stop at first window)" },
    -- ... ~437 normal mode entries from index.txt
  },
  i = {  -- Insert mode
    { lhs = "<C-W>", desc = "delete word before the cursor" },
    -- ... ~96 insert mode entries
  },
  -- ... other modes: v (~119), c (~607), o (~3)
}
```

**Rationale:**
- Matches the existing structure from `vim.api.nvim_get_keymap()` for easy merging
- Uses `lhs` (left-hand side) and `desc` fields for consistency
- Parsed dynamically from authoritative source
- Complete coverage without manual curation

### Decision 3: Source Indicators
Add visual prefixes to distinguish keybinding sources:
- `[C]` - Core Neovim built-in command
- `[P]` - Plugin-registered keymap
- `[U]` - User-defined keymap (buffer-local, marked with `[B]`)

**Rationale:**
- Clear visual distinction without changing column layout significantly
- Consistent with existing `[B]` prefix for buffer-local keymaps
- Easy to understand in documentation

### Decision 4: Scope of Built-in Commands
Include ALL built-in commands documented in index.txt, with optional filtering for display:

**Coverage:**
- All ~1,264 entries from index.txt across all modes
- Normal mode: ~437 commands (operators, motions, window commands, etc.)
- Insert mode: ~96 commands (special keys, completion, etc.)
- Visual/Select modes: ~119 commands
- Command-line mode: ~607 commands (editing, navigation, completion)
- Operator-pending: ~3 commands

**Display filtering:**
- Allow users to filter by mode (default: show current mode)
- Provide search/grep functionality in the display buffer
- Group by category when possible (editing, navigation, window management, etc.)

**Rationale:**
- Complete coverage: users get the full picture
- Authoritative: straight from Neovim's documentation
- Filterable: overwhelming data can be narrowed down interactively
- Educational: exposes the full scope of Neovim's built-in functionality

## Risks / Trade-offs

**Risk: Incomplete coverage**
- Mitigation: Document in header that built-in list is curated, not exhaustive
- Add note pointing users to `:help index` for complete reference

**Risk: Neovim version differences**
- Mitigation: Focus on stable, long-standing commands (Neovim 0.8+)
- Document any version-specific commands in comments

**Risk: Maintenance burden**
- Mitigation: Keep list focused on core commands that rarely change
- Add comments explaining how to extend the list

**Trade-off: Accuracy vs. Simplicity**
- Hardcoded list won't detect if user has unmapped built-in commands
- Acceptable for educational plugin; document this limitation

## Migration Plan

No migration needed - this is a pure enhancement that adds functionality without breaking existing behavior.

**Deployment:**
1. Implement built-in keybindings reference list
2. Update display functions to merge and format all sources
3. Add educational comments and documentation
4. Update README with new capability
5. Test manually in clean Neovim and LazyVim environments

**Rollback:**
- Simple: remove built-in keybindings list and revert display functions
- No data migration or user config changes needed

## Open Questions

1. **Should we group built-in keybindings by category?**
   - Options: Group by category (editing, navigation, etc.) or show inline with registered keymaps
   - Recommendation: Show inline, use category in description for searchability

2. **Should we support user configuration to hide built-in keybindings?**
   - Options: Add `show_builtin_keymaps` config option or always show them
   - Recommendation: Always show (educational value), mention this is optional in comments

3. **How detailed should built-in command descriptions be?**
   - Options: Brief (e.g., "Delete line") vs. detailed (e.g., "Delete current line into default register")
   - Recommendation: Brief for readability, encourage users to check `:help` for details
