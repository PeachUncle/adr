# ADR-001: Enhanced SOTA Architecture for Southern Haulers TMS

**Date**: 2025-10-23
**Status**: Approved
**Context**: Recursive enhancement initiative to build infinitely scalable, world-class drayage TMS

## Decision

Implement a **microservices-inspired, event-driven, multi-tenant SaaS architecture** with the following pillars:

### 1. Monorepo Structure (Turborepo)

```
southernhaulers/
├── apps/
│   ├── web/                    # Customer portal (Next.js 15)
│   ├── admin/                  # Dispatch & billing (Next.js 15)
│   ├── driver/                 # Driver PWA (Next.js 15 + Offline)
│   ├── recruiting/             # AI hiring engine (Next.js 15)
│   └── quote-crm/              # Proprietary CPQ (Next.js 15)
├── packages/
│   ├── ui/                     # Design system (Tailwind + Radix)
│   ├── db/                     # Supabase client + types
│   ├── auth/                   # WorkOS + Supabase auth
│   ├── agents/                 # Agentic operations (Appointment, Exception, Compliance)
│   ├── observability/          # OpenTelemetry setup
│   ├── portpro/                # PortPro integration mappers
│   └── domain/                 # Core domain logic
│       ├── shipments/
│       ├── quotes/
│       ├── drivers/
│       ├── billing/
│       └── compliance/
├── integration/
│   ├── portpro/                # Webhook handlers, sync workers
│   └── edi/                    # EDI X12 parsers (future)
├── workers/
│   ├── webhook-processor/      # Idempotent webhook handler
│   ├── appointment-agent/      # AI appointment scheduling
│   ├── exception-agent/        # TMF/demurrage risk detection
│   └── compliance-agent/       # TWIC/Clearinghouse monitoring
└── docs/
    ├── research/               # MCP-backed research notes
    ├── adr/                    # Architecture decision records
    └── runbooks/               # Operational playbooks
```

### 2. Technology Stack

#### Infrastructure
- **Cloud**: Vercel (apps) + AWS Lambda (workers) + Supabase (data)
- **Database**: Supabase Postgres 16 (with RLS, PostGIS, pgvector)
- **Message Queue**: Redis Streams (or AWS SQS for scale)
- **Auth**: WorkOS (enterprise SSO) + Supabase Auth (drivers/customers)
- **Observability**: OpenTelemetry + Datadog
- **CDN**: Vercel Edge Network + Cloudflare (DNS)

#### Backend
- **Framework**: Next.js 15 App Router (Server Actions, API Routes)
- **Language**: TypeScript 5.3+ (strict mode)
- **ORM**: Drizzle ORM (type-safe, edge-friendly)
- **Validation**: Zod schemas (shared across client/server)
- **API**: tRPC (type-safe client-server) + REST webhooks

#### Frontend
- **Framework**: React 19 (Next.js 15)
- **Styling**: Tailwind CSS 4 + Radix UI (shadcn/ui)
- **State**: Zustand (global) + React Query (server state)
- **Forms**: React Hook Form + Zod
- **Maps**: MapLibre GL JS + PostGIS (geofencing)
- **Charts**: Tremor (analytics dashboards)

### 3. Event-Driven Architecture

#### Event Flow
```
External Event (PortPro Webhook)
  ↓
[API Route: /api/webhooks/portpro]
  ↓ (verify signature, fast ACK <200ms)
[Redis Stream: "portpro-events"]
  ↓ (competing consumers)
[Worker: webhook-processor]
  ↓ (idempotent handler, event_id deduplication)
[Domain Service: ShipmentService]
  ↓ (update DB, emit internal events)
[Internal Event Stream: "shipment-events"]
  ↓ (fan-out to multiple consumers)
┌─────────────────┬──────────────────┬────────────────┐
│ Billing Agent   │ Exception Agent  │ Analytics      │
│ (invoice calc)  │ (risk detection) │ (dashboards)   │
└─────────────────┴──────────────────┴────────────────┘
```

#### Idempotency Strategy
- **Idempotency Key**: `event_id + resource_version` (PortPro events)
- **Storage**: Redis (TTL: 7 days) + Postgres (audit log)
- **Guarantee**: Duplicate events produce identical DB state

#### Dead Letter Queue (DLQ)
- Failed events after 6 retries → `dlq` Redis stream
- **Admin Dashboard**: DLQ viewer with manual reprocessing
- **Alerts**: Slack/PagerDuty if DLQ depth >10

### 4. Multi-Tenant Architecture

#### Tenancy Model: Hybrid (Pool + Silo)
- **SMB Customers** (0-50 trucks): Shared DB, `org_id` partitioning (RLS)
- **Enterprise Customers** (50+ trucks): Dedicated DB (Supabase project per org)
- **Routing**: Subdomain-based tenant resolution (`acme.southernhaulers.net`)

#### Row-Level Security (RLS)
- **Postgres RLS Policies**: Enforce tenant isolation at DB layer
- **Session Context**: `SET LOCAL app.current_org_id = $1`
- **Example Policy**:
  ```sql
  CREATE POLICY tenant_isolation ON shipments
    USING (org_id = current_setting('app.current_org_id')::uuid);
  ```

#### ABAC (Attribute-Based Access Control) - Optional
- **User Roles**: `admin`, `dispatcher`, `driver`, `customer`, `accountant`
- **Permissions**: `shipments:read`, `shipments:create`, `invoices:approve`
- **Implementation**: WorkOS Roles + custom permission check middleware

### 5. PortPro Integration (Feature-Flagged)

#### Authority Model (Flexible System of Record)
```typescript
// packages/domain/config/authority.ts
export const authorityConfig = {
  loads_status_invoices: env.PORTPRO_ENABLED ? 'portpro' : 'southernhaulers',
  quotes_pricing: 'southernhaulers', // Always internal
  drivers_assets: env.DRIVERS_AUTHORITY || 'portpro',
};
```

#### Integration Mapper Pattern
```typescript
// packages/portpro/mappers/shipment.ts
export class PortProShipmentMapper {
  toDomain(portProLoad: PortProLoad): Shipment {
    // Map PortPro "Load" → Southern Haulers "Shipment"
  }

  fromDomain(shipment: Shipment): PortProLoadUpdate {
    // Map Southern Haulers "Shipment" → PortPro update payload
  }
}
```

#### Webhook Handler (Idempotent)
```typescript
// app/api/webhooks/portpro/route.ts
export async function POST(req: Request) {
  // 1. Verify signature (HMAC-SHA256)
  const signature = req.headers.get('x-portpro-signature');
  if (!verifySignature(body, signature)) return new Response('Unauthorized', { status: 401 });

  // 2. Fast ACK (< 200ms)
  const event = await req.json();
  await redis.xadd('portpro-events', '*', event);

  return new Response('OK', { status: 200 });
}
```

#### Sync Worker (Competing Consumers)
```typescript
// workers/webhook-processor/portpro.ts
export async function processPortProEvent(event: PortProEvent) {
  const idempotencyKey = `portpro:${event.event_id}:${event.resource_version}`;

  // Check idempotency (Redis)
  if (await redis.exists(idempotencyKey)) {
    logger.info('Duplicate event, skipping', { event_id: event.event_id });
    return;
  }

  // Process event (domain service)
  await shipmentService.handlePortProUpdate(event);

  // Mark as processed (7-day TTL)
  await redis.setex(idempotencyKey, 604800, 'processed');
}
```

### 6. Programmatic SEO Infrastructure

#### Routes
```
/usa/[state]/[city]           # e.g., /usa/georgia/savannah
/services/[service]           # e.g., /services/container-drayage
/industries/[industry]        # e.g., /industries/agriculture
/terminals/[terminal]         # e.g., /terminals/port-of-savannah
```

#### Metadata Generation (ISR)
```typescript
// app/usa/[state]/[city]/page.tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const { state, city } = params;

  return {
    title: `Drayage Services in ${city}, ${state} | Southern Haulers`,
    description: `Top-rated container drayage, bulk hauling, and warehouse services in ${city}. 300+ container storage capacity. Get a quote today.`,
    openGraph: {
      images: [`/api/og?location=${city},${state}`],
    },
  };
}
```

#### JSON-LD Structured Data
```typescript
// components/seo/LocalBusinessSchema.tsx
export function LocalBusinessSchema({ city, state }: Props) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "MovingCompany",
    "name": "Southern Haulers",
    "areaServed": { "@type": "City", "name": city, "containedInPlace": state },
    "serviceType": ["Container Drayage", "Bulk Hauling", "Warehouse Services"],
    "priceRange": "$$",
    // ... full LocalBusiness schema
  };

  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />;
}
```

#### Multi-Sitemap Strategy
```
/sitemap.xml               # Index sitemap
/sitemap-pages.xml         # Static pages
/sitemap-locations.xml     # State/city pages (50 states × ~100 cities = 5,000 URLs)
/sitemap-services.xml      # Service pages
/sitemap-blog.xml          # Blog posts (future)
```

### 7. Quote CRM / CPQ Module

#### Data Model
```typescript
// packages/db/schema/quotes.ts
export const deals = pgTable('deals', {
  id: uuid('id').primaryKey().defaultRandom(),
  org_id: uuid('org_id').notNull().references(() => organizations.id),
  customer_id: uuid('customer_id').references(() => customers.id),
  status: dealStatus('status').notNull(), // draft, quoted, approved, converted, lost
  pipeline_stage: text('pipeline_stage'), // discovery, qualification, proposal, negotiation, closed
  created_by: uuid('created_by').references(() => users.id),
  created_at: timestamp('created_at').defaultNow(),
});

export const quotes = pgTable('quotes', {
  id: uuid('id').primaryKey().defaultRandom(),
  deal_id: uuid('deal_id').references(() => deals.id),
  version: integer('version').notNull().default(1),

  // Shipment details
  origin: jsonb('origin'), // { city, state, terminal, address }
  destination: jsonb('destination'),
  container_type: text('container_type'), // 20ft, 40ft, 40ft-HC, 45ft
  cargo_type: text('cargo_type'), // agriculture, general, refrigerated

  // Pricing
  base_rate: decimal('base_rate', { precision: 10, scale: 2 }),
  accessorials: jsonb('accessorials'), // [{ type: 'tmf', amount: 75 }, { type: 'per_diem', days: 5, rate: 100 }]
  total: decimal('total', { precision: 10, scale: 2 }),

  // Approval workflow
  approval_status: approvalStatus('approval_status'), // pending, approved, rejected
  approved_by: uuid('approved_by').references(() => users.id),
  approved_at: timestamp('approved_at'),

  created_at: timestamp('created_at').defaultNow(),
});
```

#### Approval Workflow
```typescript
// packages/domain/quotes/approval.ts
export class QuoteApprovalService {
  async requestApproval(quoteId: string, requesterId: string) {
    // Check if user has approval authority (RBAC)
    // If over threshold → require manager approval
    // Trigger email/Slack notification
  }

  async approve(quoteId: string, approverId: string) {
    // Validate approver has permission
    // Update quote.approval_status = 'approved'
    // Emit event: "quote.approved"
  }

  async convertToShipment(quoteId: string) {
    // Create shipment from approved quote
    // Set deal.status = 'converted'
    // Emit event: "deal.won"
  }
}
```

### 8. Agentic Operations

#### Appointment Agent
```typescript
// packages/agents/appointment/scheduler.ts
export class AppointmentAgent {
  async suggestSlots(shipmentId: string): Promise<AppointmentSlot[]> {
    // 1. Fetch terminal rules (PostGIS: operating hours, cutoffs)
    const terminal = await getTerminalRules(shipment.destination);

    // 2. Check driver availability (calendar integration)
    const drivers = await getAvailableDrivers(shipment.pickup_date);

    // 3. Predict congestion (historical data + current queue depth)
    const congestionRisk = await predictCongestion(terminal.id, shipment.appointment_date);

    // 4. Generate candidate slots (optimization algorithm)
    const slots = generateOptimalSlots({
      terminal,
      drivers,
      congestionRisk,
      constraints: { earliest: '08:00', latest: '16:00', duration: '2h' },
    });

    return slots.map(slot => ({
      ...slot,
      risk_score: calculateRiskScore(slot),
      reasoning: explainSlotSelection(slot),
    }));
  }
}
```

#### Exception Agent
```typescript
// packages/agents/exception/detector.ts
export class ExceptionAgent {
  async detectRisks(shipmentId: string): Promise<ExceptionAlert[]> {
    const shipment = await getShipment(shipmentId);
    const alerts: ExceptionAlert[] = [];

    // TMF (Terminal Handling Fee) risk
    if (shipment.last_free_day && dayjs().isAfter(shipment.last_free_day)) {
      alerts.push({
        type: 'tmf_exceeded',
        severity: 'high',
        estimated_cost: 75, // per day
        recommended_actions: ['Contact terminal for waiver', 'Expedite pickup'],
      });
    }

    // Per diem risk
    const perDiemDays = dayjs().diff(shipment.container_available_date, 'days');
    if (perDiemDays > shipment.free_days) {
      alerts.push({
        type: 'per_diem_accruing',
        severity: 'medium',
        estimated_cost: (perDiemDays - shipment.free_days) * 100,
        recommended_actions: ['Return container ASAP', 'Negotiate extended free time'],
      });
    }

    // ETA variance (driver delayed)
    if (shipment.driver && shipment.driver.eta_variance_minutes > 30) {
      alerts.push({
        type: 'driver_delayed',
        severity: 'medium',
        recommended_actions: ['Notify customer', 'Reschedule appointment if needed'],
      });
    }

    return alerts;
  }
}
```

#### Compliance Agent
```typescript
// packages/agents/compliance/monitor.ts
export class ComplianceAgent {
  async checkDriverCompliance(driverId: string): Promise<ComplianceStatus> {
    const driver = await getDriver(driverId);
    const blockers: ComplianceBlocker[] = [];

    // TWIC card expiration
    if (driver.twic_expiry && dayjs(driver.twic_expiry).isBefore(dayjs().add(30, 'days'))) {
      blockers.push({
        type: 'twic_expiring',
        severity: 'high',
        action_required: 'Renew TWIC card before port jobs',
        deadline: driver.twic_expiry,
      });
    }

    // Clearinghouse consent
    if (!driver.clearinghouse_consent_date || dayjs().diff(driver.clearinghouse_consent_date, 'years') > 1) {
      blockers.push({
        type: 'clearinghouse_consent_expired',
        severity: 'critical',
        action_required: 'Obtain new Clearinghouse consent',
      });
    }

    // Leasing agreement (49 CFR 376)
    if (driver.is_independent_contractor && !driver.leasing_agreement_signed) {
      blockers.push({
        type: 'leasing_agreement_missing',
        severity: 'critical',
        action_required: 'Sign Truth-in-Leasing agreement',
      });
    }

    return {
      is_compliant: blockers.length === 0,
      blockers,
      can_assign_port_jobs: !blockers.some(b => b.type === 'twic_expiring'),
    };
  }
}
```

### 9. Driver PWA (Progressive Web App)

#### Offline-First Architecture
```typescript
// apps/driver/lib/offline-sync.ts
export class OfflineSyncManager {
  async captureDocument(type: 'pod' | 'bol', file: File, shipmentId: string) {
    const doc = {
      id: crypto.randomUUID(),
      type,
      shipment_id: shipmentId,
      file_data: await fileToBase64(file),
      captured_at: new Date().toISOString(),
      synced: false,
    };

    // Store in IndexedDB
    await db.documents.add(doc);

    // Try immediate sync (if online)
    if (navigator.onLine) {
      await this.syncDocument(doc.id);
    }
  }

  async updateShipmentStatus(shipmentId: string, status: ShipmentStatus) {
    const update = {
      id: crypto.randomUUID(),
      shipment_id: shipmentId,
      status,
      timestamp: new Date().toISOString(),
      synced: false,
    };

    await db.statusUpdates.add(update);

    if (navigator.onLine) {
      await this.syncStatusUpdate(update.id);
    }
  }

  async syncAll() {
    const unsyncedDocs = await db.documents.where('synced').equals(false).toArray();
    const unsyncedUpdates = await db.statusUpdates.where('synced').equals(false).toArray();

    for (const doc of unsyncedDocs) {
      await this.syncDocument(doc.id);
    }

    for (const update of unsyncedUpdates) {
      await this.syncStatusUpdate(update.id);
    }
  }
}
```

#### Service Worker (Background Sync)
```typescript
// apps/driver/public/sw.js
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-shipment-updates') {
    event.waitUntil(syncOfflineData());
  }
});

async function syncOfflineData() {
  // Open IndexedDB and sync all pending updates
  const db = await openDB('driver-app', 1);
  const pending = await db.getAll('pending-updates');

  for (const update of pending) {
    try {
      await fetch('/api/shipments/update', {
        method: 'POST',
        body: JSON.stringify(update),
      });
      await db.delete('pending-updates', update.id);
    } catch (err) {
      console.error('Sync failed, will retry', err);
    }
  }
}
```

### 10. Observability Layer

#### OpenTelemetry Instrumentation
```typescript
// packages/observability/tracing.ts
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
import { ExpressInstrumentation } from '@opentelemetry/instrumentation-express';

export function setupTracing() {
  const provider = new NodeTracerProvider();

  registerInstrumentations({
    instrumentations: [
      new HttpInstrumentation(),
      new ExpressInstrumentation(),
    ],
  });

  provider.register();
}
```

#### Custom Spans
```typescript
// workers/webhook-processor/portpro.ts
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('webhook-processor');

export async function processPortProEvent(event: PortProEvent) {
  const span = tracer.startSpan('process-portpro-event', {
    attributes: {
      'event.id': event.event_id,
      'event.type': event.event_type,
      'resource.type': event.resource_type,
    },
  });

  try {
    // ... processing logic
    span.setStatus({ code: SpanStatusCode.OK });
  } catch (error) {
    span.recordException(error);
    span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
    throw error;
  } finally {
    span.end();
  }
}
```

#### Metrics Dashboard
```typescript
// apps/admin/components/operations/MetricsDashboard.tsx
export function MetricsDashboard() {
  const metrics = useMetrics();

  return (
    <div className="grid grid-cols-4 gap-4">
      <MetricCard
        title="Webhook Success Rate"
        value={metrics.webhook_success_rate}
        target={99.5}
        unit="%"
        trend="up"
      />
      <MetricCard
        title="Queue Depth"
        value={metrics.queue_depth}
        alert={metrics.queue_depth > 1000}
        unit="msgs"
      />
      <MetricCard
        title="DLQ Messages"
        value={metrics.dlq_depth}
        alert={metrics.dlq_depth > 10}
        unit="msgs"
      />
      <MetricCard
        title="API p95 Latency"
        value={metrics.api_p95_latency}
        target={250}
        unit="ms"
        trend="down"
      />
    </div>
  );
}
```

## Rationale

### Why Event-Driven?
- **Decoupling**: Services can scale independently
- **Resilience**: Failure in one service doesn't cascade
- **Auditability**: Event log as immutable source of truth
- **Real-time**: Asynchronous processing for responsiveness

### Why Monorepo?
- **Code Sharing**: Shared packages (ui, db, domain)
- **Atomic Commits**: Change frontend + backend in one PR
- **Developer Experience**: Single repo to clone, consistent tooling
- **Type Safety**: End-to-end TypeScript across all apps

### Why Multi-Tenant?
- **Efficiency**: Single deployment serves all customers
- **Cost**: Shared infrastructure reduces per-customer overhead
- **Speed**: Onboard new customers in minutes (not days)
- **Flexibility**: Hybrid model (pool + silo) for different tiers

### Why PortPro Integration?
- **Time-to-Market**: Leverage existing TMS for load management
- **Risk Mitigation**: Gradual migration vs. big bang replacement
- **Customer Choice**: Allow customers to choose PortPro or native SH
- **Competitive Positioning**: "Best of both worlds" story

### Why Agentic Operations?
- **Differentiation**: No competitor has AI-driven appointment/exception agents
- **ROI**: Reduce TMF/demurrage costs by 30%+ through proactive risk detection
- **Scalability**: Agents handle routine tasks, humans focus on exceptions
- **Innovation**: Demonstrate "TMS of the future" to customers

## Consequences

### Positive
- **Scalability**: Can handle 10x traffic without architecture changes
- **Velocity**: Teams can ship features independently (bounded contexts)
- **Reliability**: Event-driven resilience patterns (retry, DLQ, idempotency)
- **Observability**: Full distributed tracing from webhook → DB → dashboard
- **SEO**: Programmatic pages capture long-tail local search traffic
- **Competitive**: Feature parity with PortPro + unique differentiators

### Negative
- **Complexity**: More moving parts (message queues, workers, multiple apps)
- **Learning Curve**: Team must learn event-driven patterns, OpenTelemetry
- **Operational Overhead**: Monitoring queues, DLQs, and distributed traces

### Mitigations
- **Documentation**: Comprehensive runbooks for common operations
- **Tooling**: Admin dashboards for DLQ management, queue health
- **Training**: Regular architecture review sessions with team
- **Incremental Rollout**: Feature flags allow gradual adoption

## Implementation Plan

### Phase 1: Foundation (Weeks 1-2)
- ✅ Research (SOTA TMS, PortPro, scalability patterns)
- ⏳ Monorepo setup (Turborepo, shared packages)
- ⏳ Database schema design (Supabase + RLS policies)
- ⏳ Auth integration (WorkOS + Supabase Auth)
- ⏳ Design system (Tailwind + Radix UI)

### Phase 2: Core Apps (Weeks 3-6)
- Web app (customer portal)
- Admin app (dispatch, billing, exceptions)
- Driver PWA (offline-capable)
- Quote CRM/CPQ (deal pipeline, approval workflows)

### Phase 3: Integrations (Weeks 7-8)
- PortPro webhook handler (idempotent)
- PortPro sync workers (competing consumers)
- Integration mappers (PortPro ↔ domain)
- Authority swap configuration (per-entity)

### Phase 4: Agentic Ops (Weeks 9-10)
- Appointment Agent (terminal rules + optimization)
- Exception Agent (TMF/per diem risk detection)
- Compliance Agent (TWIC/Clearinghouse monitoring)

### Phase 5: SEO & Growth (Weeks 11-12)
- Programmatic state/city pages (/usa/[state]/[city])
- JSON-LD structured data (LocalBusiness)
- Multi-sitemap generation
- OG image generation (dynamic)

### Phase 6: Observability & Hardening (Week 13-14)
- OpenTelemetry instrumentation
- Metrics dashboards (webhook, queue, API, business)
- Alerting (Slack/PagerDuty)
- Load testing and performance tuning

### Phase 7: Launch (Week 15+)
- Beta customers (feature-flagged)
- Runbooks and operational playbooks
- Team training
- Full production rollout

## Success Metrics

### Technical
- **Web Vitals**: LCP ≤2.5s, CLS ≤0.1, INP ≤200ms
- **API Latency**: p95 ≤250ms
- **Webhook SLO**: ≥99.5% success, <200ms ACK
- **Queue Drain**: >100 msg/s, <1000 queue depth
- **Error Budget**: ≥99.9% success over 30 days

### Business
- **Quote Conversion**: ≥2× industry baseline (15% → 30%)
- **TMF/Demurrage Savings**: 30%+ reduction via exception agent
- **Driver Recruiting**: 10%+ opt-in rate from Meta Lead Ads
- **SEO Traffic**: 5,000+ monthly organic visitors by month 6
- **Customer NPS**: ≥50 (promoters - detractors)

---

**Reviewed by**: Claude Code (Primary Orchestrator)
**Approved by**: Sean Dwivedi (Engineering Lead)
