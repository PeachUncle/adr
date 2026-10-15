# ADR 006: Product Search Integration

## Status
Proposed

## Context
As the product catalog grows, native database search becomes insufficient for providing fast, relevant search results. Modern e-commerce users expect instant, typo-tolerant, faceted search experiences.

## Decision Drivers
- Search performance at scale (1000+ products)
- Typo tolerance and fuzzy matching
- Faceted search and filtering
- Auto-complete and suggestions
- Analytics on search behavior
- South African market considerations

## Options Evaluated

### Option 1: Algolia (Recommended)
**Provider:** Algolia (US-based, global CDN)

**Pros:**
- Industry-leading search speed (<50ms)
- Excellent typo tolerance and relevance
- Easy React/Next.js integration (InstantSearch)
- Built-in analytics
- AI-powered recommendations

**Cons:**
- Pricing based on operations (can be expensive)
- Data hosted externally
- No South African data center

**Pricing:**
- Free: 10,000 search requests/month
- Grow: $1.50 per 1,000 requests
- Premium: Custom pricing

### Option 2: Meilisearch (Self-hosted alternative)
**Provider:** Open Source (self-hosted)

**Pros:**
- Free and open source
- Can be self-hosted in SA region
- Fast and typo-tolerant
- Simple REST API

**Cons:**
- Self-hosting infrastructure required
- Less features than Algolia
- No built-in analytics

### Option 3: Elasticsearch/OpenSearch
**Provider:** Elastic/AWS

**Pros:**
- Highly customizable
- Full-text search capabilities
- Can be hosted on AWS Cape Town

**Cons:**
- Complex configuration
- Higher operational overhead
- Steep learning curve

### Option 4: Typesense
**Provider:** Typesense (can be self-hosted)

**Pros:**
- Open source with cloud option
- Fast and typo-tolerant
- Simple to set up
- Competitive pricing

**Cons:**
- Smaller community
- Less ecosystem support

## Decision
**Recommended:** Start with **Algolia** for immediate value, with option to migrate to **Meilisearch** if costs become prohibitive.

## Integration Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Create Algolia account and configure index
- [ ] Set up search index schema for products
- [ ] Implement product sync on create/update/delete
- [ ] Add environment variables for API keys

### Phase 2: Basic Search (Week 2-3)
- [ ] Install `algoliasearch` and `react-instantsearch-hooks`
- [ ] Create SearchBox component
- [ ] Implement search results page
- [ ] Add product hit component

### Phase 3: Enhanced Search (Week 3-4)
- [ ] Add faceted search (category, price range, material)
- [ ] Implement autocomplete suggestions
- [ ] Add search analytics tracking
- [ ] Create "no results" experience

### Phase 4: Advanced Features (Week 4-5)
- [ ] Implement personalized recommendations
- [ ] Add synonym management
- [ ] Configure query rules for promotions
- [ ] Set up A/B testing for search relevance

## API Design

```typescript
// src/lib/algolia.ts
import algoliasearch from 'algoliasearch';

export const searchClient = algoliasearch(
  process.env.NEXT_PUBLIC_ALGOLIA_APP_ID!,
  process.env.NEXT_PUBLIC_ALGOLIA_SEARCH_KEY!
);

export const adminClient = algoliasearch(
  process.env.ALGOLIA_APP_ID!,
  process.env.ALGOLIA_ADMIN_KEY!
);

export const productsIndex = adminClient.initIndex('products');

// Sync product to Algolia
export async function syncProduct(product: Product) {
  await productsIndex.saveObject({
    objectID: product.id.toString(),
    name: product.name,
    description: product.description,
    sku: product.sku,
    price: product.price,
    category: product.category?.name,
    material: product.material,
    stock_status: product.stock_status,
    image_url: product.image_url,
  });
}
```

## Configuration

### Environment Variables
```env
NEXT_PUBLIC_ALGOLIA_APP_ID=your_app_id
NEXT_PUBLIC_ALGOLIA_SEARCH_KEY=your_search_key
ALGOLIA_ADMIN_KEY=your_admin_key
ALGOLIA_INDEX_NAME=products
```

### Index Settings
```json
{
  "searchableAttributes": [
    "name",
    "description",
    "sku",
    "material",
    "category"
  ],
  "attributesForFaceting": [
    "category",
    "material",
    "stock_status",
    "filterOnly(price)"
  ],
  "customRanking": [
    "desc(popularity)",
    "desc(created_at)"
  ]
}
```

## Consequences

### Positive
- Significantly improved search experience
- Reduced database load
- Better conversion through search
- Actionable search analytics

### Negative
- External dependency
- Additional cost
- Data sync complexity
- Potential latency for SA users

## Related ADRs
- ADR 002: Payment Gateway Integration
- ADR 007: Marketplace Feed Integration (feeds will use same product data)
