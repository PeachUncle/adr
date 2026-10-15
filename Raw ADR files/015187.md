# ADR-004: Use Absolute Paths for All Internal URLs

**Status:** Accepted  
**Date:** 2025-05-23

## Context

The website contains various types of internal links including navigation between pages, asset references (CSS, images, favicon), and cross-references within content. We need a consistent URL referencing strategy that works reliably across all deployment scenarios and site hierarchy levels.

Relative paths (e.g., `../style.css`, `./projects/`) can become problematic when:
- Pages exist at different directory depths
- Site structure changes during development or refactoring
- Assets need to be referenced from multiple locations
- The site is deployed to different environments or subdirectories

## Decision

We will use absolute paths (starting with "/") for all internal URLs throughout the website, including:
- Navigation links between pages
- Asset references (CSS stylesheets, images, favicon)
- Internal content links and cross-references

Examples:
- CSS: `<link rel="stylesheet" href="/style.css">`
- Navigation: `<a href="/projects/">Projects</a>`
- Images: `<img src="/raise_logo.ico" alt="RAISE Logo">`

## Rationale

* **Consistency:** Absolute paths work identically regardless of the current page's location in the site hierarchy, eliminating guesswork about relative path depth.
* **Reliability:** Prevents broken links when pages are moved, renamed, or when the site structure is refactored.
* **Maintainability:** Reduces cognitive load when updating links across the site - all paths follow the same pattern from the site root.
* **Deployment Independence:** Works correctly whether the site is deployed to a domain root or maintains compatibility with most hosting scenarios.
* **Asset Loading:** Ensures CSS, images, and other assets load correctly from any page without complex relative path calculations.
* **Future Flexibility:** Supports site restructuring and growth without requiring systematic link updates.

## Consequences

* **Positive:**
  - Predictable and reliable navigation across all pages
  - Easier to refactor site structure without breaking links  
  - Simplified mental model for developers and contributors
  - Works correctly in both development and production environments
  - Reduces testing overhead for link verification

* **Negative:**
  - Cannot browse the site locally using the `file://` protocol without a local web server
  - All URLs would need updating if the entire site were moved to a subdirectory (though this is rare for GitHub Pages)
  - Slightly longer URLs compared to relative paths, though the difference is minimal

* **Neutral:**
  - Requires consistent application across all HTML files to maintain the benefits