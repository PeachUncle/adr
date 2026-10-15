# 22. Intelligent Tool Result Display for Enhanced TUI Readability

**Status:** Accepted
**Date:** 2025-01-20
**Deciders:** Forge Development Team
**Technical Story:** Improve TUI chat readability by implementing context-aware tool result display with smart truncation, collapsible sections, and overlay support for detailed inspection.

---

## Context

### Background

The current TUI executor (implemented in [ADR-0009](0009-tui-executor-design.md) and enhanced in [ADR-0012](0012-enhanced-tui-executor.md)) displays all tool calls and their results inline in the chat viewport. While this provides full transparency, it creates significant usability issues:

**Current Behavior:**
```
🔧 read_file
  ✓ 1 | package main
    2 |
    3 | import (
    4 |     "fmt"
    5 |     "log"
    ... (200 more lines) ...
    205 | }

🔧 search_files
  ✓ Found 47 matches across 12 files:
    file1.go:23: match content here
    file1.go:45: another match
    file2.go:12: yet another
    ... (44 more matches) ...

🔧 list_files
  ✓ 📁 internal/
    📁 internal/core/
    📄 internal/core/core.go
    📁 pkg/
    ... (150 more files) ...
```

### Problem Statement

The current inline display of all tool results creates several UX problems:

1. **Visual Clutter**: Large tool results (read_file, search_files, list_files) flood the chat, making it hard to follow the conversation flow
2. **Information Overload**: Users are overwhelmed with verbose output they may not need to see in detail
3. **Poor Scannability**: Hard to quickly scan what the agent did without scrolling through pages of output
4. **Context Loss**: Important agent messages and thinking get buried under tool output
5. **Inconsistent Verbosity**: All tools are treated equally, but some are semantically important (task_completion) while others are operational (read_file)

### User Feedback

> "Its a great start, but things like tool results get quite cluttery, especially when reading long files. I want the TUI to still be transparent in what is happening, but be more user friendly and not overwhelming."

### Goals

- Maintain **transparency**: Users should always know what the agent is doing
- Improve **readability**: Chat should be easy to scan and follow
- Reduce **visual clutter**: Large results should not dominate the viewport
- Enable **details on demand**: Full results available when needed
- Support **different tool types**: Small/important tools vs large/operational tools
- Preserve **conversational flow**: Agent thinking and messages should be prominent

### Non-Goals

- Hiding tool execution completely (must remain transparent)
- Removing ability to see full results (details must be accessible)
- Breaking existing overlay system (must integrate smoothly)
- Changing tool approval flow (handled by diff viewer overlay)

---

## Decision Drivers

* **User Experience**: Chat must be pleasant to read and easy to scan
* **Transparency**: Users must understand what the agent is doing
* **Flexibility**: Different tools need different display strategies
* **Discoverability**: Users should easily find how to view full results
* **Consistency**: Display patterns should be predictable
* **Performance**: Rendering large results shouldn't lag the UI

---

## Considered Options

### Option 1: Uniform Truncation

**Description:** Truncate all tool results after N lines with "... (X more lines)" indicator.

**Pros:**
- Simple to implement
- Consistent behavior
- Easy to understand

**Cons:**
- One-size-fits-all doesn't work well
- Might truncate important small results
- Doesn't account for semantic importance
- Still displays large chunks of text

### Option 2: Collapsible Sections

**Description:** Display tool results in collapsible sections with expand/collapse controls.

**Pros:**
- Clean UI when collapsed
- Full detail available when expanded
- User controls verbosity

**Cons:**
- Complex state management
- Extra interaction required
- Hard to implement in terminal UI
- May hide important information by default

### Option 3: Result Overlays Only

**Description:** Show tool name inline, view results only in overlay (like diff viewer).

**Pros:**
- Very clean chat
- Full screen for result inspection
- Consistent with approval flow

**Cons:**
- Requires extra interaction for every tool
- Less transparent (hidden by default)
- Breaks conversational flow
- Annoying for small results

### Option 4: Tiered Display Strategy (Recommended)

**Description:** Different display strategies based on tool type and result size:

**Tier 1 - Loop-Breaking Tools** (task_completion, ask_question, converse):
- **Display:** Full inline (never truncate)
- **Rationale:** High semantic value, typically small, critical context

**Tier 2 - Small Operational Tools** (write_file, apply_diff < 50 lines):
- **Display:** Summary + first few lines
- **Expansion:** Keyboard shortcut to view in overlay
- **Rationale:** Balance between context and clutter

**Tier 3 - Large Operational Tools** (read_file, search_files, list_files):
- **Display:** Summary line only (e.g., "Read 245 lines from config.go")
- **Expansion:** Keyboard shortcut to view in overlay
- **Rationale:** High token count, low ongoing semantic value

**Tier 4 - Command Execution**:
- **Display:** Already uses overlay (keep as-is)
- **Rationale:** Already well-designed

**Pros:**
- Balanced approach
- Respects semantic importance
- Reduces clutter significantly
- Details available on demand
- Transparent but not overwhelming

**Cons:**
- More complex implementation
- Need to classify tools into tiers
- Requires good summary generation

---

## Decision

**Chosen Option:** Option 4 - Tiered Display Strategy

### Rationale

The tiered approach provides the best balance between transparency and usability:

1. **Preserves Important Context**: Loop-breaking tools (task_completion, etc.) are never truncated because they represent key interaction points
2. **Reduces Clutter**: Large operational tools show only summaries, dramatically reducing visual noise
3. **Maintains Transparency**: Every tool execution is visible with a clear summary
4. **Details On Demand**: Full results available via keyboard shortcut + overlay
5. **Respects Semantics**: Different tools have different display needs
6. **Aligns with ADR-0018**: Uses same tool categorization (loop-breaking vs operational)

### Display Examples

**Before (Current):**
```
💭 I'll read the configuration file to understand the current setup...

🔧 read_file
  ✓ 1 | package config
    2 |
    3 | import (
    4 |     "encoding/json"
    5 |     "fmt"
    ... (240 more lines) ...
    245 | }

💭 Now I'll search for all references to the API key...

🔧 search_files
  ✓ Found 23 matches across 8 files:
    config/settings.go:12: apiKey := os.Getenv("API_KEY")
    config/settings.go:45: if apiKey == "" {
    ... (21 more matches) ...
```

**After (Proposed):**
```
💭 I'll read the configuration file to understand the current setup...

🔧 read_file
  ✓ Read 245 lines from config/settings.go (6.8 KB) [Press Ctrl+V to view]

💭 Now I'll search for all references to the API key...

🔧 search_files  
  ✓ Found 23 matches in 8 files [Press Ctrl+V to view]

💭 Based on the configuration, I can see the API key is loaded from...

✓ Task completed: I've updated the API key handling to use the new...
```

---

## Consequences

### Positive

- **Dramatic Clutter Reduction**: Chat becomes ~70-90% shorter in typical coding sessions
- **Better Scannability**: Users can quickly scan agent actions without scrolling through pages
- **Preserved Transparency**: Every tool execution is visible with clear summary
- **Improved Focus**: Agent thinking and messages are more prominent
- **Consistent with Existing Patterns**: Uses overlay system already established for diffs/commands
- **Flexible**: Users can view details when needed
- **Semantic Alignment**: Respects importance of different tool types

### Negative

- **Implementation Complexity**: Need to categorize tools and implement tier logic
- **Summary Generation**: Need good algorithms for generating summaries
- **Learning Curve**: Users need to learn Ctrl+V shortcut for viewing details
- **Potential Information Loss**: If summaries are poor, users might miss important info
- **State Management**: Need to track which results can be viewed in overlay

### Neutral

- **Changes Visual Appearance**: Chat will look very different (cleaner)
- **Keyboard Interaction**: Adds new keyboard shortcut for viewing results
- **Memory Usage**: Need to keep full results in memory for overlay viewing

---

## Implementation

### Architecture

```
TUI Model
├── Tool Result Display Logic
│   ├── Tool Classifier
│   │   ├── isLoopBreaking(toolName) -> bool
│   │   ├── getResultSize(result) -> int
│   │   └── getTier(toolName, resultSize) -> DisplayTier
│   ├── Summary Generator
│   │   ├── summarizeReadFile(result) -> string
│   │   ├── summarizeSearchFiles(result) -> string
│   │   ├── summarizeListFiles(result) -> string
│   │   └── summarizeGeneric(result) -> string
│   └── Result Cache
│       ├── Store full results for overlay viewing
│       └── Map tool call ID -> full result
└── Result Viewer Overlay (new)
    ├── Scrollable viewport for full result
    ├── Syntax highlighting (where applicable)
    └── Copy to clipboard support
```

### Display Tiers

```go
type DisplayTier int

const (
    TierFullInline DisplayTier = iota  // Loop-breaking tools
    TierSummaryWithPreview              // Small operational tools
    TierSummaryOnly                     // Large operational tools
    TierOverlayOnly                     // Command execution (existing)
)

type ToolResultDisplayStrategy struct {
    tier            DisplayTier
    summaryFunc     func(result string) string
    previewLines    int  // For TierSummaryWithPreview
}
```

### Tool Classification

**Tier 1 - Full Inline:**
- `task_completion`
- `ask_question`
- `converse`

**Tier 2 - Summary + Preview (first 3-5 lines):**
- `write_file` (if < 50 lines)
- `apply_diff` (if < 30 lines)
- Any tool result < 100 lines

**Tier 3 - Summary Only:**
- `read_file`
- `search_files`
- `list_files`
- `write_file` (if ≥ 50 lines)
- `apply_diff` (if ≥ 30 lines)
- Any tool result ≥ 100 lines

**Tier 4 - Overlay Only (existing):**
- `execute_command` (already implemented)

### Summary Templates

```go
// read_file summary
"Read {lineCount} lines from {filename} ({size}) [Press Ctrl+V to view]"

// search_files summary  
"Found {matchCount} matches in {fileCount} files [Press Ctrl+V to view]"

// list_files summary
"Listed {fileCount} files and {dirCount} directories [Press Ctrl+V to view]"

// write_file summary
"Wrote {lineCount} lines to {filename} ({size})"

// apply_diff summary
"Applied {editCount} edits to {filename}"

// Generic summary (fallback)
"{toolName} completed ({resultSize}) [Press Ctrl+V to view]"
```

### Result Viewer Overlay

```go
type ResultViewerOverlay struct {
    viewport      viewport.Model
    toolName      string
    fullResult    string
    resultType    string  // "text", "json", "xml", etc.
    syntaxHighlight bool
}

// Keyboard shortcuts:
// - j/k or ↓/↑: Scroll
// - g/G: Go to top/bottom
// - /: Search within result
// - s: Toggle syntax highlighting
// - c: Copy to clipboard
// - Esc or q: Close overlay
```

### Result Cache Configuration

```go
type TUIConfig struct {
    // ... existing config fields ...
    
    // ResultCacheSize controls how many tool results are cached
    // for overlay viewing. Default: 20
    ResultCacheSize int
}

type resultCache struct {
    results map[string]string  // toolCallID -> result
    order   []string           // LRU order
    maxSize int                // Configurable limit
}

func (rc *resultCache) store(id string, result string) {
    if len(rc.results) >= rc.maxSize {
        // Remove oldest entry
        oldest := rc.order[0]
        delete(rc.results, oldest)
        rc.order = rc.order[1:]
    }
    rc.results[id] = result
    rc.order = append(rc.order, id)
}
```

### Event Handling Enhancement

```go
// In handleAgentEvent()
case types.EventTypeToolResult:
    // Classify tool and result
    tier := classifyToolResult(event.ToolName, event.ToolOutput)
    
    switch tier {
    case TierFullInline:
        // Display full result inline (current behavior)
        formatted := formatEntry("  ✓ ", resultStr, toolStyle, m.width, false)
        m.content.WriteString(formatted)
        
    case TierSummaryWithPreview:
        // Display summary + first few lines
        summary := generateSummary(event.ToolName, event.ToolOutput)
        preview := getPreviewLines(event.ToolOutput, 3)
        formatted := formatEntry("  ✓ ", summary+"\n"+preview+"  ...", toolStyle, m.width, false)
        m.content.WriteString(formatted)
        // Cache full result
        m.resultCache.store(event.ToolCallID, event.ToolOutput)
        
    case TierSummaryOnly:
        // Display summary only
        summary := generateSummary(event.ToolName, event.ToolOutput)
        formatted := formatEntry("  ✓ ", summary, toolStyle, m.width, false)
        m.content.WriteString(formatted)
        // Cache full result
        m.resultCache.store(event.ToolCallID, event.ToolOutput)
    }
```

### Keyboard Shortcuts

**New Shortcuts:**
- `v`: View last tool result in overlay (if available)
- `Ctrl+V`: View specific tool result (shows picker)

**Existing Shortcuts (unchanged):**
- `Enter`: Send message
- `Alt+Enter`: New line in input
- `Ctrl+C` / `Esc`: Quit
- Tool approval overlays use existing shortcuts

### Visual Indicators

```
Tier 1 (Full Inline):
  ✓ Task completed successfully with the following results...
  
Tier 2 (Summary + Preview):
  ✓ Wrote 45 lines to config.go
    1 | package config
    2 | 
    3 | import "fmt"
    ... [42 more lines - press 'v' to view]
    
Tier 3 (Summary Only):
  ✓ Read 245 lines from settings.go (6.8 KB) [Press Ctrl+V to view]
  
Tier 4 (Overlay):
  ✓ Command completed (exit code: 0) [Viewing in overlay]
```

---

## Migration Path

### Phase 1: Foundation (Week 1)
- Implement tool classification system
- Add result cache to model
- Create summary generation functions

### Phase 2: Display Logic (Week 1-2)
- Update `handleAgentEvent()` for tiered display
- Implement summary formatting
- Add preview line extraction

### Phase 3: Overlay Viewer (Week 2)
- Create ResultViewerOverlay component
- Add keyboard shortcut handling
- Implement syntax highlighting

### Phase 4: Polish (Week 3)
- Add visual indicators and help text
- Implement clipboard copy
- Add search within overlay

### Phase 5: Testing & Documentation (Week 3)
- Unit tests for classification and summaries
- Integration tests for overlay workflow
- Update user documentation
- Gather user feedback

---

## Validation

### Success Metrics

- **Clutter Reduction**: Typical coding session chat is 70-90% shorter
- **Scannability**: Users can scan 50+ tool calls in one viewport
- **Transparency**: 100% of tool executions visible with summaries
- **Discoverability**: Users find Ctrl+V shortcut within first session
- **Detail Access**: <2s to view full result via overlay
- **User Satisfaction**: Positive feedback on readability improvement

### Test Scenarios

1. **Long File Read**: read_file with 500+ lines shows summary only
2. **Multiple Searches**: 5+ search_files in sequence remain scannable
3. **Mixed Tools**: Loop-breaking tools show full, operational show summary
4. **Small Results**: write_file with 10 lines shows preview
5. **Overlay Navigation**: Full result viewable, scrollable, searchable
6. **Result Cache**: 20+ cached results don't impact performance

### Monitoring

- Track which tiers are used most frequently
- Monitor overlay view count vs tool executions
- Measure chat length before/after implementation
- Collect user feedback on summary quality
- Track Ctrl+V shortcut usage patterns

---

## Related Decisions

- [ADR-0009](0009-tui-executor-design.md) - TUI Executor Design
- [ADR-0012](0012-enhanced-tui-executor.md) - Enhanced TUI with Overlays
- [ADR-0018](0018-selective-tool-call-summarization.md) - Tool Classification
- [ADR-0013](0013-streaming-command-execution.md) - Command Output Overlay

---

## References

- [Bubble Tea Viewport](https://github.com/charmbracelet/bubbles/tree/master/viewport)
- [Chroma Syntax Highlighting](https://github.com/alecthomas/chroma)
- [Lipgloss Styling](https://github.com/charmbracelet/lipgloss)
- User feedback and UX best practices

---

## Decisions on Open Questions

1. **Summary Quality**: ✅ **DECIDED**
   - **Decision**: Use template-based summaries with key metrics (line count, file count, size)
   - **Rationale**: Fast, predictable, informative. LLM summaries would be too slow and expensive.

2. **Result Cache Size**: ✅ **DECIDED**
   - **Decision**: Last 20 tool results, configurable via settings
   - **Rationale**: Covers recent session without excessive memory, allows power users to increase if needed
   - **Configuration**: Add `resultCacheSize` parameter to TUI executor config

3. **Preview Line Count**: ✅ **DECIDED**
   - **Decision**: 3-5 lines depending on terminal height
   - **Rationale**: Enough for context, not overwhelming

4. **Shortcut Discovery**: ✅ **DECIDED**
   - **Decision**: Include in summary text: "[Press Ctrl+V to view]"
   - **Rationale**: Immediate discoverability without requiring help lookup

5. **Syntax Highlighting in Overlay**: ✅ **DECIDED**
   - **Decision**: Auto-detect file type, toggle with 's' key
   - **Rationale**: Helpful for code, annoying for plain text, toggle gives user control

---

## Future Enhancements

1. **Custom Summaries**: Allow users to define custom summary templates
2. **Export Results**: Save tool results to files from overlay
3. **Result Comparison**: Compare before/after for apply_diff
4. **Smart Previews**: Use LLM to extract most relevant preview lines
5. **Result Annotations**: Allow users to annotate important results
6. **Search Across Results**: Global search across all cached results
7. **Result History**: Navigate through result history with arrow keys

---

## Notes

### Design Philosophy

This ADR follows the principle of **"transparent by default, detailed on demand"**:
- Every tool execution is visible
- Important details are shown inline
- Large details are available but not intrusive
- Users control their information density

### UX Principles

1. **Progressive Disclosure**: Show summary first, details on request
2. **Consistent Patterns**: Similar tools display similarly
3. **Clear Affordances**: Visual indicators show how to access details
4. **Keyboard-First**: All actions accessible via keyboard
5. **Semantic Respect**: Important tools get more prominent display

### Example Session Flow

```
User: "Can you refactor the authentication module?"

💭 I'll first read the current authentication code to understand the structure...

🔧 read_file
  ✓ Read 234 lines from auth/handler.go (7.2 KB) [Press Ctrl+V to view]

💭 Now I'll search for all authentication-related functions...

🔧 search_files
  ✓ Found 15 matches in 4 files [Press Ctrl+V to view]

💭 I see the issue - the authentication logic is spread across multiple files.
    I'll consolidate it into a single module with clear separation of concerns...

🔧 apply_diff
  ✓ Applied 12 edits to auth/handler.go

🔧 write_file
  ✓ Wrote 89 lines to auth/validator.go (2.3 KB)

✓ Task completed: I've refactored the authentication module into two focused files:
  - auth/handler.go: HTTP handlers for login/logout
  - auth/validator.go: Token validation and verification logic
  
  The code is now more maintainable with clear separation between HTTP concerns
  and business logic. All tests pass.
```

**Last Updated:** 2025-01-20
**Implementation Status:** Accepted - Ready for Implementation

## Acceptance Notes

All open questions have been resolved:
- ✅ Template-based summaries (fast, predictable)
- ✅ Cache last 20 results (configurable)
- ✅ 3-5 preview lines based on terminal height
- ✅ Discovery via inline "[Press Ctrl+V to view]" text
- ✅ Auto-detect file type with 's' key toggle

The proposal has been accepted and is ready for implementation following the 5-phase plan outlined above.