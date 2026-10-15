# ADR-003: Shipping & Logistics Integration

**Status:** Proposed
**Date:** 2025-11-29
**Decision Makers:** Development Team, Operations Manager
**Technical Story:** Implement shipping rate calculation, waybill generation, and tracking

## Context and Problem Statement

Twines and Straps needs to provide customers with accurate shipping options at checkout and streamline order fulfillment. Products range from lightweight twine (2kg) to heavy cargo nets (20kg+), requiring flexible shipping solutions. Key requirements:

- Real-time shipping quotes at checkout
- Automated waybill generation
- Package tracking for customers
- Support for different delivery speeds
- Cost-effective options for heavy/bulky items

## Decision Drivers

- **Geographic Coverage:** Must deliver nationwide in South Africa
- **Product Weight Range:** 0.5kg to 50kg+ packages
- **Cost Efficiency:** Competitive shipping rates for price-sensitive customers
- **Reliability:** Consistent delivery times and low damage rates
- **Integration Quality:** API availability and documentation
- **Collection Points:** Option for cheaper customer collection

## Considered Options

### Option 1: The Courier Guy (TCG) Only

| Aspect | Details |
|--------|---------|
| **Coverage** | All major SA cities, most rural areas |
| **Weight Limit** | Up to 70kg per parcel |
| **API** | REST API for quotes, bookings, tracking |
| **Delivery Speed** | Economy (3-5 days), Express (1-2 days) |
| **Pricing** | Volume-based, competitive for medium parcels |

**Pros:**
- Most popular courier in SA e-commerce
- Excellent API documentation
- Reliable tracking
- Good rural coverage

**Cons:**
- Expensive for very heavy items
- No integrated collection points
- Account setup required for API access

### Option 2: Pargo (Collection Points) Only

| Aspect | Details |
|--------|---------|
| **Coverage** | 3000+ collection points nationwide |
| **Weight Limit** | Up to 20kg per parcel |
| **Delivery Speed** | 2-5 business days |
| **Pricing** | Flat rate, significantly cheaper than door-to-door |

**Pros:**
- 30-50% cheaper than door-to-door
- Convenient for urban customers
- No failed delivery attempts
- Good for lightweight products

**Cons:**
- Weight limitation (20kg max)
- Not suitable for rural customers
- Requires customer to collect

### Option 3: TCG Primary + Pargo Secondary

**Description:** Offer door-to-door via TCG and collection point via Pargo.

**Pros:**
- Customer choice based on preference/budget
- Best coverage (door-to-door + collection)
- Cost optimization for customers
- Redundancy

**Cons:**
- Two integrations to maintain
- More complex checkout UX
- Weight restrictions for Pargo

### Option 4: Multi-Courier Aggregator (Bob Go, Shiplogic)

**Description:** Use aggregator to access multiple couriers via single API.

**Pros:**
- Single integration, multiple couriers
- Automatic cheapest option selection
- Unified tracking

**Cons:**
- Aggregator fee reduces margins
- Less control over carrier selection
- May have service limitations

## Decision Outcome

**Chosen Option: Option 3 - TCG Primary + Pargo Secondary**

### Rationale

1. **TCG for Door-to-Door:** Reliable, good API, handles heavy items
2. **Pargo for Budget Option:** Cost-effective for customers who can collect
3. **Customer Choice:** Let customers select based on convenience vs. cost
4. **Product Fit:** Heavy nets/equipment via TCG, lighter accessories via Pargo

### Implementation Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Checkout - Shipping                        │
├───────────────────────────────────────────────────────────────────┤
│  📍 Delivery Address: [Customer Address Input]                    │
│                                                                   │
│  📦 Shipping Options:                                             │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ○ The Courier Guy - Door to Door                           │  │
│  │   Express (1-2 days): R120.00                              │  │
│  │   Economy (3-5 days): R75.00                               │  │
│  └────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ○ Pargo Collection Point                                   │  │
│  │   Select Point: [Dropdown - nearest points]                │  │
│  │   2-5 days: R45.00                                         │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │      Shipping API Service      │
              │  /api/shipping/quote           │
              │  /api/shipping/book            │
              │  /api/shipping/track           │
              └───────────────────────────────┘
                     │              │
           ┌─────────┴──────┐      │
           ▼                ▼      ▼
    ┌────────────┐   ┌────────────┐
    │  TCG API   │   │ Pargo API  │
    └────────────┘   └────────────┘
```

### Technical Specification

#### File Structure

```
src/lib/shipping/
├── types.ts           # Shared types for shipping
├── tcg/
│   ├── config.ts      # TCG API configuration
│   ├── quote.ts       # Get shipping quotes
│   ├── book.ts        # Create waybill/booking
│   ├── track.ts       # Track shipment
│   └── webhook.ts     # Status update handler
├── pargo/
│   ├── config.ts      # Pargo API configuration
│   ├── points.ts      # Get collection points
│   ├── quote.ts       # Get shipping quote
│   └── book.ts        # Create shipment
├── calculator.ts      # Weight/dimensions calculator
└── index.ts           # Unified shipping interface
```

#### Shipping Types

```typescript
// src/lib/shipping/types.ts
export interface ShippingAddress {
  name: string;
  street: string;
  suburb: string;
  city: string;
  province: string;
  postalCode: string;
  phone: string;
}

export interface ShippingItem {
  weight: number;        // kg
  length: number;        // cm
  width: number;         // cm
  height: number;        // cm
  quantity: number;
  description: string;
}

export interface ShippingQuote {
  provider: 'TCG' | 'PARGO';
  service: string;       // 'EXPRESS', 'ECONOMY', 'COLLECTION'
  price: number;         // ZAR
  estimatedDays: number;
  collectionPoint?: PargoPoint;
}

export interface ShippingBooking {
  waybillNumber: string;
  trackingUrl: string;
  labelUrl?: string;
  estimatedDelivery: Date;
}

export interface PargoPoint {
  id: string;
  name: string;
  address: string;
  city: string;
  postalCode: string;
  hours: string;
  distance: number;      // km from customer
}
```

#### The Courier Guy Integration

```typescript
// src/lib/shipping/tcg/quote.ts
import { TCG_CONFIG } from './config';
import type { ShippingAddress, ShippingItem, ShippingQuote } from '../types';

export async function getTCGQuotes(
  from: ShippingAddress,
  to: ShippingAddress,
  items: ShippingItem[]
): Promise<ShippingQuote[]> {
  // Calculate total volumetric weight
  const totalWeight = calculateVolumetricWeight(items);

  const response = await fetch(`${TCG_CONFIG.baseUrl}/quote`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TCG_CONFIG.apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      account_number: TCG_CONFIG.accountNumber,
      collection_address: formatAddress(from),
      delivery_address: formatAddress(to),
      parcels: items.map(item => ({
        weight: item.weight,
        length: item.length,
        width: item.width,
        height: item.height,
        description: item.description,
      })),
    }),
  });

  const data = await response.json();

  return data.rates.map((rate: any) => ({
    provider: 'TCG',
    service: rate.service_level,
    price: rate.price,
    estimatedDays: rate.delivery_days,
  }));
}

function calculateVolumetricWeight(items: ShippingItem[]): number {
  return items.reduce((total, item) => {
    const volumetric = (item.length * item.width * item.height) / 5000;
    const actual = item.weight;
    return total + Math.max(volumetric, actual) * item.quantity;
  }, 0);
}
```

```typescript
// src/lib/shipping/tcg/book.ts
import { TCG_CONFIG } from './config';
import type { ShippingAddress, ShippingItem, ShippingBooking } from '../types';

export async function createTCGWaybill(
  orderId: string,
  from: ShippingAddress,
  to: ShippingAddress,
  items: ShippingItem[],
  service: string
): Promise<ShippingBooking> {
  const response = await fetch(`${TCG_CONFIG.baseUrl}/shipment`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TCG_CONFIG.apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      account_number: TCG_CONFIG.accountNumber,
      reference: orderId,
      service_level: service,
      collection_address: formatAddress(from),
      delivery_address: formatAddress(to),
      parcels: items.map((item, i) => ({
        parcel_number: i + 1,
        weight: item.weight,
        length: item.length,
        width: item.width,
        height: item.height,
        description: item.description,
      })),
      collection_date: getNextBusinessDay(),
    }),
  });

  const data = await response.json();

  return {
    waybillNumber: data.waybill_number,
    trackingUrl: `https://thecourierguy.co.za/track/${data.waybill_number}`,
    labelUrl: data.label_url,
    estimatedDelivery: new Date(data.estimated_delivery),
  };
}
```

#### Pargo Integration

```typescript
// src/lib/shipping/pargo/points.ts
import { PARGO_CONFIG } from './config';
import type { PargoPoint } from '../types';

export async function getNearbyPargoPoints(
  latitude: number,
  longitude: number,
  limit: number = 5
): Promise<PargoPoint[]> {
  const response = await fetch(
    `${PARGO_CONFIG.baseUrl}/points?lat=${latitude}&lng=${longitude}&limit=${limit}`,
    {
      headers: {
        'Authorization': `Bearer ${PARGO_CONFIG.apiKey}`,
      },
    }
  );

  const data = await response.json();

  return data.points.map((point: any) => ({
    id: point.id,
    name: point.name,
    address: point.address,
    city: point.city,
    postalCode: point.postal_code,
    hours: point.operating_hours,
    distance: point.distance_km,
  }));
}
```

#### Unified Shipping API

```typescript
// src/app/api/shipping/quote/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getTCGQuotes } from '@/lib/shipping/tcg/quote';
import { getPargoQuote, getNearbyPargoPoints } from '@/lib/shipping/pargo';
import { calculateItemDimensions } from '@/lib/shipping/calculator';
import prisma from '@/lib/prisma';

export async function POST(request: NextRequest) {
  try {
    const { cartItems, deliveryAddress, coordinates } = await request.json();

    // Get products with weights from database
    const productIds = cartItems.map((item: any) => item.productId);
    const products = await prisma.product.findMany({
      where: { id: { in: productIds } },
    });

    // Calculate shipping items
    const shippingItems = cartItems.map((item: any) => {
      const product = products.find(p => p.id === item.productId);
      return calculateItemDimensions(product, item.quantity);
    });

    const quotes: ShippingQuote[] = [];

    // Get TCG quotes (door-to-door)
    const warehouseAddress = getWarehouseAddress();
    const tcgQuotes = await getTCGQuotes(warehouseAddress, deliveryAddress, shippingItems);
    quotes.push(...tcgQuotes);

    // Get Pargo quote if items are under weight limit
    const totalWeight = shippingItems.reduce((sum, item) => sum + item.weight * item.quantity, 0);
    if (totalWeight <= 20) {
      const pargoPoints = await getNearbyPargoPoints(coordinates.lat, coordinates.lng);
      const pargoQuote = await getPargoQuote(shippingItems);
      quotes.push({
        ...pargoQuote,
        collectionPoints: pargoPoints,
      });
    }

    return NextResponse.json({ quotes });
  } catch (error) {
    console.error('Shipping quote error:', error);
    return NextResponse.json({ error: 'Failed to get shipping quotes' }, { status: 500 });
  }
}
```

### Database Schema Updates

```prisma
// Add shipping fields to Order model
model Order {
  // ... existing fields
  shipping_provider     String?   // 'TCG', 'PARGO'
  shipping_service      String?   // 'EXPRESS', 'ECONOMY', 'COLLECTION'
  waybill_number        String?
  tracking_url          String?
  pargo_point_id        String?
  estimated_delivery    DateTime?
  actual_delivery       DateTime?
  shipping_label_url    String?
}

// Track shipping events
model ShippingEvent {
  id          Int      @id @default(autoincrement())
  order_id    Int
  status      String   // 'BOOKED', 'COLLECTED', 'IN_TRANSIT', 'OUT_FOR_DELIVERY', 'DELIVERED'
  location    String?
  description String
  timestamp   DateTime
  created_at  DateTime @default(now())

  order Order @relation(fields: [order_id], references: [id])

  @@index([order_id])
}
```

### Webhook Handling

```typescript
// src/app/api/webhooks/shipping/route.ts
import { NextRequest, NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import { sendShippingUpdate } from '@/lib/email';

export async function POST(request: NextRequest) {
  try {
    const provider = request.headers.get('x-provider');
    const body = await request.json();

    let orderId: number;
    let status: string;
    let description: string;

    if (provider === 'TCG') {
      orderId = parseInt(body.reference);
      status = mapTCGStatus(body.status);
      description = body.description;
    } else if (provider === 'PARGO') {
      orderId = parseInt(body.order_reference);
      status = mapPargoStatus(body.event_type);
      description = body.message;
    } else {
      return NextResponse.json({ error: 'Unknown provider' }, { status: 400 });
    }

    // Create shipping event
    await prisma.shippingEvent.create({
      data: {
        order_id: orderId,
        status,
        description,
        timestamp: new Date(body.timestamp),
      },
    });

    // Update order if delivered
    if (status === 'DELIVERED') {
      await prisma.order.update({
        where: { id: orderId },
        data: {
          status: 'DELIVERED',
          actual_delivery: new Date(),
        },
      });
    }

    // Notify customer
    const order = await prisma.order.findUnique({
      where: { id: orderId },
      include: { user: true },
    });

    if (order?.user?.email) {
      await sendShippingUpdate(order.user.email, {
        orderNumber: order.order_number,
        status,
        trackingUrl: order.tracking_url,
      });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Shipping webhook error:', error);
    return NextResponse.json({ error: 'Processing failed' }, { status: 500 });
  }
}
```

### Frontend Components

```typescript
// src/components/ShippingSelector.tsx
'use client';

import { useState, useEffect } from 'react';
import type { ShippingQuote, PargoPoint } from '@/lib/shipping/types';

interface ShippingSelectorProps {
  cartItems: CartItem[];
  address: Address;
  onSelect: (quote: ShippingQuote) => void;
}

export function ShippingSelector({ cartItems, address, onSelect }: ShippingSelectorProps) {
  const [quotes, setQuotes] = useState<ShippingQuote[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuote, setSelectedQuote] = useState<ShippingQuote | null>(null);
  const [pargoPoint, setPargoPoint] = useState<PargoPoint | null>(null);

  useEffect(() => {
    fetchQuotes();
  }, [cartItems, address]);

  const fetchQuotes = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/shipping/quote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cartItems,
          deliveryAddress: address,
          coordinates: await getCoordinates(address),
        }),
      });
      const data = await response.json();
      setQuotes(data.quotes);
    } catch (error) {
      console.error('Failed to fetch shipping quotes');
    } finally {
      setLoading(false);
    }
  };

  // ... render shipping options
}
```

### Environment Variables

```bash
# The Courier Guy
TCG_API_KEY=xxx
TCG_ACCOUNT_NUMBER=xxx
TCG_BASE_URL=https://api.thecourierguy.co.za/v1

# Pargo
PARGO_API_KEY=xxx
PARGO_BASE_URL=https://api.pargo.co.za/v1
```

### Implementation Timeline

**Phase 1: TCG Integration (Sprint 1)**
- [ ] Set up TCG business account
- [ ] Implement quote API
- [ ] Build waybill generation
- [ ] Add tracking integration
- [ ] Set up webhook handler

**Phase 2: Pargo Integration (Sprint 2)**
- [ ] Set up Pargo merchant account
- [ ] Implement point selector
- [ ] Add quote and booking
- [ ] Integrate tracking

**Phase 3: Checkout Integration (Sprint 3)**
- [ ] Build ShippingSelector component
- [ ] Add shipping to checkout flow
- [ ] Implement admin shipping dashboard
- [ ] Email notifications for status updates

### Consequences

**Positive:**
- Comprehensive shipping coverage
- Customer choice and cost savings
- Automated fulfillment workflow
- Real-time tracking

**Negative:**
- Two APIs to maintain
- Complexity in checkout UX
- Weight restrictions for Pargo
- Setup overhead for accounts

---

*Last Updated: November 2025*
