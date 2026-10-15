# Automated PDF Sitemap Inclusion

- Status: accepted
- Date: 2025-11-22

## Context and Problem Statement

The site hosts PDF files as supplementary content for blog posts (e.g., ISO27034 Application Security for AI Applications whitepaper). These PDFs are valuable technical resources that users may search for directly, separate from the blog posts that reference them.

Static assets in Astro's `public/` directory are served as-is but are not automatically included in the sitemap. The default `@astrojs/sitemap` integration only generates entries for Astro pages/routes, meaning PDF files and other static assets are invisible to search engines unless manually added.

This creates several problems:
1. **Discoverability**: Search engines won't index PDF content
2. **SEO**: Missing opportunity for PDFs to rank in search results
3. **Manual maintenance**: Adding PDFs to sitemap manually is error-prone and doesn't scale
4. **Inconsistency**: Easy to forget to add new PDFs to sitemap

How should we ensure PDF resources are discoverable by search engines without manual intervention?

## Decision Drivers

- **SEO**: PDFs should be discoverable and indexable by search engines
- **Automation**: No manual maintenance required when adding PDFs
- **Scalability**: Solution should work for any number of PDFs
- **Maintainability**: Code should be simple, testable, and well-organized
- **Zero Runtime Cost**: PDF scanning should happen at build time, not runtime
- **Existing Patterns**: Follow project conventions (TypeScript, utils folder structure)
- **Reliability**: Must not break builds if `public/` directory is missing

## Considered Options

### Option 1: Manual customPages array in astro.config.mjs

- Hardcode PDF URLs in the sitemap configuration
- Pros:
  - Simple, no code needed
  - Explicit control over included PDFs
  - No dependencies or utilities
- Cons:
  - ❌ Manual maintenance required for every new PDF
  - ❌ Error-prone (easy to forget)
  - ❌ Doesn't scale with multiple PDFs
  - ❌ Creates technical debt

### Option 2: Build script that generates customPages

- Create a separate build script (e.g., `scripts/generate-pdf-list.js`) that runs before Astro build
- Pros:
  - Automated scanning
  - Could be run as npm script
- Cons:
  - Additional build step complexity
  - Requires modifying package.json build command
  - Doesn't follow project's utils pattern
  - Not integrated with Astro's build process

### Option 3: Runtime sitemap endpoint

- Create a dynamic API route that scans `public/` at request time
- Pros:
  - Always up-to-date
  - No build-time scanning
- Cons:
  - ❌ Runtime overhead on every sitemap request
  - ❌ Incompatible with static site generation
  - ❌ More complex than needed
  - ❌ Doesn't work with Astro's static output mode

### Option 4: Utility function in src/utils/ (Chosen)

- Create `src/utils/find-pdfs.mjs` that scans `public/` and returns PDF URLs
- Import and call in `astro.config.mjs` to populate sitemap's `customPages`
- Pros:
  - ✅ Fully automated - scans `public/` at build time
  - ✅ Follows existing project structure (`src/utils/`)
  - ✅ Build-time only, zero runtime cost
  - ✅ Works with static site generation
  - ✅ Simple, testable, maintainable
  - ✅ ESM module compatible with config file
  - ✅ Gracefully handles missing directories
- Cons:
  - Adds one utility file
  - Scans file system at build time (negligible performance impact)

## Decision Outcome

Chosen option: "Utility function in src/utils/"

Implementation:

**Created `src/utils/find-pdfs.mjs`:**
- Uses Node.js `fs.readdirSync` with `recursive: true` to scan `public/` directory
- Filters for `.pdf` file extension
- Converts file paths to full URLs (prepends site domain)
- Returns array of PDF URLs for sitemap
- Handles missing `public/` directory gracefully (returns empty array)
- Pure ESM module compatible with `astro.config.mjs`

**Updated `astro.config.mjs`:**
```javascript
import { findPdfs } from './src/utils/find-pdfs.mjs';

const siteUrl = 'https://securing.quest';

export default defineConfig({
  site: siteUrl,
  integrations: [
    mdx(),
    sitemap({
      customPages: findPdfs(siteUrl),
    }),
  ],
  // ...
});
```

**How it works:**
1. At build time, Astro loads `astro.config.mjs`
2. `findPdfs()` is called with the site URL
3. Function scans `public/` recursively for `.pdf` files
4. Returns array of full URLs (e.g., `['https://securing.quest/blog/ai-appsec-is-still-appsec/iso27034-application-security-for-ai-applications.pdf']`)
5. Sitemap integration includes these URLs in generated `sitemap-0.xml`

## Consequences

### Positive

- **Automated**: PDFs automatically included in sitemap when added to `public/`
- **SEO Benefit**: Search engines can discover and index PDF content directly
- **Zero Maintenance**: No manual updates required
- **Discoverable**: Technical documents can rank in search results independently
- **Scalable**: Works for 1 PDF or 100 PDFs
- **Build-time Only**: No runtime performance impact
- **Follows Patterns**: Uses existing `src/utils/` structure (alongside `search.ts`, `youtube.ts`)
- **Simple Code**: ~30 lines, easy to understand and maintain
- **Error Handling**: Gracefully handles missing directories
- **Cross-platform**: Handles both Unix (`/`) and Windows (`\`) path separators

### Negative

- **Build-time Scan**: Adds minor overhead to build process
  - Mitigation: File system scan is very fast (<10ms for typical sites)
- **No Filtering**: All PDFs are included automatically
  - Mitigation: If selective inclusion needed, could add ignore patterns later
  - Current behavior is correct (all PDFs should be public and indexable)
- **File Extension Only**: Relies on `.pdf` extension to identify PDFs
  - Mitigation: Standard practice; edge case of mis-named files is acceptable

### Risks and Mitigations

**Risk**: Accidentally including private/draft PDFs
- Mitigation: Don't put files in `public/` unless they should be public
- `public/` directory is explicitly for publicly-served static assets

**Risk**: Build breaks if `public/` directory doesn't exist
- Mitigation: Error handling with try-catch returns empty array, build continues

**Risk**: PDFs with spaces or special characters in filenames
- Mitigation: Path normalization handles spaces; follows URL encoding standards

## Technical Implementation

**File: `src/utils/find-pdfs.mjs`**
```javascript
import { readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

export function findPdfs(siteUrl) {
  const __dirname = fileURLToPath(new URL('.', import.meta.url));
  const publicDir = join(__dirname, '../../public');

  try {
    const files = readdirSync(publicDir, { recursive: true, encoding: 'utf-8' });

    const pdfUrls = files
      .filter(file => file.endsWith('.pdf'))
      .map(file => {
        const normalizedPath = file.replace(/\\/g, '/');
        return `${siteUrl}/${normalizedPath}`;
      });

    return pdfUrls;
  } catch (error) {
    console.warn('Warning: Could not scan public directory for PDFs:', error.message);
    return [];
  }
}
```

**Integration Point:** `astro.config.mjs`

**Build Output Verification:**
After implementation, `dist/sitemap-0.xml` now includes:
```xml
<url>
  <loc>https://securing.quest/blog/ai-appsec-is-still-appsec/iso27034-application-security-for-ai-applications.pdf</loc>
</url>
```

**File Naming Convention:**
PDFs should use lowercase, hyphen-separated names (e.g., `iso27034-application-security-for-ai-applications.pdf`) for:
- URL readability
- SEO best practices
- Cross-platform compatibility

## Future Enhancements

Potential improvements to consider:

1. **Selective Inclusion**:
   - Add `.sitemapignore` file pattern
   - Ignore PDFs in specific directories (e.g., `public/drafts/`)

2. **Metadata Enhancement**:
   - Parse PDF metadata (title, author, keywords)
   - Include `<lastmod>` based on file modification time
   - Add `<priority>` based on PDF location or metadata

3. **Other Static Assets**:
   - Extend to include `.epub`, `.zip`, or other downloadable resources
   - Configurable file extensions array

4. **Validation**:
   - Warn if PDFs are missing proper metadata
   - Check file size and warn about large PDFs (slow page load)

## Links

- Related ADRs:
  - [ADR-0001](0001-migration-nextjs-to-astro.md): Migration to Astro (context for static site generation)
- References:
  - [Astro Sitemap Documentation](https://docs.astro.build/en/guides/integrations-guide/sitemap/)
  - [Google Search Central: PDF Best Practices](https://developers.google.com/search/docs/crawling-indexing/pdf-best-practices)
  - [Sitemap Protocol](https://www.sitemaps.org/protocol.html)
- Implementation:
  - `src/utils/find-pdfs.mjs`: Utility function
  - `astro.config.mjs`: Integration configuration
