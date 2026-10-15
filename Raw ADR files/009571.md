# ADR-0001: SchemaBuilder Utility for Schema.org Structured Data

## Status

Accepted

## Date

2025-11-09

## Context

The project requires Schema.org structured data across multiple SEO components:
- SEO.astro
- HealthArticleSchema.astro
- WebsiteSchema.astro
- BreadcrumbSchema.astro

Initial implementation resulted in ~150-200 lines of duplicate code across these components for:
- Building image schema objects
- Creating author/organization schemas
- Formatting structured data consistently
- Validating URLs and handling errors

This duplication violated the DRY principle documented in CLAUDE.md and made maintenance difficult - any change to schema formatting required updating multiple files.

## Decision

Created a centralized `SchemaBuilder` utility (`src/utils/seo/SchemaBuilder.ts`) that:

1. **Consolidates common schema generation logic** into reusable functions:
   - `buildImageObject()` - Generates Schema.org ImageObject
   - `buildAuthorSchema()` - Creates Person/Organization author schemas
   - `buildOrganizationSchema()` - Generates Organization schemas
   - Helper utilities for URL validation and data normalization

2. **Provides type-safe interfaces** for all schema options:
   - `ImageSchemaOptions`
   - `AuthorSchemaOptions`
   - `OrganizationSchemaOptions`

3. **Centralizes error handling and logging** using the project's logger utility

4. **Acts as single source of truth** for:
   - Organization data (name, URL, founding year)
   - Default author information
   - Schema formatting conventions

## Consequences

### Positive

- **Eliminated ~150-200 lines of duplicate code** across SEO components
- **Ensured consistent schema formatting** - all components use the same logic
- **Simplified maintenance** - schema changes only need to be made in one place
- **Improved type safety** - TypeScript interfaces catch schema errors at compile time
- **Centralized validation** - URL validation and data normalization handled consistently
- **Better testability** - Pure functions in SchemaBuilder can be unit tested independently

### Negative

- **Additional abstraction layer** - developers must understand SchemaBuilder API
- **Potential over-engineering** for very simple schemas (but acceptable trade-off)
- **Single point of failure** - bugs in SchemaBuilder affect all SEO components (mitigated by testing)

### Neutral

- Schema generation is now a two-step process: import SchemaBuilder, call appropriate function
- Requires developers to check SchemaBuilder documentation when creating new schema types

## Implementation Details

```typescript
// Example usage in SEO components
import { buildImageObject, buildAuthorSchema } from "@/utils/seo/SchemaBuilder";

const imageSchema = buildImageObject({
  url: canonicalURL,
  width: 1200,
  height: 630,
  alt: title
});

const authorSchema = buildAuthorSchema({
  name: author.name,
  url: authorUrl,
  expertise: author.expertise
});
```

## Related Decisions

- Logging abstraction (ADR-0004) - SchemaBuilder uses centralized logger
- Component size guidelines in CLAUDE.md - SchemaBuilder helps keep components under 300 lines

## Notes

This pattern should be applied to other areas of duplication identified in the codebase. SchemaBuilder demonstrates the value of extracting shared logic into utilities rather than duplicating across components.

## References

- CLAUDE.md: Development Principles - DRY principle
- `src/utils/seo/SchemaBuilder.ts`
- `src/utils/seo/__tests__/SchemaBuilder.test.ts`
