# 4. Ordered module contents

Date: 2023-06-24

## Status

Accepted

## Context

When rendering a module into a single file output, the order of the contents is important for reading.

While there are multiple ways to tackle this, all of them have significant drawbacks.

The main options are:

- Define the rendering order in the content pieces
- Define the rendering order elsewhere, creating a sorted list of identifiers
- Use "natural" (like alphabetical) ordering when rendering
- Do not render to a single file, leaving the responsibility to index and order the contents to another tool/mechanism.

Unfortunately, the first two options suffer from a weakness of [JSON merge-patch](./0002-merge-json-modules.md). Merging modules would mean any property that stored a list (an `array`) of identifiers in order, would be overwritten by the property of the merged module. While this *could* be worked around by creating "ordering patches", this would quickly get out of hand, as a new patch would be needed for all combinations of modules.

The last option, while technically easier, forces the users to create their own solutions for this purpose. This is not ideal, as would raise the barrier of entrance to the ecosystem, and would require writers to basically recreate the "ordering patches" for all combinations of modules possible.

Ordering the contents by their identifiers is the only option that does not suffer when merging contents, but the results are **never** ideal when rendering contents. The workaround required for creating sane ordering means writers will likely nest their contents in ordered directories (`1`, `2`, `3`; or `a`, `b`, `c`) to create nested identifiers that preserve ordering. This, unfortunately, pollutes the identifiers with the rendering order logic.

## Decision

The simplest mechanism is to rely on the natural ordering of the contents when rendering.

While this doesn't guarantee optimal reading order for outputs, it does allow for quick prototyping and preserves logical groupings based on nested folder structures.

## Consequences

Module creators will be force to use identifiers for their contents that are sorted in the same order as they should be rendered.

Since, there is no quick way to reorder specific pieces of content, so merging modules risks nonsensical results being created.