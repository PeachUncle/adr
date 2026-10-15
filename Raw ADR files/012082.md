# ADR-001: Page Builder Architecture

**Status:** Proposed
**Date:** 2025-10-14
**Decision Makers:** Architecture Team
**Context:** Custom page builder system for Model Muse Studio

---

## Context and Problem Statement

Model Muse Studio currently uses a simple `custom_pages` table that stores HTML content as plain text. This approach has several limitations:

1. **No structured content**: Pages are stored as raw HTML strings, making them hard to query, analyze, or transform
2. **Limited flexibility**: Can't support different component types with specific styling options
3. **Poor UX**: Admins must write HTML manually or use a basic textarea
4. **No versioning**: Changes can't be tracked or rolled back
5. **Maintenance burden**: Updating page layouts requires HTML knowledge
6. **SEO limitations**: Can't extract structured metadata from HTML blob

We need a flexible, component-based page builder that:
- Supports multiple block types (hero, text, images, galleries, CTAs)
- Provides drag-and-drop ordering
- Offers per-component styling (alignment, spacing, colors)
- Integrates with Supabase storage for images
- Maintains backward compatibility with existing HTML pages
- Enables version history and rollback

---

## Decision Drivers

### Business Requirements
- **User Experience**: Non-technical admins should be able to build pages visually
- **Brand Consistency**: Enforce monotone color palette and design system
- **Speed**: Reduce time to create/update custom pages from hours to minutes
- **Flexibility**: Support future block types without database migrations

### Technical Requirements
- **Performance**: Pages must load in <2s, maintain high Lighthouse scores
- **Scalability**: Support 100+ pages with 5-10 blocks each
- **Maintainability**: Type-safe interfaces, clear separation of concerns
- **SEO**: Server-side rendering, structured metadata
- **Security**: RLS policies, content sanitization, admin-only editing

### Constraints
- Must use existing Supabase PostgreSQL database
- Must work with Next.js 15 App Router
- Must maintain backward compatibility with existing pages
- Limited development resources (prefer simpler solutions)

---

## Considered Options

### Option A: Pure JSON Column

Store all page content as a single JSONB column in `custom_pages`:

```sql
custom_pages (
  id UUID,
  title TEXT,
  blocks JSONB -- entire page structure
)
```

**Example:**
```json
{
  "blocks": [
    {"type": "hero", "props": {...}},
    {"type": "text", "props": {...}}
  ]
}
```

**Pros:**
- Simple schema (single table)
- Easy to understand
- Quick to implement
- Flexible (can store any structure)
- Atomic updates (entire page in one transaction)

**Cons:**
- Can't query individual blocks
- Can't index block properties
- Difficult to implement versioning
- Large row sizes (100KB+ for complex pages)
- No referential integrity for nested data
- Hard to generate analytics (e.g., "how many hero blocks exist?")
- JSONB updates can be cumbersome in SQL

**Use Case:** Small sites (<20 pages), simple requirements, rapid prototyping

---

### Option B: Separate Blocks Table (RECOMMENDED)

Create dedicated `page_blocks` table with JSONB props:

```sql
custom_pages (
  id UUID,
  title TEXT,
  slug TEXT,
  content_version INTEGER
)

page_blocks (
  id UUID,
  page_id UUID REFERENCES custom_pages(id),
  block_type TEXT,
  props JSONB,
  order_position INTEGER,
  spacing JSONB,
  alignment TEXT,
  background_color TEXT
)
```

**Pros:**
- **Queryable**: Can filter/search blocks by type, page, properties
- **Indexable**: Efficient lookups on block_type, page_id, order_position
- **Flexible**: JSONB props allow different schemas per block type
- **Scalable**: Can partition blocks, add caching layers
- **Versionable**: Easy to snapshot individual blocks
- **Type-safe**: Strong TypeScript support with union types
- **Analytical**: Can generate reports (e.g., most-used block types)
- **Performance**: JOIN operations are fast with proper indexes

**Cons:**
- More complex than single JSON column
- Requires JOIN for full page queries
- Multiple tables to manage
- Slightly more storage overhead

**Use Case:** Production systems, >20 pages, need for analytics, long-term maintenance

---

### Option C: Predefined Templates Only

Offer fixed templates with fill-in-the-blank fields:

```sql
page_templates (
  id UUID,
  name TEXT,
  layout TEXT -- 'about', 'portfolio', 'contact'
)

custom_pages (
  id UUID,
  template_id UUID,
  field_values JSONB -- {hero_title: "...", hero_image: "..."}
)
```

**Pros:**
- Simplest for end users
- Guaranteed design consistency
- Fast implementation
- No complex builder UI needed
- Minimal training required

**Cons:**
- Very limited flexibility
- Can't create unique layouts
- Users feel constrained
- May not cover all use cases
- Requires new template for each layout variation
- Template management becomes bottleneck

**Use Case:** Very small teams, strict brand control, limited page variety

---

### Option D: Full CMS (Strapi, Contentful, Sanity)

Integrate third-party headless CMS:

**Pros:**
- Feature-rich out-of-the-box
- Mature, battle-tested
- Active community support
- Regular updates and security patches
- Advanced workflows (drafts, approvals, scheduling)

**Cons:**
- Additional service to manage
- Monthly costs ($15-299/month)
- Data lives outside Supabase
- Increased complexity
- Learning curve
- May be overkill for custom pages use case
- Vendor lock-in

**Use Case:** Enterprise projects, complex content workflows, multi-language sites

---

## Decision Outcome

**Chosen Option: Option B (Separate Blocks Table with JSONB Props)**

### Rationale

1. **Best Balance**: Provides structure (separate table) AND flexibility (JSONB props)
2. **Future-Proof**: Easy to add new block types without schema changes
3. **Performance**: Indexed queries are fast; JOIN overhead is negligible
4. **Analytics**: Can query "show me all pages using gallery blocks"
5. **Versioning**: `page_block_versions` table enables undo/redo
6. **Type Safety**: TypeScript union types provide excellent DX
7. **Scalability**: Can handle 1000+ pages with proper indexing
8. **Cost**: No additional services required

### Implementation Strategy

**Phase 1: Database Schema** (Week 1)
- Create `page_blocks` table
- Create `page_block_versions` table
- Create `page_templates` table
- Add indexes for performance
- Set up RLS policies

**Phase 2: Type Definitions** (Week 1)
- Define TypeScript interfaces for all block types
- Update `database.ts` types
- Create block prop validation schemas

**Phase 3: Migration** (Week 2)
- Create migration script to convert HTML → text blocks
- Maintain `content_version` flag for backward compatibility
- Backup original content

**Phase 4: Rendering** (Week 2-3)
- Build `BlockRenderer` component (server-side)
- Create individual block components (Hero, Text, Image, Gallery, CTA)
- Update `[slug]/page.tsx` to render blocks
- Maintain fallback to HTML rendering for v1 pages

**Phase 5: Builder UI** (Week 4-6)
- Create `PageBuilder` admin component (client-side)
- Implement drag-and-drop with `@dnd-kit`
- Build block editors with real-time preview
- Add block toolbar and settings panel

**Phase 6: Advanced Features** (Week 7-8)
- Template system
- Version history UI
- Responsive preview mode
- SEO metadata editor
- Bulk operations

---

## Consequences

### Positive

- **Developer Experience**: Type-safe interfaces, clear data model
- **User Experience**: Visual page builder, no HTML knowledge required
- **Performance**: Fast queries, efficient rendering
- **Maintainability**: Well-structured code, easy to debug
- **Extensibility**: New block types add no complexity
- **Analytics**: Can generate insights on content usage
- **SEO**: Structured metadata, server-side rendering
- **Security**: Row-level security, content sanitization

### Negative

- **Initial Development**: 8-10 weeks vs 2-3 weeks for Option A
- **Complexity**: More moving parts than pure JSON approach
- **Learning Curve**: Team needs to understand block system
- **Migration Effort**: Must convert existing pages

### Neutral

- **Storage**: ~17MB for 100 pages with full history (acceptable)
- **Query Performance**: JOIN operations add ~5-10ms (negligible)

---

## Validation and Metrics

### Success Criteria

1. **Performance**
   - Page load time: <2s (p95)
   - Lighthouse score: >90
   - Time to First Byte: <500ms

2. **User Adoption**
   - 100% of new pages use block builder
   - 50% reduction in time to create page
   - Admin satisfaction score: >8/10

3. **Technical**
   - Zero data loss during migration
   - Test coverage: >80%
   - No N+1 query issues
   - RLS policies passing security audit

### Monitoring

- Track query performance with Supabase dashboard
- Monitor page render times in production
- Collect user feedback from admin team
- Analyze block usage patterns

---

## Alternatives Not Considered

- **WordPress**: Too heavy, PHP-based
- **Notion API**: Not designed for public websites
- **Custom WYSIWYG**: Reinventing the wheel
- **Markdown files**: Not admin-friendly, no storage integration

---

## References

- [Current Custom Pages Implementation](/Users/mikahalbertson/model-muse-studio/components/admin/CustomPageForm.tsx)
- [Database Schema](/Users/mikahalbertson/model-muse-studio/types/database.ts)
- [Tailwind Config (Color Palette)](/Users/mikahalbertson/model-muse-studio/tailwind.config.ts)
- [Next.js App Router Docs](https://nextjs.org/docs/app)
- [Supabase JSONB Docs](https://supabase.com/docs/guides/database/json)

---

## Appendix A: Block Type Registry

Initial block types to implement:

| Block Type | Priority | Complexity | Use Case |
|------------|----------|------------|----------|
| Hero | High | Medium | Page headers, banner images |
| Text | High | Low | Rich text content, articles |
| Image | High | Low | Single image display |
| Gallery | High | Medium | Multiple images, portfolio |
| CTA | Medium | Low | Call-to-action buttons |
| Spacer | Low | Low | Vertical spacing control |
| Divider | Low | Low | Visual separation |
| Columns | Low | High | Multi-column layouts |
| Quote | Low | Low | Testimonials, quotes |
| Video | Low | Medium | Embedded videos |

---

## Appendix B: Color Palette Reference

From `tailwind.config.ts`:

```typescript
'pure-black': '#000000',
'soft-black': '#0A0A0A',
'charcoal': '#1A1A1A',
'dark-gray': '#2D2D2D',
'medium-gray': '#666666',
'light-gray': '#999999',
'pale-gray': '#CCCCCC',
'off-white': '#F5F5F5',
'pure-white': '#FFFFFF'
```

All blocks use this monotone palette for brand consistency.

---

## Appendix C: Migration Safety

**Risk Mitigation:**

1. **Backup Strategy**
   - Full database backup before migration
   - Separate `custom_pages_content_backup` table
   - Keep original `content` column for 6 months
   - Daily automated backups

2. **Rollback Plan**
   - Migration includes rollback SQL script
   - Can revert to HTML rendering by setting `content_version = 1`
   - Block data preserved even if rollback needed

3. **Testing**
   - Test migration on staging database first
   - Verify all pages render correctly
   - Check performance metrics
   - Validate RLS policies

---

## Appendix D: Future Enhancements

Post-MVP features to consider:

- [ ] A/B testing different page versions
- [ ] Scheduled publishing
- [ ] Page analytics (views, time on page)
- [ ] Collaborative editing with locks
- [ ] Reusable block library
- [ ] AI-powered content suggestions
- [ ] Multi-language support
- [ ] Advanced permissions (editor vs publisher)
- [ ] Workflow automation (draft → review → publish)
- [ ] Custom CSS per block (advanced users)

---

**Decision Status:** ✅ APPROVED for implementation
**Review Date:** 2025-11-14 (1 month post-launch)
