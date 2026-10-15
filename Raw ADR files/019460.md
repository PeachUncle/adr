# ADR-005: Accounting & Invoicing Integration

**Status:** Proposed
**Date:** 2025-11-29
**Decision Makers:** Development Team, Finance Manager
**Technical Story:** Integrate with accounting software for invoicing and financial reporting

## Context and Problem Statement

Twines and Straps needs to integrate e-commerce transactions with accounting systems for:

- Automatic invoice generation from orders
- Payment reconciliation
- VAT/Tax reporting (SA compliance)
- Financial reporting and analysis
- Inventory value tracking

## Decision Drivers

- **SA Market Prevalence:** Accountant familiarity with the platform
- **VAT Compliance:** Proper SA VAT handling and reporting
- **API Quality:** Robust integration capabilities
- **Pricing:** Cost-effective for SME
- **Bank Integration:** SA bank feed support

## Considered Options

### Option 1: Xero

| Aspect | Details |
|--------|---------|
| **Pricing** | From R350/month |
| **API** | OAuth 2.0, REST API |
| **SA Support** | Full VAT, bank feeds |
| **Features** | Invoicing, expenses, reporting, payroll |

**Pros:**
- Modern cloud platform
- Excellent API and documentation
- Strong SA presence and support
- Good mobile app

**Cons:**
- Higher cost than Sage
- Less established in SA than Sage

### Option 2: Sage Business Cloud

| Aspect | Details |
|--------|---------|
| **Pricing** | From R200/month |
| **API** | REST API |
| **SA Support** | Deep SA tax expertise |
| **Features** | Full accounting suite |

**Pros:**
- Most established in SA
- Best SA tax compliance
- Lower cost
- Accountant familiarity

**Cons:**
- Older platform feel
- API less modern than Xero
- Documentation quality varies

### Option 3: QuickBooks

| Aspect | Details |
|--------|---------|
| **Pricing** | From R300/month |
| **API** | REST API |
| **SA Support** | Available but less focus |

**Pros:**
- Global brand
- Good automation features

**Cons:**
- SA not primary market
- Bank integration limited
- Less accountant familiarity in SA

## Decision Outcome

**Chosen Option: Option 1 - Xero**

### Rationale

1. **API Quality:** Best developer experience, modern OAuth 2.0
2. **Growing SA Adoption:** Increasing accountant acceptance
3. **Integration Ecosystem:** Many e-commerce connectors exist
4. **Automation:** Rules for recurring transactions
5. **Real-time Sync:** Webhooks for immediate updates

### Implementation Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    E-commerce Platform                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │    Orders    │  │   Payments   │  │    Products      │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
└─────────┼─────────────────┼────────────────────┼────────────┘
          │                 │                    │
          ▼                 ▼                    ▼
┌──────────────────────────────────────────────────────────────┐
│                   Xero Sync Service                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Invoice     │  │   Payment    │  │   Inventory      │   │
│  │  Creation    │  │   Recording  │  │   Sync           │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                        Xero API                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐ │
│  │  Invoices  │  │  Payments  │  │  Contacts  │  │ Items  │ │
│  └────────────┘  └────────────┘  └────────────┘  └────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Technical Specification

#### File Structure

```
src/lib/accounting/
├── xero/
│   ├── config.ts          # OAuth configuration
│   ├── client.ts          # Xero API client
│   ├── auth.ts            # OAuth token management
│   └── types.ts           # Xero type definitions
├── sync/
│   ├── invoices.ts        # Invoice sync logic
│   ├── payments.ts        # Payment recording
│   ├── contacts.ts        # Customer sync
│   └── inventory.ts       # Product/inventory sync
├── mappers/
│   ├── order-to-invoice.ts
│   └── customer-to-contact.ts
└── index.ts               # Main accounting service
```

#### Xero OAuth Setup

```typescript
// src/lib/accounting/xero/auth.ts
import { XeroClient } from 'xero-node';

const xero = new XeroClient({
  clientId: process.env.XERO_CLIENT_ID!,
  clientSecret: process.env.XERO_CLIENT_SECRET!,
  redirectUris: [process.env.XERO_REDIRECT_URI!],
  scopes: [
    'openid',
    'profile',
    'email',
    'accounting.transactions',
    'accounting.contacts',
    'accounting.settings',
  ],
});

export async function getXeroClient(): Promise<XeroClient> {
  // Get stored tokens from database
  const tokens = await getStoredTokens();

  if (tokens) {
    xero.setTokenSet(tokens);

    // Refresh if needed
    if (xero.readTokenSet().expired()) {
      const newTokens = await xero.refreshToken();
      await storeTokens(newTokens);
    }
  }

  return xero;
}

export async function initiateXeroAuth(): Promise<string> {
  const consentUrl = await xero.buildConsentUrl();
  return consentUrl;
}

export async function handleXeroCallback(code: string): Promise<void> {
  const tokenSet = await xero.apiCallback(code);
  await storeTokens(tokenSet);
}
```

#### Invoice Sync Service

```typescript
// src/lib/accounting/sync/invoices.ts
import { getXeroClient } from '../xero/auth';
import { Invoice, LineItem } from 'xero-node';
import { mapOrderToInvoice } from '../mappers/order-to-invoice';
import prisma from '@/lib/prisma';

export async function createInvoiceFromOrder(orderId: number): Promise<string> {
  const xero = await getXeroClient();

  // Get order with items
  const order = await prisma.order.findUnique({
    where: { id: orderId },
    include: {
      items: { include: { product: true } },
      user: true,
    },
  });

  if (!order) throw new Error('Order not found');

  // Ensure customer exists in Xero
  const contactId = await ensureContact(order.user);

  // Map order to Xero invoice format
  const invoiceData = mapOrderToInvoice(order, contactId);

  // Create invoice in Xero
  const invoices = await xero.accountingApi.createInvoices(
    await getTenantId(),
    { invoices: [invoiceData] }
  );

  const xeroInvoiceId = invoices.body.invoices?.[0]?.invoiceID;

  // Update order with Xero reference
  await prisma.order.update({
    where: { id: orderId },
    data: {
      xero_invoice_id: xeroInvoiceId,
    },
  });

  return xeroInvoiceId!;
}

async function ensureContact(user: User): Promise<string> {
  const xero = await getXeroClient();
  const tenantId = await getTenantId();

  // Check if contact exists
  const existing = await xero.accountingApi.getContacts(tenantId, undefined, `EmailAddress=="${user.email}"`);

  if (existing.body.contacts?.length) {
    return existing.body.contacts[0].contactID!;
  }

  // Create new contact
  const contact = {
    name: user.name,
    emailAddress: user.email,
    phones: user.phone ? [{ phoneType: 'MOBILE', phoneNumber: user.phone }] : [],
  };

  const result = await xero.accountingApi.createContacts(tenantId, { contacts: [contact] });
  return result.body.contacts?.[0]?.contactID!;
}
```

#### Order to Invoice Mapper

```typescript
// src/lib/accounting/mappers/order-to-invoice.ts
import { Invoice, LineItem, LineAmountTypes } from 'xero-node';
import type { Order, OrderItem, Product } from '@prisma/client';

const VAT_ACCOUNT_CODE = '200'; // Output VAT account
const SALES_ACCOUNT_CODE = '400'; // Sales revenue account

export function mapOrderToInvoice(
  order: Order & { items: (OrderItem & { product: Product })[] },
  contactId: string
): Invoice {
  const lineItems: LineItem[] = order.items.map(item => ({
    description: item.product_name,
    quantity: item.quantity,
    unitAmount: item.unit_price,
    accountCode: SALES_ACCOUNT_CODE,
    taxType: order.items[0].product.vat_applicable ? 'OUTPUT' : 'NONE',
    lineAmount: item.total_price,
  }));

  // Add shipping as line item if applicable
  if (order.shipping_cost > 0) {
    lineItems.push({
      description: 'Shipping',
      quantity: 1,
      unitAmount: order.shipping_cost,
      accountCode: SALES_ACCOUNT_CODE,
      taxType: 'OUTPUT', // VAT on shipping
    });
  }

  return {
    type: Invoice.TypeEnum.ACCREC, // Accounts Receivable
    contact: { contactID: contactId },
    date: order.created_at.toISOString().split('T')[0],
    dueDate: getDueDate(order.created_at),
    lineAmountTypes: LineAmountTypes.Exclusive, // Prices exclude VAT
    lineItems,
    reference: order.order_number,
    status: Invoice.StatusEnum.AUTHORISED,
    currencyCode: 'ZAR',
  };
}

function getDueDate(orderDate: Date): string {
  const due = new Date(orderDate);
  due.setDate(due.getDate() + 7); // 7-day payment terms
  return due.toISOString().split('T')[0];
}
```

#### Payment Recording

```typescript
// src/lib/accounting/sync/payments.ts
import { getXeroClient } from '../xero/auth';
import { Payment } from 'xero-node';
import prisma from '@/lib/prisma';

const PAYMENT_ACCOUNTS = {
  PAYFAST: '090', // PayFast clearing account
  YOCO: '091',    // Yoco clearing account
  EFT: '092',     // EFT clearing account
};

export async function recordPayment(
  orderId: number,
  provider: 'PAYFAST' | 'YOCO' | 'EFT',
  transactionRef: string
): Promise<void> {
  const xero = await getXeroClient();
  const tenantId = await getTenantId();

  const order = await prisma.order.findUnique({
    where: { id: orderId },
  });

  if (!order?.xero_invoice_id) {
    throw new Error('No Xero invoice for this order');
  }

  const payment: Payment = {
    invoice: { invoiceID: order.xero_invoice_id },
    account: { code: PAYMENT_ACCOUNTS[provider] },
    date: new Date().toISOString().split('T')[0],
    amount: order.total,
    reference: transactionRef,
  };

  await xero.accountingApi.createPayment(tenantId, payment);

  // Update order payment reference
  await prisma.order.update({
    where: { id: orderId },
    data: {
      xero_payment_recorded: true,
    },
  });
}
```

#### Admin Connection UI

```typescript
// src/app/admin/settings/accounting/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useToast } from '@/components/Toast';

export default function AccountingSettingsPage() {
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [lastSync, setLastSync] = useState<string | null>(null);
  const { showToast } = useToast();

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    const response = await fetch('/api/admin/accounting/status');
    const data = await response.json();
    setConnected(data.connected);
    setLastSync(data.lastSync);
  };

  const handleConnect = async () => {
    setConnecting(true);
    const response = await fetch('/api/admin/accounting/connect');
    const { authUrl } = await response.json();
    window.location.href = authUrl;
  };

  const handleDisconnect = async () => {
    await fetch('/api/admin/accounting/disconnect', { method: 'POST' });
    setConnected(false);
    showToast('Xero disconnected', 'success');
  };

  const handleSync = async () => {
    try {
      await fetch('/api/admin/accounting/sync', { method: 'POST' });
      showToast('Sync started', 'success');
    } catch (error) {
      showToast('Sync failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Accounting Integration</h1>

      <div className="bg-white dark:bg-secondary-800 p-6 rounded-lg border border-gray-200 dark:border-secondary-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <img src="/xero-logo.png" alt="Xero" className="h-10" />
            <div>
              <h3 className="font-semibold">Xero Accounting</h3>
              <p className="text-sm text-gray-500">
                {connected ? 'Connected' : 'Not connected'}
              </p>
            </div>
          </div>
          {connected ? (
            <div className="flex gap-2">
              <button
                onClick={handleSync}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Sync Now
              </button>
              <button
                onClick={handleDisconnect}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Disconnect
              </button>
            </div>
          ) : (
            <button
              onClick={handleConnect}
              disabled={connecting}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {connecting ? 'Connecting...' : 'Connect to Xero'}
            </button>
          )}
        </div>

        {connected && lastSync && (
          <p className="mt-4 text-sm text-gray-500">
            Last synced: {new Date(lastSync).toLocaleString()}
          </p>
        )}
      </div>

      {/* Sync settings */}
      {connected && (
        <div className="bg-white dark:bg-secondary-800 p-6 rounded-lg border border-gray-200 dark:border-secondary-700">
          <h3 className="font-semibold mb-4">Sync Settings</h3>
          <div className="space-y-4">
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span>Auto-create invoices for new orders</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="rounded" />
              <span>Auto-record payments when confirmed</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" className="rounded" />
              <span>Sync inventory quantities</span>
            </label>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Database Schema Updates

```prisma
model Order {
  // ... existing fields
  xero_invoice_id       String?   @unique
  xero_payment_recorded Boolean   @default(false)
}

model XeroConnection {
  id            Int      @id @default(1)
  tenant_id     String
  access_token  String   @db.Text
  refresh_token String   @db.Text
  expires_at    DateTime
  updated_at    DateTime @updatedAt
}
```

### Environment Variables

```bash
# Xero
XERO_CLIENT_ID=xxx
XERO_CLIENT_SECRET=xxx
XERO_REDIRECT_URI=https://twinesandstraps.co.za/api/admin/accounting/callback
```

### Implementation Timeline

**Phase 1: Connection & Invoicing (Sprint 1)**
- [ ] Set up Xero developer account
- [ ] Implement OAuth flow
- [ ] Build invoice creation from orders
- [ ] Admin connection UI

**Phase 2: Payments & Contacts (Sprint 2)**
- [ ] Implement payment recording
- [ ] Customer contact sync
- [ ] Bank account mapping

**Phase 3: Automation & Reporting (Sprint 3)**
- [ ] Auto-sync triggers
- [ ] Inventory sync (optional)
- [ ] Financial dashboard widgets

### Consequences

**Positive:**
- Automated bookkeeping
- Real-time financial data
- Reduced manual entry errors
- VAT reporting simplified

**Negative:**
- OAuth token management complexity
- Xero subscription cost
- Sync failure handling needed

---

*Last Updated: November 2025*
