
# 1. Handle styling within the tools gem wherever possible

Date: 2025-11-26

## Status

Accepted

## Context

The `content_block_tools` gem provides reusable content blocks (such as contact blocks) that are rendered across 
multiple frontend applications in the GOV.UK publishing platform.

When we introduced contact blocks, we realised that there was a decent amount of styling that we needed to add to get
the contact block to render correctly.

After much back and forth, we decided to ship the styles within the 
[`govuk_publishing_components`](https://github.com/alphagov/govuk_publishing_components/) gem.

This was because we felt that it was the most appropriate place for the styling to live, as all frontend apps already
depend on it, ensuring consistent styling across applications.

However, since we first shipped the contact block, we've made some changes to the structure of the block, and it is now
much simpler, meaning we can revisit our original decision.

### Problems with the Current Approach

- Changes to content blocks require coordinated releases of two separate gems
- Content blocks are conceptually different from reusable UI components, making their inclusion in the components gem 
somewhat awkward
- The components gem accumulates styling code that is specific to content blocks rather than general-purpose components

## Decision

We will handle styling for content blocks within the `content_block_tools` gem wherever possible, rather than in 
the `govuk_publishing_components` gem.

Our approach will follow this priority order:

1. **First preference**: Use GOV.UK Frontend override classes to style our content blocks, such as:
    - [Font override classes](https://design-system.service.gov.uk/styles/font-override-classes/)
    - [Spacing override classes](https://design-system.service.gov.uk/styles/spacing/#overriding-spacing)

2. **When override classes are insufficient**: Add small, generic utility classes to the `govuk_publishing_components` 
gem that are not specific to any particular block type.

   For example: All lists within a `.govspeak` wrapper are styled with bullet points in the components gem. Since we 
   don't want this in content blocks, we will add a generic `.list-no-bullet` class to the component gem, which can be 
   used by content blocks and potentially other use cases.

## Consequences

- **Faster iteration**: We do not have to wait for two gems to be released when a change is made to a block
- **Better separation of concerns**: Content block styling lives with content block logic
- **Simpler components gem**: We can remove content-block-specific styles from the components gem, reducing noise and 
maintaining clearer boundaries
- **Encourages consistency**: This approach forces us to think carefully about the styling of our content blocks, 
ensuring any custom styling is minimal and consistent with the rest of GOV.UK

### Migration Required

- Remove existing content block styles from `govuk_publishing_components` gem
- Refactor contact block to use override classes where possible
- Document the styling approach for future content block implementations
