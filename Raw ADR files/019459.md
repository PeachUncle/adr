# ADR-004: Email Marketing & Automation Integration

**Status:** Proposed
**Date:** 2025-11-29
**Decision Makers:** Development Team, Marketing Manager
**Technical Story:** Implement email marketing, transactional emails, and automation

## Context and Problem Statement

Twines and Straps needs email capabilities for:

1. **Transactional Emails:** Order confirmations, shipping updates, password resets
2. **Marketing Emails:** Newsletters, promotions, product announcements
3. **Automated Workflows:** Welcome series, abandoned cart, post-purchase follow-ups
4. **Segmentation:** Different messaging for B2B vs B2C customers

## Decision Drivers

- **Deliverability:** High inbox placement rates
- **Pricing:** Cost-effective for growing email list
- **Automation:** Visual workflow builder for non-technical users
- **API Quality:** Developer-friendly integration
- **POPIA Compliance:** Support for SA privacy regulations
- **Transactional Reliability:** High deliverability for critical emails

## Considered Options

### Option 1: Brevo (formerly Sendinblue)

| Aspect | Details |
|--------|---------|
| **Free Tier** | 300 emails/day |
| **Paid Plans** | From $25/month for 20K emails |
| **Features** | Transactional + Marketing, SMS, Automation |
| **API** | REST API, SMTP relay |
| **Deliverability** | 95%+ inbox rate |

**Pros:**
- Combined transactional + marketing platform
- Affordable pricing
- Good automation builder
- GDPR/POPIA compliant features
- SMS capability (future use)

**Cons:**
- Less sophisticated segmentation than enterprise tools
- Template builder less polished than Mailchimp

### Option 2: Mailchimp

| Aspect | Details |
|--------|---------|
| **Free Tier** | 500 contacts, 1K emails/month |
| **Paid Plans** | From $13/month |
| **Features** | Marketing-focused, good templates |
| **API** | REST API |

**Pros:**
- Best template builder
- Strong brand recognition
- Excellent analytics

**Cons:**
- Expensive at scale
- Transactional requires separate product (Mandrill)
- Free tier very limited

### Option 3: Resend (Transactional) + Brevo (Marketing)

**Description:** Use Resend for transactional emails, Brevo for marketing.

**Pros:**
- Best-in-class transactional delivery
- Modern React email templates
- Marketing flexibility with Brevo

**Cons:**
- Two platforms to manage
- Higher complexity

## Decision Outcome

**Chosen Option: Option 1 - Brevo (All-in-One)**

### Rationale

1. **Single Platform:** Unified for transactional and marketing
2. **Cost-Effective:** Good free tier, reasonable scaling
3. **Automation:** Built-in workflow builder
4. **Future-Ready:** SMS capability for SA market
5. **Compliance:** POPIA-friendly consent management

### Implementation Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     Application Layer                          │
├────────────────────────────────────────────────────────────────┤
│  Transactional           Marketing              Automation      │
│  ─────────────           ─────────              ──────────      │
│  • Order Confirmation    • Newsletter           • Welcome       │
│  • Shipping Update       • Promotions           • Abandoned     │
│  • Password Reset        • Product Launch       • Re-engage     │
│  • Review Request        • Announcements        • Post-Purchase │
└───────────────┬───────────────────┬──────────────────┬─────────┘
                │                   │                   │
                ▼                   ▼                   ▼
┌───────────────────────────────────────────────────────────────┐
│                    Brevo Email Service                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  SMTP API   │  │  REST API    │  │  Automation Engine  │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
│                           │                                    │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  Templates  │  │   Contacts   │  │     Analytics       │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

### Technical Specification

#### File Structure

```
src/lib/email/
├── brevo/
│   ├── config.ts          # API configuration
│   ├── client.ts          # Brevo API client
│   └── contacts.ts        # Contact management
├── templates/
│   ├── order-confirmation.tsx
│   ├── shipping-update.tsx
│   ├── password-reset.tsx
│   ├── welcome.tsx
│   └── abandoned-cart.tsx
├── transactional.ts       # Send transactional emails
├── marketing.ts           # Campaign management
└── automation.ts          # Trigger automation workflows
```

#### Brevo Client Setup

```typescript
// src/lib/email/brevo/client.ts
import * as SibApiV3Sdk from '@sendinblue/client';

const apiInstance = new SibApiV3Sdk.TransactionalEmailsApi();
apiInstance.setApiKey(
  SibApiV3Sdk.TransactionalEmailsApiApiKeys.apiKey,
  process.env.BREVO_API_KEY!
);

const contactsInstance = new SibApiV3Sdk.ContactsApi();
contactsInstance.setApiKey(
  SibApiV3Sdk.ContactsApiApiKeys.apiKey,
  process.env.BREVO_API_KEY!
);

export { apiInstance as transactionalApi, contactsInstance as contactsApi };
```

#### Transactional Email Service

```typescript
// src/lib/email/transactional.ts
import { transactionalApi } from './brevo/client';
import * as SibApiV3Sdk from '@sendinblue/client';
import { render } from '@react-email/render';
import { OrderConfirmationEmail } from './templates/order-confirmation';
import type { Order } from '@prisma/client';

export async function sendOrderConfirmation(order: Order & { user: User; items: OrderItem[] }) {
  const html = render(OrderConfirmationEmail({ order }));

  const sendSmtpEmail = new SibApiV3Sdk.SendSmtpEmail();
  sendSmtpEmail.subject = `Order Confirmation #${order.order_number}`;
  sendSmtpEmail.htmlContent = html;
  sendSmtpEmail.sender = {
    name: 'Twines and Straps',
    email: 'orders@twinesandstraps.co.za',
  };
  sendSmtpEmail.to = [
    {
      email: order.user.email,
      name: order.user.name,
    },
  ];
  sendSmtpEmail.tags = ['order-confirmation'];

  try {
    await transactionalApi.sendTransacEmail(sendSmtpEmail);
    console.log(`Order confirmation sent to ${order.user.email}`);
  } catch (error) {
    console.error('Failed to send order confirmation:', error);
    throw error;
  }
}

export async function sendShippingUpdate(
  email: string,
  data: { orderNumber: string; status: string; trackingUrl: string }
) {
  const html = render(ShippingUpdateEmail(data));

  const sendSmtpEmail = new SibApiV3Sdk.SendSmtpEmail();
  sendSmtpEmail.subject = `Shipping Update for Order #${data.orderNumber}`;
  sendSmtpEmail.htmlContent = html;
  sendSmtpEmail.sender = {
    name: 'Twines and Straps',
    email: 'shipping@twinesandstraps.co.za',
  };
  sendSmtpEmail.to = [{ email }];
  sendSmtpEmail.tags = ['shipping-update'];

  await transactionalApi.sendTransacEmail(sendSmtpEmail);
}

export async function sendPasswordReset(email: string, resetUrl: string) {
  const html = render(PasswordResetEmail({ resetUrl }));

  const sendSmtpEmail = new SibApiV3Sdk.SendSmtpEmail();
  sendSmtpEmail.subject = 'Reset Your Password - Twines and Straps';
  sendSmtpEmail.htmlContent = html;
  sendSmtpEmail.sender = {
    name: 'Twines and Straps',
    email: 'noreply@twinesandstraps.co.za',
  };
  sendSmtpEmail.to = [{ email }];
  sendSmtpEmail.tags = ['password-reset'];

  await transactionalApi.sendTransacEmail(sendSmtpEmail);
}
```

#### Email Templates (React Email)

```typescript
// src/lib/email/templates/order-confirmation.tsx
import {
  Body,
  Container,
  Head,
  Heading,
  Html,
  Link,
  Preview,
  Section,
  Text,
  Row,
  Column,
} from '@react-email/components';

interface OrderConfirmationEmailProps {
  order: {
    order_number: string;
    items: Array<{
      product_name: string;
      quantity: number;
      unit_price: number;
    }>;
    subtotal: number;
    vat_amount: number;
    shipping_cost: number;
    total: number;
    user: { name: string };
  };
}

export function OrderConfirmationEmail({ order }: OrderConfirmationEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Order #{order.order_number} confirmed</Preview>
      <Body style={main}>
        <Container style={container}>
          <Heading style={h1}>Order Confirmed!</Heading>
          <Text style={text}>
            Hi {order.user.name}, thank you for your order!
          </Text>
          <Section style={orderSection}>
            <Text style={orderNumber}>Order #{order.order_number}</Text>
            {order.items.map((item, index) => (
              <Row key={index} style={itemRow}>
                <Column>
                  <Text style={itemName}>{item.product_name}</Text>
                  <Text style={itemQty}>Qty: {item.quantity}</Text>
                </Column>
                <Column align="right">
                  <Text style={itemPrice}>R{(item.unit_price * item.quantity).toFixed(2)}</Text>
                </Column>
              </Row>
            ))}
            <Row style={totalRow}>
              <Column><Text>Subtotal</Text></Column>
              <Column align="right"><Text>R{order.subtotal.toFixed(2)}</Text></Column>
            </Row>
            <Row style={totalRow}>
              <Column><Text>VAT (15%)</Text></Column>
              <Column align="right"><Text>R{order.vat_amount.toFixed(2)}</Text></Column>
            </Row>
            <Row style={totalRow}>
              <Column><Text>Shipping</Text></Column>
              <Column align="right"><Text>R{order.shipping_cost.toFixed(2)}</Text></Column>
            </Row>
            <Row style={grandTotalRow}>
              <Column><Text style={grandTotalText}>Total</Text></Column>
              <Column align="right"><Text style={grandTotalText}>R{order.total.toFixed(2)}</Text></Column>
            </Row>
          </Section>
          <Link href={`https://twinesandstraps.co.za/profile/orders/${order.order_number}`} style={button}>
            View Order Status
          </Link>
          <Text style={footer}>
            Questions? Contact us at info@twinesandstraps.co.za
          </Text>
        </Container>
      </Body>
    </Html>
  );
}

const main = { backgroundColor: '#f6f9fc', fontFamily: 'Arial, sans-serif' };
const container = { margin: '0 auto', padding: '40px 20px', maxWidth: '600px' };
const h1 = { color: '#E31E24', fontSize: '24px', fontWeight: 'bold' };
// ... more styles
```

#### Contact Management

```typescript
// src/lib/email/brevo/contacts.ts
import { contactsApi } from './client';
import * as SibApiV3Sdk from '@sendinblue/client';

export async function createOrUpdateContact(
  email: string,
  attributes: {
    FIRSTNAME?: string;
    LASTNAME?: string;
    COMPANY?: string;
    CUSTOMER_TYPE?: 'B2B' | 'B2C';
    TOTAL_ORDERS?: number;
    TOTAL_SPENT?: number;
  },
  listIds: number[] = []
) {
  const createContact = new SibApiV3Sdk.CreateContact();
  createContact.email = email;
  createContact.attributes = attributes;
  createContact.listIds = listIds;
  createContact.updateEnabled = true; // Update if exists

  try {
    await contactsApi.createContact(createContact);
  } catch (error) {
    // Handle duplicate - update instead
    if (error.response?.status === 400) {
      const updateContact = new SibApiV3Sdk.UpdateContact();
      updateContact.attributes = attributes;
      await contactsApi.updateContact(email, updateContact);
    } else {
      throw error;
    }
  }
}

export async function addToList(email: string, listId: number) {
  const contactEmails = new SibApiV3Sdk.AddContactToList();
  contactEmails.emails = [email];
  await contactsApi.addContactToList(listId, contactEmails);
}

export async function removeFromList(email: string, listId: number) {
  const contactEmails = new SibApiV3Sdk.RemoveContactFromList();
  contactEmails.emails = [email];
  await contactsApi.removeContactFromList(listId, contactEmails);
}
```

#### Automation Triggers

```typescript
// src/lib/email/automation.ts
import { transactionalApi } from './brevo/client';
import * as SibApiV3Sdk from '@sendinblue/client';

// Brevo Automation IDs (configured in Brevo dashboard)
const AUTOMATION_IDS = {
  WELCOME_SERIES: 1,
  ABANDONED_CART: 2,
  POST_PURCHASE: 3,
  WIN_BACK: 4,
};

export async function triggerWelcomeSeries(email: string, name: string) {
  // Add contact to welcome automation in Brevo
  // This triggers the pre-built workflow in Brevo dashboard
  await createOrUpdateContact(email, { FIRSTNAME: name }, [AUTOMATION_IDS.WELCOME_SERIES]);
}

export async function triggerAbandonedCart(
  email: string,
  cartItems: Array<{ name: string; price: number; imageUrl: string }>
) {
  // Send transactional email for abandoned cart
  const sendSmtpEmail = new SibApiV3Sdk.SendSmtpEmail();
  sendSmtpEmail.templateId = 1; // Abandoned cart template ID in Brevo
  sendSmtpEmail.to = [{ email }];
  sendSmtpEmail.params = {
    CART_ITEMS: cartItems,
    CART_URL: 'https://twinesandstraps.co.za/cart',
  };

  await transactionalApi.sendTransacEmail(sendSmtpEmail);
}

export async function triggerReviewRequest(orderId: string, email: string, productNames: string[]) {
  // Delay and send review request (handled by Brevo automation)
  const sendSmtpEmail = new SibApiV3Sdk.SendSmtpEmail();
  sendSmtpEmail.templateId = 2; // Review request template
  sendSmtpEmail.to = [{ email }];
  sendSmtpEmail.params = {
    ORDER_ID: orderId,
    PRODUCTS: productNames.join(', '),
    REVIEW_URL: `https://twinesandstraps.co.za/review?order=${orderId}`,
  };
  sendSmtpEmail.scheduledAt = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000); // 14 days later

  await transactionalApi.sendTransacEmail(sendSmtpEmail);
}
```

### Newsletter Signup Integration

```typescript
// src/app/api/newsletter/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createOrUpdateContact, addToList } from '@/lib/email/brevo/contacts';
import { z } from 'zod';

const NEWSLETTER_LIST_ID = 3; // Newsletter list in Brevo

const subscribeSchema = z.object({
  email: z.string().email(),
  name: z.string().optional(),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, name } = subscribeSchema.parse(body);

    await createOrUpdateContact(
      email,
      { FIRSTNAME: name?.split(' ')[0] || '' },
      [NEWSLETTER_LIST_ID]
    );

    return NextResponse.json({ success: true, message: 'Subscribed successfully' });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: 'Invalid email' }, { status: 400 });
    }
    console.error('Newsletter subscription error:', error);
    return NextResponse.json({ error: 'Subscription failed' }, { status: 500 });
  }
}
```

### Environment Variables

```bash
# Brevo
BREVO_API_KEY=xkeysib-xxx
BREVO_SMTP_HOST=smtp-relay.brevo.com
BREVO_SMTP_PORT=587
BREVO_SMTP_USER=xxx
BREVO_SMTP_PASSWORD=xxx
```

### Email List Segmentation

| List ID | Name | Criteria |
|---------|------|----------|
| 1 | All Customers | Registered + purchased |
| 2 | B2B Customers | Company email or high value |
| 3 | Newsletter | Opted in via form |
| 4 | Abandoned Cart | Cart but no purchase |
| 5 | VIP | LTV > R10,000 |

### Automation Workflows

1. **Welcome Series (3 emails)**
   - Day 0: Welcome + brand story
   - Day 3: Popular products + buying guide
   - Day 7: First purchase incentive (10% off)

2. **Abandoned Cart (3 emails)**
   - Hour 1: "Forgot something?"
   - Hour 24: Product benefits + urgency
   - Hour 72: Limited-time discount

3. **Post-Purchase (3 emails)**
   - Day 3: Usage tips for purchased products
   - Day 14: Review request
   - Day 30: Related products recommendation

4. **Win-Back (2 emails)**
   - Day 60: "We miss you" + new arrivals
   - Day 90: Special comeback offer

### Implementation Timeline

**Phase 1: Transactional Emails (Sprint 1)**
- [ ] Set up Brevo account
- [ ] Create email templates
- [ ] Implement order confirmation
- [ ] Implement shipping updates
- [ ] Implement password reset

**Phase 2: Contact Management (Sprint 2)**
- [ ] Sync existing customers to Brevo
- [ ] Implement newsletter signup
- [ ] Set up list segmentation
- [ ] Build customer attribute sync

**Phase 3: Automation (Sprint 3)**
- [ ] Build automation workflows in Brevo
- [ ] Implement trigger hooks
- [ ] Set up abandoned cart detection
- [ ] Test all workflows

### Metrics to Track

- Open rate (target: 25%+)
- Click rate (target: 4%+)
- Unsubscribe rate (target: <0.5%)
- Revenue per email
- Automation conversion rates

---

*Last Updated: November 2025*
