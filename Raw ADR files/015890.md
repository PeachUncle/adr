# ADR-004: Rule Connections and Cross-References

## Status

Proposed

## Context

Riftbound rules frequently reference other rules:

- "See rule 346. Playing Cards for more information."
- Cross-reference arrays in the data (`crossRefs: ["346"]`)
- Implicit connections (rules about the same game concept)

Currently, cross-references are displayed as a "See Also" section at the bottom of a rule detail page. This is:

1. Easy to miss
2. Out of context
3. Doesn't show the relationship type
4. Doesn't show inline references within rule text

Users learning the game need to understand how rules connect to build a mental model.

## Options Considered

### Option A: Enhanced Cross-Reference Section

Keep cross-refs at the bottom but make them more prominent:

- Grouped by relationship type
- Preview of referenced rule content
- Two-way linking (also shows "Referenced By")

**Pros:**

- Minimal change to existing UI
- Non-intrusive

**Cons:**

- Still easy to miss
- Doesn't help with inline references

### Option B: Inline Cross-Reference Links

Parse rule content for rule number patterns (e.g., "rule 346") and make them clickable links.

**Pros:**

- Discoverable where users naturally read
- Contextual

**Cons:**

- Requires content parsing
- May have false positives
- Changes reading flow

### Option C: Contextual Sidebar

Show related rules in a sidebar when viewing a rule:

- Parent rule context
- Sibling rules
- Cross-referenced rules
- Rules that reference this one

**Pros:**

- Rich contextual information
- Always visible

**Cons:**

- Takes screen real estate
- Complex on mobile

### Option D: Progressive Disclosure with Hover/Tap

Inline links for rule references that show a preview on hover/tap before navigating.

**Pros:**

- Contextual without leaving current rule
- Progressive disclosure
- Works inline

**Cons:**

- More complex interaction
- Mobile hover doesn't exist (needs tap variant)

## Decision

We will implement **a combination of Options B and D**: Inline cross-reference links with preview tooltips.

### Implementation Approach

#### 1. Content Parsing

Parse rule content to find rule number references:

- Pattern: `rule \d+\.?(\d+\.?)*` (e.g., "rule 346", "rule 103.2.b")
- Pattern: `See (\d+\.)+` (e.g., "See 346.")
- Pattern: Rule numbers in parentheses `\((\d+\.)+\)`

Convert matches to interactive links.

#### 2. Inline Links

- Style: `text-primary-600 underline hover:text-primary-700`
- Accessible: Proper link text, not just the number
- Example: "See rule [346. Playing Cards]" (linked)

#### 3. Preview Tooltip/Popover

On hover (desktop) or tap (mobile):

- Show popover with:
  - Rule number and title
  - First 2-3 lines of content
  - "Go to rule" action button
- Accessible: Can be keyboard-triggered, dismissable with Escape
- Position: Smart positioning to avoid screen edges

#### 4. Cross-Reference Section Enhancement

Keep the "See Also" section but enhance:

- Group by: "Related Topics" (same parent), "References" (explicit crossRefs), "Referenced By" (backlinks)
- Show rule type badges
- Preview content on hover

### Mobile Considerations

- Hover becomes tap-to-preview
- Second tap navigates to rule
- Clear "X" to dismiss popover
- Popover sized for mobile viewport

## Consequences

### Positive

- Rules feel connected, not isolated
- Natural discovery of related content
- Helps users build mental model of rules
- Accessible (keyboard navigation, screen reader support)

### Negative

- Content parsing adds complexity
- Popovers can be finicky on mobile
- May have false positive matches in content

### Neutral

- Need to test parsing against full dataset
- May want to add user setting to disable popovers
- Consider caching parsed content for performance
