# ADR 007: Keyboard Navigation Implementation

**Date**: 2025-01-27  
**Status**: Accepted  
**Deciders**: Development Team

## Context

Power users expect keyboard shortcuts for efficient PDF navigation. Preview (macOS) provides comprehensive keyboard support, and we want to match that experience. Without keyboard navigation, users must rely solely on mouse/trackpad, which slows down workflows.

## Decision

We will implement keyboard navigation with the following mappings:

| Key | Action |
|-----|--------|
| `Arrow Up` | Previous page |
| `Arrow Down` | Next page |
| `Page Up` | Previous page |
| `Page Down` | Next page |
| `Home` | First page |
| `End` | Last page |

### Implementation Details

**Event Listener Scope**: Window-level `keydown` listener in `AppContent` component

**Conditions**:
- Only active when a document is loaded
- Prevents default browser scrolling for arrow keys
- Checks page bounds before navigation

**Integration**:
- Calls `setCurrentPage()` from PDF context
- Triggers scroll-to-page behavior in PDFViewer
- Updates thumbnail sidebar highlight
- Updates toolbar page indicator

```typescript
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (!document) return

    switch (e.key) {
      case 'ArrowUp':
      case 'PageUp':
        if (currentPage > 1) {
          e.preventDefault()
          setCurrentPage(currentPage - 1)
        }
        break
      // ... more cases
    }
  }

  window.addEventListener('keydown', handleKeyDown)
  return () => window.removeEventListener('keydown', handleKeyDown)
}, [document, currentPage, setCurrentPage])
```

## Alternatives Considered

### 1. Component-Level Event Listeners
**Pros**: Scoped to specific components
**Cons**: Requires focus management, easy to lose focus
**Rejected**: Window-level is more reliable for global shortcuts

### 2. Arrow Keys for Scrolling, Space for Page Navigation
**Pros**: Matches browser behavior
**Cons**: Less intuitive for document navigation, conflicts with zoom/pan
**Rejected**: Doesn't match Preview UX

### 3. Vim-Style Navigation (j/k)
**Pros**: Popular with developers
**Cons**: Unintuitive for general users, conflicts with text input
**Rejected**: Arrow keys are more universal

### 4. Keyboard Shortcuts Library (e.g., react-hotkeys)
**Pros**: Handles edge cases, provides key binding UI
**Cons**: Additional dependency, overkill for simple navigation
**Rejected**: Native event listeners sufficient for our needs

## Consequences

### Positive
- ✅ Matches Preview (macOS) keyboard behavior
- ✅ Improves efficiency for power users
- ✅ No additional dependencies
- ✅ Works consistently across the application
- ✅ Integrates seamlessly with programmatic navigation

### Negative
- ⚠️ Prevents default arrow key scrolling (by design)
- ⚠️ Could conflict with future features (text input, annotations)
- ⚠️ No visual indication of available shortcuts

### Neutral
- 🔄 Must coordinate with scroll behavior (handled via isUserScrollingRef)
- 🔄 Requires document to be loaded

## Future Considerations

### Phase 2 (Search)
When search is implemented, we'll need to add:
- `Cmd/Ctrl+F`: Open search
- `Cmd/Ctrl+G` / `F3`: Find next
- `Cmd/Ctrl+Shift+G` / `Shift+F3`: Find previous
- `Escape`: Close search

**Conflict Resolution**: Search shortcuts will take precedence when search is active.

### Phase 3 (Annotations)
When markup tools are active, arrow keys may need different behavior:
- Move selected annotation
- Adjust shape size
- Navigate between annotations

**Conflict Resolution**: Mode-based behavior - navigation keys work differently in "markup mode" vs "view mode".

### Phase 7 (Accessibility)
We'll need to add:
- Tab navigation for interactive elements
- Focus indicators for current element
- Screen reader announcements for page changes
- Keyboard shortcut help modal (`?` key)

## Mitigation Strategies

**Conflict with Future Text Input**:
- Check `e.target` to avoid capturing keys in input/textarea elements
- Example: `if (e.target instanceof HTMLInputElement) return`

**Visual Discoverability**:
- Add keyboard shortcut hints to toolbar tooltips
- Consider future keyboard shortcuts modal (Phase 7)

**Browser Scroll Prevention**:
- Only prevent default when navigation actually occurs
- Respects page bounds (no preventDefault if already at first/last page)

## Testing Strategy

**Manual Tests**:
- [ ] Arrow keys navigate pages when document loaded
- [ ] Arrow keys do nothing when no document loaded
- [ ] Home/End jump to first/last page
- [ ] Page Up/Down navigate pages
- [ ] No action when already at bounds
- [ ] Smooth scroll animation occurs
- [ ] Thumbnail sidebar highlights update
- [ ] Toolbar page number updates

**Edge Cases**:
- [ ] Rapid key presses don't cause conflicts
- [ ] Works during/after zoom changes
- [ ] Works with sidebar open/closed
- [ ] Works on single-page documents

## Performance Impact

Negligible - event listeners are lightweight, and navigation logic is already optimized for programmatic navigation.

## References

- Preview (macOS) - Keyboard shortcut reference
- Adobe Acrobat - Alternative keyboard patterns
- [Web Accessibility Guidelines - Keyboard Navigation](https://www.w3.org/WAI/WCAG21/Understanding/keyboard.html)

## Notes

This implementation provides a foundation for Phase 7 (Keyboard & Accessibility). The architecture is extensible to support additional shortcuts without refactoring.

When adding future shortcuts:
1. Document in PRD and this ADR
2. Add to keyboard help modal
3. Test for conflicts with existing shortcuts
4. Consider modifier keys (Cmd/Ctrl, Shift, Alt) for advanced features
