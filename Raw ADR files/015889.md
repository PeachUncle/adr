# ADR-003: Visual Hierarchy and Content Presentation

## Status

Proposed

## Context

The current interface treats all rules visually the same - a card with a number, title, and chevron. This fails to communicate:

1. **Rule Type**: Is this a section header, topic header, or actual rule content?
2. **Content Depth**: How much content is behind this rule?
3. **Importance**: Is this a core concept or a minor clarification?
4. **Relationships**: How does this rule connect to others?

Users scanning 80+ pages of rules need immediate visual cues to understand what they're looking at.

## Design Principles

1. **Scanability**: Users should understand page structure at a glance
2. **Hierarchy**: Visual weight should match content importance
3. **Differentiation**: Different content types look different
4. **Consistency**: Same content type always looks the same
5. **Accessibility**: Visual distinctions must not rely on color alone

## Options Considered

### Option A: Typography-Only Hierarchy

Use font size, weight, and spacing to distinguish rule types:

- Sections: Large, bold, full-width
- Topic headers: Medium, bold, card-style
- Definitions: Normal, with visible content
- Sub-rules: Smaller, indented

**Pros:**

- Clean, minimal design
- Accessible (no color dependency)
- Works well in reading mode

**Cons:**

- May not be distinctive enough
- Limited differentiation options

### Option B: Card Variant System

Different card styles for different content types:

- Sections: Full-bleed gradient cards
- Topic headers: Prominent cards with icon/badge
- Definitions: Content-focused cards (less chrome)
- Sub-rules: Inline or nested within parent

**Pros:**

- Clear visual distinction
- Familiar card patterns
- Flexible styling options

**Cons:**

- More visual complexity
- More variants to maintain

### Option C: Mixed Typography + Visual Markers

Combine typography hierarchy with visual markers:

- Color-coded left borders by content type
- Icons/badges for rule type
- Background treatment for headers vs. content
- Depth indicators (indentation, nesting lines)

**Pros:**

- Maximum clarity
- Multiple redundant cues (accessibility)
- Works for both navigation and reading

**Cons:**

- Most complex to implement
- Risk of visual noise

## Decision

We will implement **Option C: Mixed Typography + Visual Markers** with restraint.

### Visual System

#### 1. Section Headers (Level 0)

- **Background**: Subtle gradient (primary-50 to white)
- **Typography**: `text-3xl font-bold`
- **Border**: None (gradient provides separation)
- **Layout**: Full-width, prominent spacing above/below
- **Icon**: Category-specific icon (if applicable)

#### 2. Topic Headers (e.g., "401. Exhaust")

- **Background**: White with left border accent
- **Border**: 4px left border in primary-500
- **Typography**: `text-xl font-semibold` for number, `text-lg font-medium` for title
- **Badge**: "Topic" chip in subtle style
- **Children indicator**: "5 rules" badge
- **Behavior**: Expandable to show children OR navigate to reading view

#### 3. Definitions (Rules with Content)

- **Background**: White
- **Border**: 2px left border in primary-300
- **Typography**:
  - Number: `text-lg font-mono font-semibold`
  - Title: `text-base font-medium`
  - Content: `text-base prose` (optimized for reading)
- **Content Preview**: Show full definition text (not truncated)
- **Sub-rules**: Rendered inline with indentation

#### 4. Sub-rules (Nested Content)

- **Background**: Transparent or neutral-50
- **Border**: 1px left border in neutral-300 (continuation line)
- **Typography**:
  - Number: `text-sm font-mono`
  - Content: `text-sm`
- **Indentation**: 24px left margin from parent
- **Behavior**: Always expanded within parent definition

### Color System for Borders

Using left borders as visual anchors:

- **primary-500**: Topic headers (important concepts)
- **primary-300**: Definitions (content rules)
- **neutral-300**: Sub-rules (supporting detail)
- **primary-600**: Section headers (major divisions)

This creates a visual "timeline" when viewing rules sequentially.

### Typography Scale

| Element            | Size      | Weight        | Purpose            |
| ------------------ | --------- | ------------- | ------------------ |
| Section title      | text-3xl  | bold          | Major divisions    |
| Topic number       | text-xl   | semibold      | Concept identifier |
| Topic title        | text-lg   | medium        | Concept name       |
| Definition number  | text-lg   | semibold mono | Rule reference     |
| Definition content | text-base | normal        | Primary reading    |
| Sub-rule number    | text-sm   | medium mono   | Detail reference   |
| Sub-rule content   | text-sm   | normal        | Supporting detail  |

## Consequences

### Positive

- Clear visual hierarchy communicates content type instantly
- Typography scale supports both scanning and reading
- Left borders create cohesive visual system
- Multiple cues ensure accessibility
- System scales to any nesting depth

### Negative

- More CSS complexity
- More component variants to maintain
- Need to test against full rules dataset

### Neutral

- Existing components will need refactoring
- Design system needs documentation for future consistency
- May want to add theme support later (dark mode borders, etc.)
