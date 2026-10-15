# ADR 008: Inventory Management Integration

## Status
Proposed

## Context
As the business grows, manual inventory management becomes unsustainable. An Inventory Management System (IMS) or Enterprise Resource Planning (ERP) integration is needed to automate stock tracking, reordering, and multi-channel synchronization.

## Decision Drivers
- Real-time stock accuracy
- Automated reorder points
- Multi-location support (future)
- Integration with accounting (ADR 005)
- South African vendor support
- B2B/wholesale management

## Options Evaluated

### Option 1: DEAR Inventory (Recommended for SMB)
**Provider:** DEAR Systems (now Cin7 Core)

**Pros:**
- Comprehensive inventory features
- Good SA support
- Integrates with Xero/SAGE
- B2B/wholesale module
- Reasonable pricing

**Cons:**
- Learning curve
- Monthly subscription

**Pricing:**
- Standard: $249/month
- Manufacturing: $349/month

**SA Considerations:**
- ZAR billing available
- Local support team

### Option 2: TradeGecko (Now QuickBooks Commerce)
**Provider:** QuickBooks/Intuit

**Pros:**
- Strong QuickBooks integration
- User-friendly
- Multi-channel sync

**Cons:**
- No native SAGE integration
- QuickBooks dependency
- USD pricing

### Option 3: Cin7 Omni
**Provider:** Cin7

**Pros:**
- Enterprise features
- EDI support
- 3PL integration
- Advanced analytics

**Cons:**
- Expensive for SMB
- Complex setup
- Overkill for current scale

**Pricing:** $349-999/month

### Option 4: Unleashed
**Provider:** Unleashed Software

**Pros:**
- Manufacturing focus
- Good Xero integration
- Clean interface

**Cons:**
- Limited SA presence
- No SAGE integration

### Option 5: Custom Solution (Current + Enhancements)
**Description:** Enhance current Prisma-based inventory with alerts

**Pros:**
- No additional cost
- Full control
- No external dependency

**Cons:**
- Development effort
- Limited features
- No accounting integration

## Decision
**Recommended:**
- **Short-term:** Enhance current system with automated alerts and reorder points
- **Medium-term:** Integrate with **DEAR Inventory** when scale requires

## Integration Roadmap

### Phase 1: Internal Enhancements (Week 1-2)
- [ ] Add reorder point field to products
- [ ] Create low stock alert system
- [ ] Implement stock adjustment history
- [ ] Add bulk stock update interface

### Phase 2: Reporting (Week 2-3)
- [ ] Build inventory valuation report
- [ ] Create stock movement history
- [ ] Add ABC analysis for products
- [ ] Implement dead stock identification

### Phase 3: Automation (Week 3-4)
- [ ] Set up automated low stock emails
- [ ] Create purchase order drafts
- [ ] Add supplier lead time tracking
- [ ] Implement safety stock calculations

### Phase 4: IMS Integration (Future - When Scale Requires)
- [ ] Evaluate IMS requirements
- [ ] Select and configure IMS
- [ ] Build sync middleware
- [ ] Migrate inventory data
- [ ] Configure webhooks

## Technical Implementation

### Enhanced Product Schema
```prisma
model Product {
  // ... existing fields
  reorder_point       Int?      @default(5)
  reorder_quantity    Int?      @default(10)
  supplier_lead_days  Int?      @default(7)
  safety_stock        Int?      @default(2)
  last_restock_at     DateTime?
}

model StockAdjustment {
  id          Int      @id @default(autoincrement())
  product_id  Int
  product     Product  @relation(fields: [product_id], references: [id])
  quantity    Int      // positive = add, negative = subtract
  reason      String   // SALE, RETURN, ADJUSTMENT, DAMAGE, RECOUNT
  notes       String?
  created_by  Int?
  created_at  DateTime @default(now())
}
```

### Low Stock Alert Service
```typescript
// src/lib/inventory-alerts.ts
import prisma from './prisma';
import { sendEmail } from './email';
import { STOCK_STATUS } from '@/constants';

export async function checkLowStockAlerts() {
  const lowStockProducts = await prisma.product.findMany({
    where: {
      stock_status: STOCK_STATUS.LOW_STOCK,
      reorder_point: { not: null },
    },
    include: { category: true },
  });

  if (lowStockProducts.length > 0) {
    await sendEmail({
      to: process.env.ADMIN_EMAIL!,
      subject: `Low Stock Alert: ${lowStockProducts.length} products need restocking`,
      template: 'low-stock-alert',
      data: { products: lowStockProducts },
    });
  }

  return lowStockProducts;
}

// Cron job setup
export async function runInventoryChecks() {
  await checkLowStockAlerts();
  await identifyDeadStock();
  await generateReorderSuggestions();
}
```

### Admin Inventory Dashboard
```typescript
// src/app/api/admin/inventory/summary/route.ts
export async function GET() {
  const [
    totalProducts,
    inStock,
    lowStock,
    outOfStock,
    totalValue,
  ] = await Promise.all([
    prisma.product.count(),
    prisma.product.count({ where: { stock_status: STOCK_STATUS.IN_STOCK } }),
    prisma.product.count({ where: { stock_status: STOCK_STATUS.LOW_STOCK } }),
    prisma.product.count({ where: { stock_status: STOCK_STATUS.OUT_OF_STOCK } }),
    prisma.product.aggregate({
      _sum: { price: true },
      where: { stock_status: { not: STOCK_STATUS.OUT_OF_STOCK } },
    }),
  ]);

  return NextResponse.json({
    totalProducts,
    inStock,
    lowStock,
    outOfStock,
    inventoryValue: totalValue._sum.price || 0,
    stockTurnover: await calculateStockTurnover(),
  });
}
```

## IMS API Integration (Future)

### DEAR Inventory Integration
```typescript
// src/lib/dear-inventory.ts
const DEAR_API_BASE = 'https://inventory.dearsystems.com/ExternalApi/v2';

export class DEARInventory {
  constructor(private apiKey: string, private accountId: string) {}

  async syncProduct(product: Product) {
    const response = await fetch(`${DEAR_API_BASE}/product`, {
      method: 'POST',
      headers: {
        'api-auth-accountid': this.accountId,
        'api-auth-applicationkey': this.apiKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        SKU: product.sku,
        Name: product.name,
        Category: product.category?.name,
        DefaultPurchasePrice: product.cost_price,
        DefaultSalesPrice: product.price,
        ReorderPoint: product.reorder_point,
        ReorderQuantity: product.reorder_quantity,
      }),
    });
    return response.json();
  }

  async updateStock(sku: string, quantity: number, location = 'Main Warehouse') {
    // Stock adjustment API call
  }

  async getStockOnHand(sku: string) {
    // Get current stock levels
  }
}
```

## Environment Variables
```env
# DEAR Inventory (Future)
DEAR_API_KEY=your_api_key
DEAR_ACCOUNT_ID=your_account_id

# Internal Alerts
ADMIN_EMAIL=admin@twinesandstraps.co.za
LOW_STOCK_THRESHOLD=5
ALERT_CRON_SCHEDULE="0 8 * * *"
```

## Consequences

### Positive
- Improved stock accuracy
- Reduced stockouts
- Better cash flow management
- Automated reordering
- Accurate cost tracking

### Negative
- Integration complexity
- Additional subscription cost
- Training required
- Data sync challenges

## Related ADRs
- ADR 005: Accounting Integration (inventory value sync)
- ADR 007: Marketplace Feed Integration (stock sync to channels)
