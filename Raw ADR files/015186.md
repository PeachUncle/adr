# ADR-003: Use Plain HTML5 and Minimal CSS for Initial Website

**Status:** Accepted  
**Date:** 2025-05-15

## Context

We need to publish the RAISE Manifesto as a simple, accessible, single-page website. The primary goal is to present the manifesto text clearly and allow for future inclusion of related sections like "Who We Are," "What's Next," and discussion links.

Consideration was given to using a Static Site Generator (SSG) like Jekyll for potential ease of content updates (e.g., writing in Markdown). However, for the initial launch and the defined scope of a single-page site with relatively static supplemental sections, the added complexity of an SSG setup (even one as integrated as Jekyll with GitHub Pages) might be unnecessary.

## Decision

We will build the initial RAISE Manifesto website using plain HTML5 for structure and content, and a minimal set of custom CSS rules to achieve the defined design goals (typography, layout, color scheme).

No client-side JavaScript will be used for the initial version, unless an explicit future requirement for dynamic behavior cannot be met otherwise and is deemed essential.

## Rationale

*   **Simplicity:** This approach is the most straightforward and directly aligns with the RAISE value of simplicity. It avoids introducing any new tools, build steps, or abstractions beyond the fundamental web technologies.
*   **Minimalism:** For a single-page site with limited interactivity, HTML and CSS are entirely sufficient.
*   **Control:** Direct HTML/CSS provides maximum control over the final output and a clear path to implementing the accessibility requirements.
*   **Performance:** Static HTML/CSS files are inherently performant.
*   **Low Barrier to Contribution:** Anyone familiar with basic HTML/CSS can understand and contribute to the codebase.
*   **Future Flexibility:** If the site grows significantly in complexity, the decision to introduce an SSG or other tools can be revisited. Starting with plain HTML/CSS does not preclude this.

## Consequences

*   Content updates (e.g., to the manifesto text or other sections) will involve direct editing of HTML files.
*   No benefits from SSG features like Markdown-to-HTML conversion, templating for repeated elements (though for a single page, this is less critical), or programmatic content generation are realized in this initial version.
*   Maintenance of semantic HTML and adherence to design principles will rely on careful manual editing. 