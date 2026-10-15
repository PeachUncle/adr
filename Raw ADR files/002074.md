# ADR-0006: Chat Interface Embedding Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-19
- **Feature:** chatkit-rag
- **Context:** Need to integrate Chatkit UI components into the Docusaurus layout in a way that's accessible from all pages without disrupting the reading experience of the Physical AI Book.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Implement the Chatkit UI as:
- **Desktop**: Persistent sidebar on wider screens for constant accessibility
- **Mobile**: Collapsible floating button that expands to full chat interface
- **Integration**: Embedded within Docusaurus layout to maintain consistent user experience
- **Positioning**: Non-intrusive placement that doesn't compete with main content

## Consequences

### Positive

- Chat interface accessible from all pages without navigation away from content
- Maintains reading flow while providing immediate assistance
- Responsive design that adapts to different screen sizes
- Consistent with modern web application patterns
- Doesn't compete with footer or header navigation elements

### Negative

- Sidebar may reduce content width on wider screens
- Floating button may obscure content on mobile devices
- Additional complexity in layout management
- Potential conflicts with existing Docusaurus components
- Possible performance impact from always-present chat components

## Alternatives Considered

Alternative Strategy A: Dedicated chat page
- Pros: Simpler implementation, no layout conflicts
- Cons: Requires navigation away from content, reduces accessibility, breaks reading flow

Alternative Strategy B: Overlay modal
- Pros: Doesn't permanently alter layout
- Cons: Disruptive to reading experience, may be dismissed accidentally

Alternative Strategy C: Fixed bottom widget
- Pros: Always accessible
- Cons: Competes with footer content, may interfere with page navigation

## References

- Feature Spec: ../../specs/5-chatkit-rag/spec.md
- Implementation Plan: ../../specs/5-chatkit-rag/plan.md
- Research Document: ../../specs/5-chatkit-rag/research.md
- Evaluator Evidence: ../../history/prompts/chatkit-rag/002-create-implementation-plan.plan.prompt.md