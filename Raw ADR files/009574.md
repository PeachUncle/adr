# ADR-0005: Content Collections Structure

## Status

Accepted

## Date

2025-11-09

## Context

The project is a health-focused blog requiring:
- Blog posts with rich metadata
- Author profiles
- Glossary of health terms
- Scientific references
- Product recommendations
- Books and resources

**Requirements**:
- Type-safe content schemas
- Rich frontmatter validation
- Relationships between content types (posts → authors, posts → references)
- Support for both Markdown and MDX
- YAML for structured data
- Fast build times
- Good developer experience

**Challenges**:
- How to structure different content types
- How to handle relationships (e.g., blog post referencing multiple authors/references)
- How to validate frontmatter at build time
- How to keep schemas maintainable
- How to support both file-based and programmatic content

## Decision

Adopted **Astro Content Collections** with a directory-based structure:

### 1. Directory Structure
```
src/data/
├── authors/       # Author profiles (Markdown)
├── blog/          # Blog posts (MDX)
├── glossary/      # Health terms (Markdown)
├── favorites/     # Product recommendations (YAML)
├── references/    # Scientific citations (individual YAML files)
└── books/         # Book recommendations (YAML)
```

### 2. Collection Configuration

**Location**: `src/content.config.ts`

**Pattern**: Each collection defined with:
- Glob loader pattern
- Zod schema for validation
- Type inference for TypeScript

**Example**:
```typescript
const blog = defineCollection({
  loader: glob({ pattern: "**/[^_]*.{md,mdx}", base: "src/data/blog" }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      author: z.union([z.string(), reference("authors")]),
      description: z.string().min(10),
      pubDatetime: z.coerce.date(),
      categories: z.array(z.enum(CATEGORIES)),
      heroImage: z.object({
        src: image(),
        alt: z.string()
      }),
      references: z.array(reference("references")).optional()
    })
});
```

### 3. Reference System

**Key Innovation**: Individual YAML files per reference

**Structure**:
```
src/data/references/
├── 2023-smith-nutrition-health.yaml
├── 2024-jones-mindfulness.yaml
└── 2024-wilson-exercise.yaml
```

**Benefits**:
- Easy to reuse across articles
- Single source of truth
- Validates once, used everywhere
- Git-friendly (clear diffs)

**Naming Convention**: `{year}-{author}-{topic-keywords}.yaml`

### 4. Type Safety

Astro generates TypeScript types from schemas:
```typescript
import type { CollectionEntry } from "astro:content";

type BlogPost = CollectionEntry<"blog">;
type Author = CollectionEntry<"authors">;
type Reference = CollectionEntry<"references">;
```

Full IntelliSense and compile-time validation.

### 5. Validation Strategy

**Build-time validation**:
- Zod schemas validate all frontmatter
- Invalid content causes build failure
- Clear error messages point to exact issue

**Runtime validation**:
- Additional validation in components (e.g., URL format)
- Validation utilities in `src/types/index.ts`

## Consequences

### Positive

- **Type safety**: Full TypeScript support, compile-time errors
- **Validation**: Frontmatter validated at build time
- **Relationships**: Built-in support via `reference()` helper
- **Developer experience**: Autocomplete for all content fields
- **Performance**: Content loaded at build time, cached efficiently
- **Reusability**: References used across multiple posts
- **Maintainability**: Schemas centralized in one file
- **Flexibility**: Support for Markdown, MDX, and YAML
- **Git-friendly**: Individual files create clear diffs
- **Documentation**: Schema serves as documentation

### Negative

- **Learning curve**: Developers must understand Astro content collections
- **Migration complexity**: Changing schema requires content updates
- **Build-time errors**: Content errors prevent builds (good for quality, bad for iteration speed)
- **Astro-specific**: Tied to Astro framework (acceptable trade-off)

### Neutral

- Content must follow specific directory structure
- Frontmatter must match schema exactly
- Reference IDs must match filenames

## Implementation Details

### Blog Post Example
```yaml
---
title: "Understanding Gut Health"
author: "dr-mueller"  # Reference to authors collection
description: "Comprehensive guide to gut microbiome"
pubDatetime: 2024-03-15
categories: ["Gesundheit", "Ernährung"]
group: "health"
featured: true
draft: false
heroImage:
  src: "./images/gut-health.avif"
  alt: "Illustration of gut microbiome"
references:
  - "2023-smith-nutrition-health"
  - "2024-jones-gut-microbiome"
---

Blog post content here...
```

### Reference Example (YAML)
```yaml
# src/data/references/2023-smith-nutrition-health.yaml
type: journal
title: "Nutrition and Gut Health: A Comprehensive Review"
authors:
  - "Smith, J."
  - "Johnson, K."
year: 2023
journal: "Journal of Nutrition Research"
volume: 45
issue: 3
pages: "123-145"
doi: "10.1234/jnr.2023.45.3.123"
keywords:
  - "nutrition"
  - "gut health"
  - "microbiome"
```

### Loading Content
```typescript
import { getCollection, getEntry } from "astro:content";

// Get all blog posts
const posts = await getCollection("blog");

// Get specific reference
const ref = await getEntry("references", "2023-smith-nutrition-health");

// Filter by criteria
const featuredPosts = await getCollection("blog", ({ data }) => {
  return data.featured === true && data.draft !== true;
});
```

## Schema Design Principles

### 1. Required vs Optional
- **Required**: title, description, pubDatetime, categories
- **Optional**: tags, canonicalURL, modDatetime
- **Defaults**: draft (false), featured (false)

### 2. Enums for Controlled Values
```typescript
categories: z.array(z.enum(CATEGORIES))  // Predefined list
group: z.enum(GROUPS)                    // Controlled vocabulary
```

### 3. Relationships via Reference
```typescript
author: reference("authors")           // Single reference
references: z.array(reference("references")) // Multiple references
```

### 4. Complex Objects
```typescript
heroImage: z.object({
  src: image(),           // Astro image helper
  alt: z.string()
})
```

## Migration Path

If migrating from another CMS:

1. Export content to Markdown/YAML
2. Transform frontmatter to match schema
3. Place files in appropriate directories
4. Run `bun run build` to validate
5. Fix any schema violations
6. Commit to repository

## Performance Optimization

Content collections integrate with caching (ADR-0003):
- References cached after first load
- Content hashed for change detection
- Only changed content reprocessed

## Validation Error Examples

**Good error message from Zod**:
```
[blog] src/data/blog/gut-health.mdx
  - description: String must contain at least 10 character(s)
  - categories: Invalid enum value. Expected 'Gesundheit' | 'Ernährung' | ...
```

Clear, actionable, points to exact file and field.

## Future Enhancements

Potential improvements:

1. **Content versioning**: Track changes over time
2. **Multi-language support**: Extend for i18n
3. **Content validation CLI**: Pre-commit validation
4. **Auto-migration tools**: Upgrade schemas automatically
5. **Content preview**: Preview unpublished drafts
6. **Content search**: Full-text search across collections

## Alternatives Considered

### 1. Traditional CMS (Contentful, Sanity)
**Rejected**: Adds complexity, requires API calls, costs money, loses git-based workflow

### 2. Flat Markdown Files (no schema)
**Rejected**: No validation, no type safety, error-prone

### 3. JSON Files for All Content
**Rejected**: Less human-friendly than YAML/Markdown, harder to write

### 4. Database-backed Content
**Rejected**: Overkill for static site, adds deployment complexity

## Related Decisions

- Reference caching (ADR-0003) - Optimizes content collection loading
- Component composition (ADR-0002) - Content rendered via reusable components
- TypeScript best practices (CLAUDE.md) - Collections provide excellent types

## Pattern Extension

Content collections pattern can extend to:
- Newsletter archives
- Case studies
- Team member profiles
- Event listings
- FAQ sections

## Notes

Content collections demonstrate **Design by Contract**:
- Schema defines the contract
- Content must fulfill contract
- Build system enforces contract
- TypeScript carries contract through codebase

This architectural decision is fundamental to the project's maintainability and developer experience.

## References

- `src/content.config.ts`
- Astro Content Collections documentation
- Zod validation library
- CLAUDE.md: References System section
