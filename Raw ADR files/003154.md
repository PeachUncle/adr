# ADR: Text Highlighter Implementation Architecture

## Status
Accepted

## Context
We needed to implement a text highlighter feature for the Physical AI & Humanoid Robotics book documentation. The feature should allow users to select text, highlight it with different colors, persist the highlights across sessions, and provide a way to manage all highlights across pages.

## Decision
We decided to implement the text highlighter using the following architectural approach:

1. **Client-Side Persistence**: Use localStorage to store highlights instead of a server-side solution
   - Rationale: Simpler implementation, no backend requirements, works offline
   - Trade-offs: Data is tied to browser, limited storage space, no cross-device sync

2. **DOM Manipulation Approach**: Wrap selected text in `<span>` elements with specific classes instead of CSS-only approaches
   - Rationale: Provides full control over highlighting, allows for rich interactions
   - Trade-offs: More complex DOM manipulation, potential for conflicts with other DOM changes

3. **Custom Implementation**: Build a custom solution instead of using existing libraries
   - Rationale: Full control over features, no external dependencies, tailored to specific requirements
   - Trade-offs: More development time, potential for bugs, maintenance responsibility

4. **TreeWalker for Restoration**: Use TreeWalker API to restore highlights instead of storing position information
   - Rationale: More robust to content changes, doesn't rely on fragile position data
   - Trade-offs: More complex restoration logic, potential performance impact on large documents

## Alternatives Considered

### Server-Side Storage
- Store highlights on the backend with user accounts
- Pros: Cross-device sync, unlimited storage, data backup
- Cons: Requires user accounts, backend infrastructure, privacy concerns

### CSS-Only Approach
- Use CSS to highlight text without DOM manipulation
- Pros: Simpler, less DOM changes
- Cons: Limited functionality, harder to persist, less interactive

### Existing Libraries
- Use libraries like Medium.js or similar
- Pros: Faster implementation, proven solutions
- Cons: Larger bundle size, less control, potential feature mismatches

## Consequences

### Positive
- Full control over the feature implementation
- No external dependencies
- Works offline
- Rich interactive features
- Tailored to specific requirements

### Negative
- More complex implementation
- DOM manipulation complexity
- LocalStorage limitations
- Potential performance considerations on large documents
- Maintenance responsibility

## Implementation Notes

The solution was implemented across multiple components:
- TextHighlighter: Core highlighting functionality
- MyHighlights: Sidebar for managing all highlights
- Highlighter: Combined component
- Integration with existing Chatbot component

## Date
2025-12-21

## Authors
Claude Sonnet 4.5