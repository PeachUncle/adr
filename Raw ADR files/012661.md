# Design: Floating Window Sidebar Implementation

## Context
The plugin currently demonstrates a vertical split sidebar pattern (lua/nvim-plugin/sidebar.lua) which integrates with Neovim's window layout system. Users have requested an alternative implementation using a floating window with more direct rendering control via extmarks. This provides an educational comparison between two common sidebar approaches in Neovim plugin development.

**Constraints:**
- Must maintain educational clarity (extensive comments)
- Must coexist with existing vertical split sidebar (no breaking changes)
- Must follow modern Neovim API patterns (vim.api.*, vim.keymap.set)
- Must be minimal example suitable for teaching (no unnecessary complexity)

**Stakeholders:**
- Plugin learners studying different sidebar implementation patterns
- Developers comparing floating window vs split window approaches

## Goals / Non-Goals

**Goals:**
- Demonstrate floating window creation and configuration
- Show extmark-based rendering for complete visual control
- Illustrate keymap isolation in floating contexts
- Provide side-by-side comparison with vertical split approach
- Maintain code quality and educational documentation standards

**Non-Goals:**
- Replace or deprecate the existing vertical split sidebar
- Add complex features beyond basic sidebar functionality
- Implement production-ready features (this is an educational example)
- Support custom user configuration of floating window position/size

## Decisions

### Decision 1: Floating Window Configuration
**What:** Use `nvim_open_win()` with relative="editor", positioned at left edge (col=0), with fixed width (32 columns) and height (lines - 4), bordered with "single" border style, zindex=40.

**Why:**
- `relative="editor"` positions relative to entire Neovim instance (clearer for teaching than "win")
- Left edge positioning (col=0) mirrors traditional sidebar placement
- Fixed dimensions simplify the example (avoids dynamic resizing logic)
- Border provides clear visual separation from other windows
- zindex=40 ensures sidebar appears above normal windows but below command-line

**Alternatives considered:**
- Centered modal overlay - rejected because sidebar metaphor implies edge-anchored positioning
- Dynamic sizing - rejected to keep example minimal
- Custom highlight groups for borders - deferred to keep example focused on core mechanics

### Decision 2: Extmark-Based Rendering vs Traditional Buffer Lines
**What:** Use `nvim_buf_set_lines()` for base content and `nvim_buf_set_extmark()` for enhanced visual elements (virtual text, highlights).

**Why:**
- Demonstrates both rendering approaches in a single example
- `nvim_buf_set_lines()` provides stable line content (searchable, selectable)
- `nvim_buf_set_extmark()` shows advanced rendering (icons, inline highlights, virtual text)
- Educational value: students learn when to use each approach

**Alternatives considered:**
- Pure extmark rendering (no buffer lines) - rejected because it's less discoverable for beginners
- Pure buffer lines (no extmarks) - rejected because user specifically requested extmark demonstration
- Canvas-based rendering - rejected as overly complex for this educational example

### Decision 3: Buffer Configuration Strategy
**What:** Create scratch buffer with buftype="nofile", bufhidden="wipe", swapfile=false, modifiable=false (same as vertical split sidebar).

**Why:**
- Consistency with existing sidebar implementation aids learning
- These options are the standard pattern for UI buffers in Neovim ecosystem
- Students can compare implementations and see shared patterns
- Reusing buffer across open/close cycles is efficient

**Alternatives considered:**
- Recreate buffer each time - rejected for inefficiency and unnecessary complexity
- Use bufhidden="hide" - rejected because it leaves buffers lingering in memory

### Decision 4: Coexistence with Vertical Split Sidebar
**What:** Both sidebar implementations exist as separate modules, callable independently, no shared state.

**Why:**
- Educational value: side-by-side comparison of approaches
- No breaking changes to existing sidebar users
- Demonstrates module isolation patterns
- Users can experiment with both patterns in same session

**Alternatives considered:**
- Replace vertical split with floating window - rejected as breaking change
- Unified sidebar with mode toggle - rejected as adding unnecessary complexity
- Shared state between implementations - rejected to keep modules cleanly separated

### Decision 5: Keymap Namespace
**What:** Use `<leader>pf` for floating sidebar toggle (mnemonic: "plugin floating"), keep `<leader>ps` for split sidebar (mnemonic: "plugin sidebar").

**Why:**
- Clear differentiation between the two sidebar variants
- Follows existing plugin keymap pattern (`<leader>p*`)
- Mnemonic aids discoverability

**Alternatives considered:**
- Reuse `<leader>ps` with toggle between modes - rejected for complexity
- Use `<leader>pF` (capital F) - rejected as less ergonomic

## Risks / Trade-offs

**Risk 1: User confusion between two sidebar implementations**
- **Mitigation:** Clear documentation in code comments explaining differences and use cases
- **Mitigation:** Distinct commands and keymaps make the separation obvious
- **Trade-off:** Some duplication of sidebar logic, but educational benefit outweighs cost

**Risk 2: Floating window overlaps important content**
- **Mitigation:** Users can close with `q`, `<Esc>`, or `:NvimPluginFloatingSidebarClose`
- **Mitigation:** zindex=40 keeps it above windows but below command-line
- **Trade-off:** Floating windows inherently overlap; this is expected behavior

**Risk 3: Extmark API changes in future Neovim versions**
- **Mitigation:** Use stable, documented APIs (nvim_buf_set_extmark is stable in 0.8+)
- **Mitigation:** Comments reference API documentation for future maintainers
- **Trade-off:** All plugin code faces this risk; minimal example makes updates easier

## Migration Plan
Not applicable - this is a new feature addition with no breaking changes.

**Rollout:**
1. Implement floating sidebar module
2. Register commands and keymaps in init.lua
3. Test coexistence with vertical split sidebar
4. Deploy as additive feature

**Rollback:**
- Remove commands and keymaps from init.lua
- Delete floating-sidebar.lua file
- No data or state to migrate (both sidebars are ephemeral UI)

## Open Questions
None - this is a straightforward additive feature with well-defined scope.
