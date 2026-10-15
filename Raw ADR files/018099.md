# ADR 005: Interactive Mode with FZF

## Status

Accepted

## Context

Users working with large log datasets (10k-100k+ messages) face several challenges:

### Problems

1. **Static JSON output**: Once search completes, users get a large JSON blob that's hard to explore
2. **No filtering**: Must pipe through `jq` or other tools to filter results
3. **No quick navigation**: Can't quickly jump between messages or view details
4. **Copy/paste difficulty**: Hard to extract specific information from JSON output
5. **Context switching**: Must switch between terminal and editor to view/analyze logs
6. **Memory intensive**: Loading entire JSON in editor for large datasets

### User Request

Users specifically requested an interactive mode similar to `fzf` for more effective interaction with large datasets, allowing:
- Quick navigation through results
- Fuzzy searching within results
- Easy copying of specific log data
- Visual exploration without external tools

## Decision

**Implement a single `-i/--interactive` flag that launches an FZF-based interactive browser for search results.**

### Key Design Principles

1. **Single external dependency**: FZF only (no fallback to avoid complexity)
2. **Performance first**: JSONL format for O(1) preview access with sed
3. **Simple interface**: One flag, clear keybindings
4. **No new gems**: Use stdlib + external FZF binary
5. **Clear error messages**: Guide users to install FZF if missing

## Implementation

### Architecture

```
lib/
  sumologic/
    interactive.rb              # Entry point, FZF availability check
    interactive/
      fzf_viewer.rb            # FZF integration and UI
```

### Data Flow

```
Search Results (JSON)
    ↓
Interactive.launch(results)
    ↓
Check FZF availability
    ↓
FzfViewer.new(results).run
    ↓
Create temp files:
  - input.txt (formatted display lines)
  - preview.jsonl (one JSON per line)
    ↓
Launch FZF with:
  - Preview command (sed + jq)
  - Keybindings for actions
  - Color-coded display
    ↓
User navigates/selects
    ↓
Export/copy/save selected messages
```

### Performance Optimization: JSONL Format

**Decision**: Store preview data as JSONL (one JSON per line) instead of individual files.

**Rationale**:
- For 100k messages:
  - ❌ 100k individual files = filesystem overhead, slow creation/cleanup
  - ✅ Single JSONL file = fast write, O(1) line extraction with `sed -n Np`
- Preview command: `sed -n "${line}p" file.jsonl | jq -C .`
  - Instant extraction (<1ms per message)
  - Syntax highlighting with jq
  - Constant memory usage

### Text Selection Solution

**Challenge**: FZF preview pane is read-only, users can't select text with mouse.

**Solution**: Bind `Tab` to open current message in `less` pager:
- Press Tab → Opens full JSON in less
- Normal mouse selection works in less
- Press 'q' → Returns to FZF
- Balances convenience with simplicity

**Rejected alternatives**:
- ❌ `--no-mouse` flag: Makes entire UI non-interactive
- ❌ Complex terminal bypass instructions: Too technical for users
- ❌ Custom TUI with mouse support: Major complexity increase

### Keybindings

```ruby
'--bind=enter:toggle',           # Select/unselect (stays in FZF)
'--bind=tab:execute(view_cmd)',  # Open in pager for copying
'--bind=ctrl-s:...+abort',       # Save and exit
'--bind=ctrl-y:...+abort',       # Copy and exit
'--bind=ctrl-e:...+abort',       # Export and exit
'--bind=ctrl-a:select-all',      # Select all
'--bind=ctrl-d:deselect-all',    # Deselect all
'--bind=ctrl-/:toggle-preview',  # Toggle preview
'--bind=ctrl-q:abort'            # Quit
```

### Display Format

**Left pane (list):**
```
HH:MM:SS LEVEL   source_category      message_preview
10:23:45 ERROR   prod/api              Connection timeout after 30s
```

**Right pane (preview):**
```json
{
  "_messagetime": "1705318425000",
  "_sourceCategory": "prod/api",
  "_sourceName": "api-server-03",
  "level": "ERROR",
  "message": "Connection timeout after 30s",
  ...
}
```

### Error Handling

If FZF not installed:
```
╔════════════════════════════════════════════════════════════╗
║  Interactive mode requires FZF to be installed             ║
╚════════════════════════════════════════════════════════════╝

📦 Install FZF:

   macOS:    brew install fzf
   Ubuntu:   sudo apt-get install fzf
   ...
```

## Consequences

### Positive

1. **Excellent UX**: Fast, intuitive log exploration
2. **Performance**: Handles 100k+ messages efficiently
3. **Zero gem dependencies**: Only FZF binary required
4. **Familiar**: FZF is widely used (kubectl, git, vim plugins)
5. **Composable**: Still outputs JSON normally without `-i` flag
6. **Simple**: One flag unlocks full interactive experience
7. **Copyable**: Tab key provides easy text selection in pager

### Negative

1. **External dependency**: Requires FZF installation
2. **Platform limitation**: FZF not available on all platforms
3. **No fallback**: If FZF missing, feature unavailable (intentional trade-off for simplicity)
4. **Preview read-only**: Can't directly select text in preview (mitigated with Tab → pager)

### Trade-offs

**Rejected: tty-prompt fallback**
- Would add complexity (two implementations)
- tty-prompt has poor performance with large datasets
- Clear error message is better than degraded experience

**Rejected: jq integration**
- Keep tools separate (Unix philosophy)
- Users can pipe: `sumo-query search ... | jq ...`
- FZF already provides powerful filtering

**Accepted: Read-only preview**
- Tab key → pager provides copyable view
- Simpler than implementing custom mouse handling
- Good enough UX trade-off

## Metrics

- **Code added**: ~190 lines (fzf_viewer.rb) + ~40 lines (interactive.rb)
- **No new gems**: Zero dependencies added
- **Test coverage**: Existing tests all pass
- **Performance**: Constant memory, instant preview updates

## References

- FZF: https://github.com/junegunn/fzf
- Similar implementations: kubectl-fzf, git-fzf, lazygit
- User request: "like fzf, we can interact with those dataset more effective"
