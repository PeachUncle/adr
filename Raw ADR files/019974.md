---
status: 'accepted'
date: 2025-07-09
decision-makers: voder.ai website team
---

# ADR 0007: Use vite-plugin-inline-source for Critical CSS Inlining

## Context and Problem Statement

The Voder.ai pre-launch site currently loads its global stylesheet (`style.css`) synchronously, blocking rendering and delaying the First Contentful Paint (FCP). Lighthouse CI reports FCP above our 1500 ms budget, and render-blocking CSS has been identified as a primary culprit.

## Decision Drivers

- Meet performance budgets for First Contentful Paint (≤ 1500 ms)
- Minimize CI build time and complexity
- Automate critical CSS extraction without manual maintenance overhead
- Leverage a well-maintained, community-supported plugin for inlining

## Considered Options

- Critters (deprecated): upstream Critters plugin for critical CSS inlining
- Beasties: an actively maintained fork of Critters that inlines critical CSS without a headless browser
- vite-plugin-inline-source: simpler CSS inlining solution with base64 encoding
- Manual inlining: hand-craft critical CSS rules in `<style>` tags (brittle and high maintenance)

## Decision Outcome

**Initially chosen**: Beasties via `vite-plugin-beasties`
**Final choice**: **vite-plugin-inline-source**

**Reason for change**: During implementation, `vite-plugin-beasties` encountered persistent errors (`TypeError: Cannot read properties of undefined (reading 'replace')`) indicating the plugin was trying to process undefined CSS content. Multiple debugging attempts and configuration changes failed to resolve the issue.

**vite-plugin-inline-source** was chosen as the replacement because:

- Resolves the undefined CSS processing errors completely
- Provides reliable CSS inlining with base64 encoding
- Uses modern performance techniques (media="print" with onload switching)
- Maintains external CSS files as fallbacks
- Integrates seamlessly with Vite build process

### Consequences

- **Positive**: Clean builds with no errors; improved FCP through critical CSS inlining; non-critical CSS loaded efficiently via base64 data URLs
- **Negative**: Different inlining approach than originally planned; uses base64 encoding instead of selective critical CSS extraction

## Confirmation

- Verify FCP drops below 1500 ms in Lighthouse CI (`npm run assert:lhci`).
- Confirm critical CSS is inlined in production HTML and non-critical CSS is deferred via base64 data URLs.
- Measure CI build times to ensure no build errors or processing delays.

## Implementation Details

**Issue encountered with Beasties (2025-07-15):**

```text
vite-plugin-beasties error: TypeError: Cannot read properties of undefined (reading 'replace')
```

This error persisted despite multiple configuration attempts, indicating the plugin was trying to process undefined CSS content during the build process.

**Solution implemented:**

- Removed `vite-plugin-beasties`
- Installed `vite-plugin-inline-source`
- Simple configuration: `inlineSource()` with no additional options
- Result: Clean builds with CSS inlining via base64 data URLs

## Pros and Cons of the Options

### Critters (deprecated)

- Good: Originally designed for critical CSS inlining.
- Bad: No longer actively maintained; limited compatibility with modern build tools.

### Beasties (attempted)

- Good: Fast, headless-browser–free critical CSS inlining; integrates with Vite via `vite-plugin-beasties`.
- Good: Automatically prunes unused CSS and supports font inlining/preloading.
- **Bad: Encountered undefined CSS processing errors that could not be resolved**
- Bad: New dependency to manage; may require configuration tweaks.

### vite-plugin-inline-source (final choice)

- Good: Reliable CSS inlining without processing errors
- Good: Uses modern performance techniques (base64 data URLs with smart loading)
- Good: Maintains external CSS files as fallbacks
- Good: Simple configuration with minimal maintenance
- Neutral: Uses base64 encoding rather than selective critical CSS extraction

### Manual inlining

- Good: Full control over which CSS rules are critical.
- Bad: High maintenance overhead; fragile as CSS grows and changes.

## More Information

- [vite-plugin-inline-source documentation](https://www.npmjs.com/package/vite-plugin-inline-source)
- [Beasties documentation](https://github.com/danielroe/beasties) (attempted but failed)
- [Original Vite plugin for Beasties](https://www.npmjs.com/package/vite-plugin-beasties) (problematic)
