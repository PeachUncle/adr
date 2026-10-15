# ADR 03: ImageData and thumbExtractor

## Status

Implemented

## Context

In FY2026-27 the Readers Growth team is working on an Image Browsing
experiment which somewhat overlaps with current functionality in
MultimediaViewer and MobileFrontend in extracting a list of interesting
images from the current page and providing ways to browse through them.

The frontend is using modern Codex tokens and Vue components, making
direct calls into MultimediaViewer with its old OOUI/jQuery code
awkward.

We need a quick modern implementation whose results can easily be sent
into a Vue application for rendering, but which is compatible with
existing conventions for which images should be excluded from viewer
tools.

## Decision

A one-off port of MMV's selectors was made, with local customizations,
returning a list of objects which are friendly to sending into Vue
components.

An object type description is provided in our `types.d.ts` file to aid
in IDE autocomplete and static analysis.

## Consequences

`thumbExtractor.js` contains this logic, with adapted selectors from
MMV for inclusions and exclusions using modern DOM methods, returning a
list of objects with plain-old string and number properties plus a
couple of DOM object references for when they're needed (eg, to scroll
to a live object position).

### Data types

This `ImageData` type structure is defined in TypeScript style in our
`types.d.ts` file to aid in IDE type hinting and other static analysis
tools.

Note this definition could get out of sync with `thumbExtractor.js` due
to them being separate files in separate syntax. When updating the
extractor and changing the return types, be sure to update the type
definitions.

The object structure is meant to be ad-hoc and private to the
experiment; if we need a more permanent version refactoring common code
with MultimediaViewer to production quality might be useful later with
a fixed definition for use in multiple places.

### Extraction logic

The extraction is oriented around looking for `<figure><img>` etc with
the proper MediaWiki structure on them, and identifying the image and
its base attributes (even if it's been nerfed for lazy loading),
looking for alt text and caption if present.

This matches MMV's patterns -- directly porting some of its logic to
local copies -- but adds a custom exclusion for SVGs in infoboxes,
which we  are provisionally excluding as a test.

Important bits in thumbExtract.js:

* `extensions` list is used to allow-list files with base name with
  known file types and should match MMV's `MediaViewerExtensions`
  config array. For now this is a static copy.
* `thumbInfo()` performs the internal logic of extracting data from an
  `<img>` (or a `<span>` with a lazy-loadable image). This finds some
  DOM objects (`thumb`, `link`, `container`, and `caption`) and some
  primitive data (`width`, `height`, `src`, `srcset`, `alt`) as a nice
  `ImageData` object.
* `extractThumbInfo()` is the exported call function, which takes a DOM
  object for a content area and searches it for matching images.
* `isAllowedThumb()` controls the main exclusions, checking for parent
  elements matching a list of selectors copied from MMV. This can be
  extended to easily exclude any particular parent, such as tables or
  something with a class or id.
* `isIncludedThumbInfo()` implements top-level inclusions/exclusion
  checks, some copied from MMV and some added here. Custom logic in
  ReaderExperiments should appear here to distinguish from shared logic
  in `isAllowedThumb()`.
* `getCaptionIfAvailable` pulls the caption HTML if present from the
  container. This is also exported, and may be refined to match needs.

Check the doc comments for each function for details on where selectors
are taken from or if they're custom.

The entire list can be passed into Vue components for list rendering,
or individual `ImageData` objects can be passed one at a time, as in
the detail component.
