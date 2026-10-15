# ADR-005: Website Redesign Architecture

> **Scope**: Decision to implement Claude Code-inspired design system with unified user profile management and improved RAG functionality.

- **Status:** Accepted
- **Date:** 2025-11-30
- **Feature:** 005-website-redesign-and-ui-improvements
- **Context:** The Physical AI textbook website had a basic Docusaurus template appearance, broken RAG functionality, and scattered user management components.

## Decision

Implement a comprehensive website redesign with the following architectural decisions:

### 1. Design System: Warm Color Palette with CSS Custom Properties

```css
:root {
  --ifm-color-primary: #c9a87c;
  --ifm-background-color: #faf9f7;
  --ifm-font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
  --ifm-line-height-base: 1.65;
}
```

**Rationale**: 
- Warm colors create welcoming learning environment
- CSS custom properties enable easy theming and dark mode
- System font stack ensures fast loading and native feel

### 2. Unified User Profile Component

Replace scattered auth button and theme toggle with single `UserProfileButton` component.

```typescript
// UserProfileButton.tsx
const UserProfileButton = () => {
  return (
    <div className={styles.profileContainer}>
      <button onClick={toggleDropdown}>
        <Avatar user={user} />
      </button>
      <Dropdown>
        <ThemeToggle />
        <ProfileEdit />
        <GitHubLink />
        <AuthActions />
      </Dropdown>
    </div>
  );
};
```

**Rationale**:
- Reduces navbar clutter
- Centralizes user management
- Improves mobile experience
- Follows modern UI patterns

### 3. Pre-Fetch RAG Context Architecture

Instead of using function tools for retrieval, pre-fetch context before LLM calls.

```python
# agent_service.py
async def chat_stream(self, user_message, ...):
    # Pre-fetch context
    textbook_context = self._search_textbook(search_query)
    user_context = self._get_user_context(user_id)
    
    # Build system prompt with context
    system_prompt = self._get_system_prompt(
        textbook_context, user_context, current_page
    )
    
    # Run agent with pre-loaded context
    result = await Runner.run(agent, input=user_message)
```

**Rationale**:
- Ensures reliable retrieval (no tool call failures)
- Reduces latency (parallel context fetching)
- Simpler debugging (context visible in prompt)

### 4. Semantic Document Chunking

Replace header-based splitting with semantic chunking (200-2000 chars).

**Rationale**:
- Larger chunks provide better context
- Reduced from 101 tiny chunks to 22 meaningful chunks
- Better search relevance

### 5. Resizable Chat Panel

Three size presets (S/M/L) with smooth CSS transitions.

**Rationale**:
- Users need different sizes for different tasks
- Smooth transitions enhance UX
- Mobile-responsive by default

## Consequences

### Positive

- **Professional Appearance**: Modern, trustworthy design
- **Improved UX**: Unified navigation, better mobile experience
- **Reliable RAG**: Consistent vector retrieval
- **Maintainability**: Clean component architecture
- **Performance**: Optimized chunking and caching

### Negative

- **Complexity**: More sophisticated codebase
- **Migration Effort**: Required re-ingesting all documents
- **Learning Curve**: New design patterns

## Alternatives Considered

### Alternative 1: Keep Default Docusaurus Theme
**Why rejected**: Poor user experience, unprofessional appearance

### Alternative 2: Use Third-Party Theme
**Why rejected**: Less control, potential compatibility issues

### Alternative 3: Function Tools for RAG
**Why rejected**: Less reliable, added latency from tool calls

### Alternative 4: Keep Separate Auth/Theme Components
**Why rejected**: Cluttered navbar, poor mobile experience

## References

- Feature Spec: specs/005-website-redesign-and-ui-improvements/spec.md
- Implementation Plan: specs/005-website-redesign-and-ui-improvements/plan.md
- Related ADRs: history/adr/004-rag-function-tools.md
- Docusaurus Theming: https://docusaurus.io/docs/styling-layout
