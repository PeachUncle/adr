# ADR 007: Marketplace Feed Integration

## Status
Proposed

## Context
To increase product visibility and sales, products need to be syndicated to major marketplaces and shopping platforms. This enables customers to discover products through Google Shopping, Facebook Shops, and local South African marketplaces.

## Decision Drivers
- Increase product visibility
- Drive traffic from multiple channels
- Local SA marketplace support
- Automated inventory sync
- ROI tracking per channel

## Marketplaces Evaluated

### Tier 1: Essential (Immediate Priority)

#### Google Merchant Center / Google Shopping
**Relevance:** High - Primary product discovery for SA users

**Features:**
- Free product listings
- Paid Shopping ads
- Performance Max campaigns
- Local inventory ads (for pickup)

**Integration:**
- Product feed (XML/JSON)
- Content API for real-time updates
- Google Analytics 4 for tracking

**Pricing:** Free listings + PPC for ads

#### Facebook/Instagram Shops
**Relevance:** High - Strong social commerce in SA

**Features:**
- Product catalog
- Shopping posts
- Checkout on FB/IG
- Dynamic ads

**Integration:**
- Catalog API
- Facebook Pixel
- Conversions API

**Pricing:** Free catalog + PPC for ads

### Tier 2: Regional Marketplaces

#### Takealot Seller Portal
**Relevance:** High - Largest SA e-commerce platform

**Features:**
- Marketplace listings
- Fulfillment by Takealot
- Seller analytics

**Integration:**
- Seller API
- Inventory sync
- Order management

**Pricing:** Commission-based (7-15%)

#### Bob Shop (formerly bidorbuy)
**Relevance:** Medium - Established SA marketplace

**Features:**
- Product listings
- Auction and fixed price
- Buyer protection

**Integration:**
- API for listings
- Order webhook

**Pricing:** Commission-based (5-10%)

### Tier 3: Future Consideration

#### Amazon South Africa (when available)
- Currently ships to SA from international
- Native marketplace expected

#### Alibaba/AliExpress B2B
- For wholesale/bulk sales
- B2B product listings

## Decision
**Recommended Implementation Order:**
1. Google Merchant Center (immediate - highest ROI)
2. Facebook/Instagram Catalog (immediate - social commerce)
3. Takealot (Phase 2 - requires more setup)
4. Bob Shop (Phase 3 - additional reach)

## Integration Roadmap

### Phase 1: Google Merchant Center (Week 1-2)
- [ ] Create Google Merchant Center account
- [ ] Verify website ownership
- [ ] Set up product feed endpoint
- [ ] Configure feed fetch schedule
- [ ] Submit for review

### Phase 2: Facebook Catalog (Week 2-3)
- [ ] Create Facebook Business account
- [ ] Set up Commerce Manager
- [ ] Configure catalog data source
- [ ] Implement Facebook Pixel
- [ ] Connect Instagram Shopping

### Phase 3: Feed Automation (Week 3-4)
- [ ] Create unified feed generation service
- [ ] Add feed health monitoring
- [ ] Set up error alerting
- [ ] Configure automatic updates on product changes

### Phase 4: Takealot Integration (Week 5-7)
- [ ] Apply for Takealot seller account
- [ ] Map product categories
- [ ] Configure inventory sync
- [ ] Set up order webhook

### Phase 5: Analytics & Optimization (Week 7-8)
- [ ] Set up channel attribution
- [ ] Create performance dashboard
- [ ] A/B test product titles/images
- [ ] Optimize feed for each platform

## Technical Implementation

### Product Feed API Endpoint
```typescript
// src/app/api/feeds/google/route.ts
import { NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import { STOCK_STATUS } from '@/constants';

export async function GET() {
  const products = await prisma.product.findMany({
    where: { stock_status: { not: STOCK_STATUS.OUT_OF_STOCK } },
    include: { category: true },
  });

  const feed = {
    version: '2.1',
    title: 'TASSA Product Feed',
    link: 'https://twinesandstraps.co.za',
    description: 'Twines and Straps SA Products',
    items: products.map(p => ({
      id: p.id.toString(),
      title: p.name,
      description: p.description,
      link: `https://twinesandstraps.co.za/products/${p.id}`,
      image_link: p.image_url,
      price: `${p.price.toFixed(2)} ZAR`,
      availability: p.stock_status === STOCK_STATUS.IN_STOCK
        ? 'in_stock'
        : 'limited_availability',
      brand: 'TASSA',
      gtin: p.sku,
      condition: 'new',
      product_type: p.category?.name,
    })),
  };

  return NextResponse.json(feed);
}
```

### Facebook Catalog Sync
```typescript
// src/lib/facebook-catalog.ts
export async function syncToFacebookCatalog(product: Product) {
  const response = await fetch(
    `https://graph.facebook.com/v18.0/${process.env.FB_CATALOG_ID}/products`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        access_token: process.env.FB_ACCESS_TOKEN,
        retailer_id: product.id.toString(),
        name: product.name,
        description: product.description,
        availability: mapStockStatus(product.stock_status),
        price: Math.round(product.price * 100), // cents
        currency: 'ZAR',
        url: `https://twinesandstraps.co.za/products/${product.id}`,
        image_url: product.image_url,
        brand: 'TASSA',
      }),
    }
  );
  return response.json();
}
```

## Feed Specifications

### Google Product Feed Schema
| Field | Required | Source |
|-------|----------|--------|
| id | Yes | product.id |
| title | Yes | product.name |
| description | Yes | product.description |
| link | Yes | Product URL |
| image_link | Yes | product.image_url |
| price | Yes | product.price + " ZAR" |
| availability | Yes | Mapped stock_status |
| brand | Yes | "TASSA" |
| gtin | Recommended | product.sku |
| mpn | Optional | product.sku |
| condition | Yes | "new" |

## Environment Variables
```env
# Google Merchant Center
GOOGLE_MERCHANT_ID=your_merchant_id
GOOGLE_MERCHANT_KEY=your_service_account_key

# Facebook Catalog
FB_CATALOG_ID=your_catalog_id
FB_ACCESS_TOKEN=your_access_token
FB_PIXEL_ID=your_pixel_id

# Takealot
TAKEALOT_API_KEY=your_api_key
TAKEALOT_SELLER_ID=your_seller_id
```

## Consequences

### Positive
- Increased product visibility
- Multiple sales channels
- Better customer acquisition
- Improved brand awareness

### Negative
- Feed maintenance overhead
- Commission fees on marketplaces
- Inventory sync complexity
- Price parity management

## Related ADRs
- ADR 006: Product Search Integration
- ADR 003: Shipping Integration (for fulfillment)
