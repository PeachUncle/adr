## Context
This change adds a commands viewer feature similar to the existing `NvimPluginAllKeybindings` feature. The plugin is an educational example demonstrating Neovim plugin development, so this feature should showcase how to programmatically discover and display all ex-commands.

**Critical Discovery:** Neovim's command query APIs have significant limitations:
- `vim.api.nvim_get_commands({})` - Returns global **user-defined** commands only
- `vim.api.nvim_buf_get_commands(0, {})` - Returns buffer-local **user-defined** commands only

These APIs **do not** return built-in ex-commands (`:help`, `:quit`, `:write`, `:substitute`, `:global`, `:lua`, `:terminal`, `:checkhealth`, `:messages`, etc.). Built-in commands are handled internally by Neovim's ex-command processor and are not exposed through the commands API.

To provide complete command discovery (similar to how the keybindings viewer works), we must parse Neovim's runtime documentation file `doc/index.txt`, which comprehensively documents all ~539 built-in ex-commands.

## Goals / Non-Goals

### Goals
- Provide a comprehensive way to discover **all** ex-commands in the current Neovim session (built-in + user-defined)
- Display commands in a readable, educational format with clear source indicators
- Demonstrate usage of `vim.api.nvim_get_commands()` and `vim.api.nvim_buf_get_commands()` for user-defined commands
- Demonstrate parsing Neovim's runtime documentation for built-in commands (educational value)
- Follow the same patterns as the existing keybindings viewer for consistency
- Clearly explain why parsing is necessary (built-in commands not exposed via API)

### Non-Goals
- Filtering or categorizing commands beyond basic built-in vs. user-defined distinction
- Advanced command introspection beyond what's in the metadata (argument completion details, etc.)
- Making the commands viewer highly configurable or extensible
- Parsing commands from plugin documentation files (only Neovim core built-ins from `doc/index.txt`)

## Decisions

### Built-in Command Discovery: Parse doc/index.txt
Parse Neovim's runtime `doc/index.txt` file to extract built-in ex-commands. This is the authoritative source for Neovim's built-in commands and matches the installed Neovim version automatically.

Format in `doc/index.txt`:
```
|:help|		:h[elp]		open a help window
|:quit|		:q[uit]		quit current window
|:write|	:w[rite]	write to a file
```

Pattern: `|:tag|\t\t:command[abbrev]\t\tdescription`

**Why this approach:**
- Same pattern as keybindings viewer (parses `doc/index.txt` for built-in keybindings)
- Uses authoritative source (Neovim's own documentation)
- Automatically matches installed Neovim version
- No manual maintenance when Neovim updates
- Educational value: shows how to parse runtime documentation

**Alternatives considered:**
- Only show user-defined commands - Rejected because users primarily use built-in commands (`:help`, `:quit`, etc.)
- Maintain a hardcoded list - Rejected because it requires manual updates and may be version-specific
- Parse multiple help files - Rejected to keep implementation simple; `index.txt` is comprehensive

### User-defined Command Discovery: API
Use `vim.api.nvim_get_commands({})` for global user-defined commands and `vim.api.nvim_buf_get_commands(0, {})` for buffer-local user-defined commands.

**Why this approach:**
- Standard Neovim APIs for user-defined command discovery
- Returns structured metadata (name, attributes, description)
- Buffer-local commands are important (LSP commands, etc.)

**Alternatives considered:**
- Only show global commands - Rejected because buffer-local commands (like LSP commands) are important
- Parse `:command` output - Rejected because the API provides structured data

### Display Format
Display commands in a table format with columns:
- Source indicator ([C] for core/built-in, [G] for global user-defined, [B] for buffer-local user-defined)
- Command name (`:CommandName` or `:com[mand]` for abbreviated forms)
- Attributes (bang, range, etc. for user-defined commands)
- Description

**Why this approach:**
- Consistent with keybindings viewer format
- Clear visual distinction between built-in and user-defined
- Educational: users learn which commands are built-in vs. from plugins

**Alternatives considered:**
- Grouping by source (built-in section, then user-defined) - Rejected in favor of alphabetical sorting with source indicators
- Separate buffers for built-in vs. user-defined - Rejected to keep UX simple

### Keymap Choice
Use `<leader>pc` for "Plugin Commands" to follow the existing pattern:
- `<leader>ph` - Plugin Hello
- `<leader>pt` - Plugin Toggle
- `<leader>pk` - Plugin Keybindings
- `<leader>pa` - Plugin All keybindings
- `<leader>pc` - Plugin Commands (new)

**Alternatives considered:**
- `<leader>pe` - Rejected because "e" doesn't clearly indicate "commands"
- No default keymap - Rejected for consistency with other features

### Performance: Cache Parsed Built-ins
Cache the parsed built-in commands in a module-level variable (parse once per Neovim session).

**Why this approach:**
- Parsing ~539 commands from `doc/index.txt` is relatively fast but unnecessary to repeat
- Built-in commands don't change during a Neovim session
- Same pattern as keybindings viewer's `builtin_keymaps_cache`

## Risks / Trade-offs

### Risk: Command list may be very long (~539 built-in + user-defined)
**Mitigation:** Use a scratch buffer so users can search with `/` and navigate freely. Include counts in the header so users understand the scope.

### Risk: Parsing doc/index.txt may fail or format may change
**Mitigation:** 
- Handle file not found gracefully (show warning, display only user-defined commands)
- Use robust regex patterns that handle variations
- Test with current Neovim version (0.11.4)
- Document the expected format in code comments

### Risk: User-defined commands list may be very long in some setups
**Mitigation:** Count and display statistics in header. Users can search with `/` within the buffer.

### Trade-off: Simplicity vs. completeness
We show all discoverable commands without intelligent filtering. This may include internal plugin commands that aren't user-facing, but filtering would require heuristics that may not be reliable. Choose completeness and let users search/filter visually.

### Trade-off: Parsing complexity vs. educational value
Parsing `doc/index.txt` adds implementation complexity, but:
- It's necessary for complete command discovery
- It has high educational value (shows how to work with runtime files)
- It follows the established pattern from the keybindings viewer
- Users expect completeness (similar to `:help` showing all commands)

## Migration Plan
No migration needed - this is a new additive feature. No breaking changes to existing functionality.

## Open Questions
None - the design follows the established keybindings viewer pattern and addresses the API limitation through documentation parsing.
