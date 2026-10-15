# ADR-002: Co-located Component Metadata System

**Status**: Accepted

**Date**: 2024-2025 (retroactive documentation)

## Context

With hundreds of animation components, we needed a way to:

1. **Organize Components**: Group related animations into categories and subcategories
2. **Provide Metadata**: Associate each animation with title, description, tags, and configuration
3. **Enable Discovery**: Allow users to browse and search animations effectively
4. **Maintain Type Safety**: Ensure metadata is typed and validated
5. **Support Multiple Variants**: Track Framer Motion vs CSS implementations

Traditional approaches considered:
- **Separate JSON Files**: External metadata files (e.g., `animations.json`)
- **Database**: Store metadata in a database
- **Naming Conventions**: Derive metadata from file/folder structure
- **Co-located Metadata**: Each component file includes its own metadata

## Decision

We implemented a **co-located metadata system** where each animation component file exports its own metadata object:

```typescript
// Example: ButtonBounce.tsx
export const metadata: AnimationMetadata = {
  id: 'button-bounce',
  title: 'Button Bounce',
  description: 'Bouncy button effect on click',
  tags: ['button', 'bounce', 'click'],
  category: 'button-effects',
  group: 'button-effects-framer',
}

export default function ButtonBounce() {
  // Component implementation
}
```

A registration system (`animationRegistry.ts`) then:
1. Dynamically imports all animation components
2. Extracts metadata from each component
3. Builds a hierarchical catalog (categories → groups → animations)
4. Provides type-safe access to the catalog

## Consequences

### Positive

- **Single Source of Truth**: Metadata lives with the component it describes
- **Type Safety**: TypeScript ensures metadata conforms to `AnimationMetadata` interface
- **Refactoring Safety**: Moving/renaming components updates metadata automatically
- **Developer Experience**: All component info in one file reduces context switching
- **Hot Reload**: Metadata changes reflect immediately during development
- **Tree Shaking**: Unused components and their metadata can be eliminated

### Negative

- **Build Complexity**: Registration system requires dynamic imports and processing
- **Runtime Overhead**: Metadata included in bundle (mitigated by tree shaking)
- **Convention Enforcement**: Developers must remember to export metadata
- **Scaling**: With 500+ components, registration can be slow (mitigated with caching)

### Mitigation Strategies

1. **Caching**: `animationDataService` caches catalog to avoid re-processing
2. **Validation**: Build-time checks ensure all components have valid metadata
3. **Documentation**: Clear guidelines in `docs/meta/styleguide.md`
4. **ESLint Rules**: Consider custom rule to enforce metadata export
5. **Code Generation**: Script to generate metadata stubs for new components

## Architecture

```
src/components/
  base/
    button-effects/
      framer/
        ButtonBounce.tsx         # Exports metadata + component
        ButtonPulse.tsx
      css/
        ButtonBounceCSS.tsx

  animationRegistry.ts           # Central registration

src/services/
  animationData.ts               # Data service with caching

src/types/
  animation.ts                   # AnimationMetadata interface
```

### Key Files

- **`animationRegistry.ts`**: Imports all components, extracts metadata, builds catalog
- **`animationData.ts`**: Service layer with caching and error handling
- **`animation.ts`**: Type definitions for metadata structure

### Metadata Structure

```typescript
interface AnimationMetadata {
  id: string                    // Unique identifier
  title: string                 // Display name
  description: string           // Short description
  tags: string[]                // Searchable tags
  category: string              // Top-level category
  group: string                 // Subcategory (framer/css)
  infiniteAnimation?: boolean   // Auto-loop flag
  disableReplay?: boolean       // Hide replay button
}
```

## Alternatives Not Chosen

### Separate JSON Metadata Files

**Pros**: Clear separation of data and code
**Cons**: Maintenance burden (two files per component), no type safety, refactoring risk

### Database-Backed Metadata

**Pros**: Centralized, queryable, version controlled separately
**Cons**: Build complexity, deployment overhead, synchronization issues

### File/Folder Convention

**Pros**: Zero boilerplate
**Cons**: Limited metadata (only file names), inflexible, hard to search

## Future Enhancements

1. **Build-Time Catalog Generation**: Pre-generate catalog at build time for faster startup
2. **Metadata Validation**: JSON Schema or Zod validation for runtime safety
3. **Search Indexing**: Build full-text search index for better discovery
4. **Versioning**: Track metadata versions for migration support

## References

- `src/components/animationRegistry.ts` - Registration implementation
- `src/services/animationData.ts` - Data service
- `docs/architecture.md` - Overall architecture
- `docs/meta/styleguide.md` - Component authoring guidelines
