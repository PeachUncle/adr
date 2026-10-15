# ADR-002: Reading Mode vs. Navigation Mode

## Status

Proposed

## Context

The current Rule Bound interface is optimized entirely for navigation - users click through a hierarchy of cards to find rules. However, the 80+ pages of Riftbound rules are meant to be _read_, not just navigated. Users need:

1. **Quick reference**: Find a specific rule number quickly
2. **Contextual reading**: Understand a rule in the context of related rules
3. **Sequential reading**: Read through a section like a document
4. **Learning mode**: Study rules with connections highlighted

The current "grid of cards with chevrons" interface fails at all but quick reference.

## Options Considered

### Option A: Single Interface, Enhanced Cards

Keep the current card-based approach but enhance cards to show more content inline.

**Pros:**

- Minimal UI changes
- Consistent interface

**Cons:**

- Cards are inherently navigation-focused
- Long content doesn't fit card metaphor
- Doesn't support sequential reading

### Option B: Reading Mode Toggle

Add a "Reading Mode" that presents rules as a continuous document within a section.

**Pros:**

- Best of both worlds
- Users can choose their preferred experience
- Document-like reading for studying rules

**Cons:**

- Two UI modes to maintain
- User must understand and choose modes

### Option C: Context-Aware Display

Automatically switch between card-view (for topic headers with many children) and document-view (for rules with substantial content).

**Pros:**

- Seamless experience
- Appropriate display for each content type
- No manual mode switching

**Cons:**

- Less user control
- More complex display logic
- May be surprising to users

### Option D: Hybrid - Document-First with Navigation Sidebar

Display rules as a document by default, with a collapsible navigation sidebar for jumping between sections.

**Pros:**

- Prioritizes reading experience
- Quick navigation still available
- Familiar pattern (documentation sites)

**Cons:**

- Major UI restructure
- Mobile sidebar can be challenging

## Decision

We will implement **Option B: Reading Mode Toggle** with elements of **Option C**.

The approach:

1. **Default Navigation View**: Current card-based browsing with enhancements
2. **Reading Mode Button**: Toggle to document-style view within a section
3. **Smart Defaults**: Automatically enter reading mode when viewing a topic (like "401. Exhaust") that has definitional children
4. **Visual Indicators**: Clear UI to show which mode is active

### Reading Mode Behavior

When in reading mode for a topic (e.g., "401. Exhaust"):

- Display the topic header prominently
- Show all child rules as a continuous, formatted document
- Include inline navigation (next/prev rule, jump to related)
- Collapsible sub-sections for deeply nested rules
- Sticky topic header while scrolling

### Navigation Mode Behavior (Default)

- Grid of cards for sections with many diverse children
- Preview cards showing first line of content
- Quick-scan optimized

## Consequences

### Positive

- Users can choose between navigation and reading experiences
- Document-style reading for learning/studying
- Card-based navigation for quick lookups
- Smart defaults reduce friction

### Negative

- Two display modes to implement and maintain
- Toggle UI must be discoverable but not intrusive
- State management for mode preference

### Neutral

- Mode preference could be persisted per-section
- Could add keyboard shortcut (e.g., `R` for reading mode)
- Analytics could inform default mode decisions
