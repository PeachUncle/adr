# ADR-001: Pure Blazor Server Architecture

## Status
Accepted

## Context
The WitchCityRope application was initially developed with a hybrid Razor Pages + Blazor Server architecture. This hybrid approach caused several critical issues:

1. **Render Mode Conflicts**: Mixing Razor Pages and Blazor components led to unpredictable render mode behavior
2. **Layout/CSS Issues**: Razor Pages layouts conflicted with Blazor component styling
3. **Authentication Complexity**: Managing authentication state between Razor Pages and Blazor components was problematic
4. **Antiforgery Token Issues**: Hybrid architecture made proper token handling difficult
5. **Developer Confusion**: Two different paradigms in one application increased complexity

## Decision
We migrated the entire application to use **Pure Blazor Server** architecture, eliminating all Razor Pages.

### Implementation Details
- Removed all `.cshtml` files (Razor Pages)
- Removed `AddRazorPages()` and `MapRazorPages()` from Program.cs
- Migrated to `App.razor` as the root HTML document
- All pages are now Blazor components (`.razor` files)
- Use `@rendermode="InteractiveServer"` for interactive pages
- Configure with `MapRazorComponents<App>().AddInteractiveServerRenderMode()`

## Consequences

### Positive
1. **Consistent Architecture**: Single paradigm throughout the application
2. **Simplified Render Modes**: Interactive modes work properly without conflicts
3. **Better Authentication**: Authentication state flows correctly through components
4. **Easier Maintenance**: Developers only need to understand Blazor patterns
5. **Improved Performance**: Eliminated overhead of mixing technologies
6. **Native Blazor Features**: Can fully leverage Blazor Server capabilities

### Negative
1. **Migration Effort**: Required converting all existing Razor Pages
2. **Learning Curve**: Developers familiar with Razor Pages need to learn Blazor patterns
3. **SEO Limitations**: Pure Blazor Server has different SEO characteristics than Razor Pages

### Mitigation
- Created comprehensive documentation for Blazor Server patterns
- Established clear component structure guidelines
- Implemented validation scripts to prevent Razor Pages creation

## Verification
The migration has been verified successful with:
- HTML Structure: Complete with head, title, CSS, scripts (20 head children)
- Layout System: Working properly without hybrid issues
- Blazor Server: Fully functional with interactive components
- Authentication: Login working with proper redirects
- Antiforgery Tokens: Automatic handling working correctly
- CSS Loading: All stylesheets loading properly

## References
- [Microsoft Blazor Server Documentation](https://docs.microsoft.com/blazor)
- [Blazor Render Modes](https://docs.microsoft.com/aspnet/core/blazor/components/render-modes)
- Internal discussion threads on architecture issues