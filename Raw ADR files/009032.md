# ADR-063: HTML Links vs Blazor Navigation Workaround

**Status:** ⚠️ Accepted (Temporary Workaround)  
**Date:** October 2025  
**Context:** Blazor Server Navigation Reliability

## Context

Blazor Server uses SignalR for all UI updates and navigation. During development, we encountered:

- Intermittent navigation failures when SignalR circuit was stressed
- Navigation hung when LLM calls took too long (20-25s for Ollama)
- Browser back button sometimes didn't work
- Connection timeouts during long assessments

Blazor's `NavigationManager.NavigateTo()` depends on active SignalR connection.

## Decision

Implemented **HTML anchor links** (`<a href>`) as fallback for critical navigation paths when SignalR is unreliable.

## Rationale

1. **Reliability**: HTML links work even if SignalR circuit breaks
2. **Browser Native**: Back button works correctly
3. **Performance**: No SignalR roundtrip for navigation
4. **User Experience**: Navigation never "hangs"
5. **Temporary**: Can revert once SignalR reliability improves

## Consequences

### Positive

- **100% reliable navigation**: Never fails due to SignalR issues
- **Faster**: No server roundtrip for navigation
- **Better UX**: Back button works as expected
- **Simple**: Standard HTML, no special handling

### Negative

- **Full page reload**: Loses interactive component state
- **Not idiomatic Blazor**: Blazor prefers NavigationManager
- **Debugging confusion**: Mixed navigation patterns
- **Future maintenance**: May need to revert later

### Risks Mitigated

- Only used for critical paths (post-assessment navigation)
- Still use NavigationManager for non-critical navigation
- Documented as temporary workaround
- Tests cover both navigation patterns

## Implementation

**Before** (NavigationManager, could hang):

```razor
@inject NavigationManager Navigation

<button @onclick="NavigateToResults">View Results</button>

@code {
    private void NavigateToResults()
    {
        // Problem: Can hang if SignalR circuit is busy/broken
        Navigation.NavigateTo($"/student/assessment/{assessmentId}/results");
    }
}
```

**After** (HTML link, always works):

```razor
<a href="/student/assessment/@assessmentId/results" 
   class="btn btn-primary">
    View Results
</a>
```

## When to Use Each Pattern

**Use HTML Links (`<a href>`)** for:

- Post-assessment navigation (critical path)
- Inter-page navigation (different sections)
- Navigation during long-running operations
- Error recovery navigation

**Use NavigationManager** for:

- Internal component navigation (tabs, modals)
- Programmatic navigation after successful operation
- Navigation with query string manipulation
- When preserving component state is critical

## Alternative Considered: Improve SignalR Reliability

**Attempted** but not fully successful:

- Increased circuit timeout (4 hours)
- Configured circuit handler for reconnection
- Added Redis backplane for state sharing
- Still had intermittent issues with long LLM calls

**Why HTML links were chosen**:

- Simpler immediate fix
- 100% reliable
- Buys time to investigate SignalR issues properly
- Easy to revert later

## Future Plan

This is marked as **temporary workaround**. Future improvements:

1. Investigate SignalR circuit stress under LLM load
2. Consider offloading LLM calls to background job (Azure Functions)
3. Implement better circuit reconnection logic
4. Revert to NavigationManager once reliability proven

## User Impact

Users see:

- **Before**: Loading spinner sometimes hung during navigation
- **After**: Instant navigation, small page reload flash

Trade-off accepted: Page reload is better than hung navigation.

## Related Decisions

- ADR-002: Blazor Server for Student App
- ADR-006: Redis for Caching Layer (SignalR backplane)
- ADR-004: Ollama for Local LLM (20-25s calls stress SignalR)

## References

- `src/AcademicAssessment.StudentApp/Pages/` - Navigation implementation
- GitHub issue: Navigation hanging during long assessments
- Commit: `ef219b5` - "feat(student-ui): Complete Week 2 Student Assessment UI"
