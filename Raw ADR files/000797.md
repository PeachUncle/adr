---
docid: ADR-087
title: ADR 043 Paid Services Infrastructure
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-043: Paid Services Infrastructure

**Status**: Proposed  
**Date**: 2026-01-06  
**Deciders**: @Architect, @Backend, @ProductOwner, @DevOps  
**Technical Story**: Enable monetization of premium features and add-on services

---

## Context and Problem Statement

B2X needs infrastructure to support additional paid services beyond the core platform. This includes:
- Tiered subscription management per tenant
- Usage-based billing for compute-intensive features
- Feature entitlement checking at service boundaries
- Metering and reporting for billing integration

**Key Questions:**
1. How do we manage subscription tiers and add-ons per tenant?
2. How do we meter usage for consumption-based services?
3. How do we integrate with billing providers?
4. How do we enforce feature access without performance impact?

---

## Decision Drivers

- **Multi-tenancy**: Must integrate with existing tenant architecture [ADR-004]
- **Performance**: Entitlement checks must be fast (<5ms)
- **Flexibility**: Support subscription + usage-based + one-time purchases
- **Auditability**: Full tracking of feature usage and billing events
- **Scalability**: Handle high-volume metering without impacting core services

---

## Considered Options

### Option 1: Feature Flag Service + External Billing (Recommended)
### Option 2: Full Custom Implementation
### Option 3: All-in-One SaaS (Chargebee/Recurly)

---

## Decision Outcome

**Chosen Option**: Option 1 - Feature Flag Service + External Billing

Combines custom entitlement management with proven billing infrastructure.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                              │
│                  (Rate Limiting + Metering)                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                  Entitlement Service                            │
│         (Redis Cache + PostgreSQL Source of Truth)              │
├─────────────────────────────────────────────────────────────────┤
│  • TenantSubscriptionHandler (Wolverine)                        │
│  • FeatureEntitlementQuery                                      │
│  • UsageQuotaEnforcement                                        │
└─────────────────────────┬───────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Subscription │ │    Usage      │ │   Billing     │
│   Database    │ │   Metering    │ │   Provider    │
│  (PostgreSQL) │ │ (TimescaleDB) │ │   (Stripe)    │
└───────────────┘ └───────────────┘ └───────────────┘
```

---

## Detailed Design

### 1. Subscription Tiers

| Tier | Monthly | Features |
|------|---------|----------|
| **Starter** | Free | Core B2B, 1 ERP, 1000 products |
| **Professional** | €149 | API access, 3 ERPs, 50k products, Webhooks |
| **Business** | €449 | Unlimited ERPs, 500k products, Priority support |
| **Enterprise** | Custom | Dedicated resources, SLA, Custom integrations |

### 2. Add-On Services (Usage-Based)

| Service | Unit | Price | Category |
|---------|------|-------|----------|
| AI Product Matching | per 1000 matches | €5 | AI/ML |
| BMEcat Import | per catalog | €25 | Data |
| Advanced Analytics | per report | €2 | Analytics |
| API Overage | per 10k calls | €10 | Platform |
| Additional Users | per user/month | €15 | Platform |

### 3. Premium Third-Party Services (Pass-Through + Margin)

These services require separate customer activation and billing due to external API costs:

#### 3.1 Design & Branding Services

| Service | Provider | Unit | Est. Cost | Customer Price |
|---------|----------|------|-----------|----------------|
| **Figma Design Sync** | Figma API | per sync/month | ~€15/seat | €25/month |
| **Image Resizing** | imgproxy/Cloudinary | per 1000 transforms | €0.50 | €2 |
| **Asset CDN Storage** | Azure Blob/S3 | per GB/month | €0.02 | €0.10 |

**Use Cases**:
- Figma: Sync tenant branding/design tokens from Figma files ([ADR-041])
- Image Resizing: Dynamic product image optimization
- Blob Storage: Extended media storage beyond base quota

#### 3.2 AI & Intelligence Services

| Service | Provider | Unit | Est. Cost | Customer Price |
|---------|----------|------|-----------|----------------|
| **Custom AI Provider** | OpenAI/Azure/Anthropic | per 1M tokens | €2-15 | Cost + 30% |
| **AI Product Descriptions** | GPT-4/Claude | per 100 products | €1-5 | €10 |
| **AI Translation** | DeepL API Pro | per 1M chars | €20 | €35 |

**Use Cases**:
- BYOK (Bring Your Own Key) for AI features
- Bulk product description generation
- Automatic catalog translation

#### 3.3 Legal & Compliance Services

| Service | Provider | Unit | Est. Cost | Customer Price |
|---------|----------|------|-----------|----------------|
| **Legal Text Generator** | [e-recht24 API](https://api-docs.e-recht24.de) | per document | €5-20 | €25-50 |
| **Imprint Generator** | e-recht24 | per generation | €5 | €15 |
| **Privacy Policy** | e-recht24 | per generation | €10 | €30 |
| **Terms & Conditions** | e-recht24 | per generation | €15 | €40 |

**Use Cases**:
- Auto-generate legally compliant imprint for tenant shops
- Privacy policy generation with tenant-specific data
- T&C templates for B2B transactions

#### 3.4 Business Data APIs

| Service | Provider | Unit | Est. Cost | Customer Price |
|---------|----------|------|-----------|----------------|
| **Company Verification** | Creditreform/SCHUFA | per lookup | €0.50-2 | €5 |
| **VAT Validation** | VIES API | per check | Free | €0.10 |
| **Address Validation** | Google/HERE | per 1000 lookups | €4 | €10 |
| **Bank Verification** | IBAN API | per check | €0.02 | €0.50 |

**Use Cases**:
- B2B customer onboarding verification
- Credit check before extending payment terms
- Address standardization for shipping

#### 3.5 Communication Services

| Service | Provider | Unit | Est. Cost | Customer Price |
|---------|----------|------|-----------|----------------|
| **Transactional Email** | SendGrid/Mailjet | per 1000 emails | €0.50 | €2 |
| **SMS Notifications** | Twilio | per SMS | €0.07 | €0.20 |
| **WhatsApp Business** | Twilio/360dialog | per message | €0.05-0.15 | €0.30 |

### 4. Service Activation Model

```
┌─────────────────────────────────────────────────────────────────┐
│                 Premium Service Lifecycle                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Request  │───▶│ Approve  │───▶│ Activate │───▶│  Meter   │  │
│  │ Service  │    │ (Manual/ │    │ API Keys │    │  Usage   │  │
│  │          │    │  Auto)   │    │          │    │          │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                                                                 │
│  Tenant Admin    Payment/        Provisioning   TimescaleDB     │
│  Portal          Credit Check    Service        + Stripe Meter  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5. Domain Model

```csharp
// B2X.Billing.Domain

public sealed record TenantSubscription
{
    public required TenantId TenantId { get; init; }
    public required SubscriptionTier Tier { get; init; }
    public required DateTimeOffset StartedAt { get; init; }
    public DateTimeOffset? ExpiresAt { get; init; }
    public required BillingProvider Provider { get; init; }
    public required string ExternalCustomerId { get; init; }
    public required string ExternalSubscriptionId { get; init; }
    public IReadOnlyList<AddOnSubscription> AddOns { get; init; } = [];
    public UsageQuotas Quotas { get; init; } = UsageQuotas.Default;
    
    public bool IsActive => ExpiresAt is null || ExpiresAt > DateTimeOffset.UtcNow;
    public bool HasFeature(FeatureKey feature) => Tier.Includes(feature) || AddOns.Any(a => a.Provides(feature));
}

public sealed record UsageQuotas
{
    public int MaxProducts { get; init; }
    public int MaxErpConnections { get; init; }
    public int MaxApiCallsPerMonth { get; init; }
    public int MaxUsersIncluded { get; init; }
    
    public static UsageQuotas Default => new()
    {
        MaxProducts = 1000,
        MaxErpConnections = 1,
        MaxApiCallsPerMonth = 10_000,
        MaxUsersIncluded = 3
    };
}

public enum SubscriptionTier
{
    Starter = 0,
    Professional = 10,
    Business = 20,
    Enterprise = 100
}

public sealed record AddOnSubscription
{
    public required AddOnKey Key { get; init; }
    public required int Quantity { get; init; }
    public required DateTimeOffset EnabledAt { get; init; }
}

// Premium third-party service activation
public sealed record PremiumServiceActivation
{
    public required TenantId TenantId { get; init; }
    public required PremiumServiceKey ServiceKey { get; init; }
    public required PremiumServiceStatus Status { get; init; }
    public required DateTimeOffset ActivatedAt { get; init; }
    public DateTimeOffset? DeactivatedAt { get; init; }
    public EncryptedCredentials? TenantCredentials { get; init; } // BYOK support
    public Dictionary<string, string> Configuration { get; init; } = [];
}

public enum PremiumServiceKey
{
    // Design & Branding
    FigmaSync,
    ImageResizing,
    BlobStorage,
    
    // AI & Intelligence
    CustomAiProvider,
    AiProductDescriptions,
    AiTranslation,
    
    // Legal & Compliance
    ERecht24LegalTexts,
    ERecht24Imprint,
    ERecht24PrivacyPolicy,
    ERecht24TermsConditions,
    
    // Business Data
    CompanyVerification,
    VatValidation,
    AddressValidation,
    BankVerification,
    
    // Communication
    TransactionalEmail,
    SmsNotifications,
    WhatsAppBusiness
}

public enum PremiumServiceStatus
{
    Requested,
    PendingApproval,
    Active,
    Suspended,
    Deactivated
}

// Encrypted storage for BYOK (Bring Your Own Key)
public sealed record EncryptedCredentials
{
    public required string EncryptedApiKey { get; init; }
    public required string KeyVaultReference { get; init; }
    public required DateTimeOffset RotatedAt { get; init; }
}
```

### 6. Entitlement Service (Wolverine Handlers)

```csharp
// Query: Check if tenant has feature access
public sealed record CheckFeatureEntitlement(TenantId TenantId, FeatureKey Feature) : IQuery<EntitlementResult>;

public sealed record EntitlementResult(bool Allowed, string? Reason, UsageInfo? CurrentUsage);

public sealed class CheckFeatureEntitlementHandler
{
    public async Task<EntitlementResult> Handle(
        CheckFeatureEntitlement query,
        IEntitlementCache cache,
        ISubscriptionRepository subscriptions,
        CancellationToken ct)
    {
        // 1. Check cache first (Redis, <1ms)
        var cached = await cache.GetEntitlementAsync(query.TenantId, query.Feature, ct);
        if (cached is not null) return cached;
        
        // 2. Load from database
        var subscription = await subscriptions.GetByTenantAsync(query.TenantId, ct);
        if (subscription is null)
            return new EntitlementResult(false, "No active subscription", null);
        
        if (!subscription.IsActive)
            return new EntitlementResult(false, "Subscription expired", null);
        
        var allowed = subscription.HasFeature(query.Feature);
        var result = new EntitlementResult(allowed, allowed ? null : "Feature not included in plan", null);
        
        // 3. Cache result
        await cache.SetEntitlementAsync(query.TenantId, query.Feature, result, TimeSpan.FromMinutes(5), ct);
        
        return result;
    }
}
```

### 5. Usage Metering

```csharp
// Fire-and-forget usage recording via Wolverine
public sealed record RecordUsageEvent(
    TenantId TenantId,
    UsageMetric Metric,
    long Quantity,
    DateTimeOffset OccurredAt,
    Dictionary<string, string>? Metadata = null);

public sealed class RecordUsageEventHandler
{
    public async Task Handle(
        RecordUsageEvent command,
        IUsageMeteringRepository metering,
        IMessageBus bus,
        CancellationToken ct)
    {
        // Store in TimescaleDB for time-series aggregation
        await metering.RecordAsync(new UsageRecord
        {
            TenantId = command.TenantId,
            Metric = command.Metric,
            Quantity = command.Quantity,
            RecordedAt = command.OccurredAt,
            Metadata = command.Metadata
        }, ct);
        
        // Check if quota exceeded → notify
        var currentUsage = await metering.GetCurrentPeriodUsageAsync(command.TenantId, command.Metric, ct);
        var quota = await GetQuotaAsync(command.TenantId, command.Metric, ct);
        
        if (currentUsage >= quota * 0.9m)
        {
            await bus.PublishAsync(new UsageThresholdReached(command.TenantId, command.Metric, currentUsage, quota));
        }
    }
}
```

### 6. Database Schema

```sql
-- Subscription management (PostgreSQL)
CREATE TABLE billing.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    tier VARCHAR(50) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    billing_provider VARCHAR(50) NOT NULL, -- 'stripe', 'manual'
    external_customer_id VARCHAR(255),
    external_subscription_id VARCHAR(255),
    quotas JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id)
);

CREATE INDEX idx_subscriptions_tenant ON billing.subscriptions(tenant_id);
CREATE INDEX idx_subscriptions_expires ON billing.subscriptions(expires_at) WHERE expires_at IS NOT NULL;

-- Add-on services
CREATE TABLE billing.addon_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID NOT NULL REFERENCES billing.subscriptions(id) ON DELETE CASCADE,
    addon_key VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    enabled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    disabled_at TIMESTAMPTZ,
    UNIQUE (subscription_id, addon_key)
);

-- Usage metering (TimescaleDB hypertable)
CREATE TABLE billing.usage_events (
    tenant_id UUID NOT NULL,
    metric VARCHAR(100) NOT NULL,
    quantity BIGINT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB
);

SELECT create_hypertable('billing.usage_events', 'recorded_at');

CREATE INDEX idx_usage_tenant_metric ON billing.usage_events(tenant_id, metric, recorded_at DESC);

-- Billing events (audit trail)
CREATE TABLE billing.billing_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    external_event_id VARCHAR(255),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_billing_events_tenant ON billing.billing_events(tenant_id, occurred_at DESC);

-- Premium third-party service activations
CREATE TABLE billing.premium_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    service_key VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'requested',
    activated_at TIMESTAMPTZ,
    deactivated_at TIMESTAMPTZ,
    configuration JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, service_key)
);

CREATE INDEX idx_premium_services_tenant ON billing.premium_services(tenant_id);
CREATE INDEX idx_premium_services_status ON billing.premium_services(status) WHERE status = 'active';

-- Encrypted credentials for BYOK (stored separately, Azure Key Vault references)
CREATE TABLE billing.premium_service_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    premium_service_id UUID NOT NULL REFERENCES billing.premium_services(id) ON DELETE CASCADE,
    credential_type VARCHAR(50) NOT NULL, -- 'api_key', 'oauth_token', 'client_secret'
    key_vault_secret_name VARCHAR(255) NOT NULL, -- Reference to Azure Key Vault
    rotated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    UNIQUE (premium_service_id, credential_type)
);

-- Third-party API cost tracking (for margin calculation)
CREATE TABLE billing.external_api_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    service_key VARCHAR(100) NOT NULL,
    external_cost_cents BIGINT NOT NULL, -- Actual cost from provider
    billed_amount_cents BIGINT NOT NULL, -- What we charge tenant
    margin_cents BIGINT GENERATED ALWAYS AS (billed_amount_cents - external_cost_cents) STORED,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    reconciled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_external_costs_tenant_period ON billing.external_api_costs(tenant_id, period_start, period_end);
```

### 9. Stripe Integration

```csharp
// Webhook handler for Stripe events
public sealed class StripeWebhookHandler
{
    public async Task Handle(
        StripeWebhookReceived webhook,
        ISubscriptionService subscriptions,
        IMessageBus bus,
        CancellationToken ct)
    {
        var stripeEvent = webhook.Event;
        
        switch (stripeEvent.Type)
        {
            case "customer.subscription.created":
            case "customer.subscription.updated":
                var subscription = stripeEvent.Data.Object as Stripe.Subscription;
                await subscriptions.SyncFromStripeAsync(subscription, ct);
                break;
                
            case "customer.subscription.deleted":
                var deletedSub = stripeEvent.Data.Object as Stripe.Subscription;
                await subscriptions.HandleCancellationAsync(deletedSub.Id, ct);
                break;
                
            case "invoice.payment_failed":
                var invoice = stripeEvent.Data.Object as Stripe.Invoice;
                await bus.PublishAsync(new PaymentFailed(invoice.CustomerId, invoice.Id));
                break;
        }
    }
}
```

### 8. Feature Enforcement Middleware

```csharp
// ASP.NET Core middleware for API rate limiting + feature checks
public class EntitlementMiddleware
{
    private readonly RequestDelegate _next;
    
    public async Task InvokeAsync(
        HttpContext context,
        IEntitlementService entitlements,
        ITenantContext tenant,
        IMessageBus bus)
    {
        var endpoint = context.GetEndpoint();
        var featureAttribute = endpoint?.Metadata.GetMetadata<RequiresFeatureAttribute>();
        
        if (featureAttribute is not null)
        {
            var result = await entitlements.CheckAsync(tenant.Id, featureAttribute.Feature);
            
            if (!result.Allowed)
            {
                context.Response.StatusCode = StatusCodes.Status402PaymentRequired;
                await context.Response.WriteAsJsonAsync(new ProblemDetails
                {
                    Title = "Feature Not Available",
                    Detail = result.Reason ?? "Upgrade your plan to access this feature",
                    Status = 402,
                    Extensions = { ["upgradeUrl"] = "/billing/upgrade" }
                });
                return;
            }
        }
        
        // Record API usage (fire-and-forget)
        _ = bus.PublishAsync(new RecordUsageEvent(
            tenant.Id,
            UsageMetric.ApiCalls,
            1,
            DateTimeOffset.UtcNow));
        
        await _next(context);
    }
}

// Attribute for marking endpoints
[AttributeUsage(AttributeTargets.Method | AttributeTargets.Class)]
public class RequiresFeatureAttribute(FeatureKey feature) : Attribute
{
    public FeatureKey Feature { get; } = feature;
}

// Attribute for premium services
[AttributeUsage(AttributeTargets.Method | AttributeTargets.Class)]
public class RequiresPremiumServiceAttribute(PremiumServiceKey service) : Attribute
{
    public PremiumServiceKey Service { get; } = service;
}

// Usage examples
[RequiresFeature(FeatureKey.AdvancedAnalytics)]
[HttpGet("analytics/advanced")]
public async Task<IActionResult> GetAdvancedAnalytics() { ... }

[RequiresPremiumService(PremiumServiceKey.ERecht24LegalTexts)]
[HttpPost("legal/generate-imprint")]
public async Task<IActionResult> GenerateImprint() { ... }

[RequiresPremiumService(PremiumServiceKey.FigmaSync)]
[HttpPost("design/sync-figma")]
public async Task<IActionResult> SyncFigmaDesign() { ... }
```

### 11. Premium Service Proxy Pattern

```csharp
// Generic proxy for third-party API calls with metering
public interface IPremiumServiceProxy<TRequest, TResponse>
{
    Task<TResponse> ExecuteAsync(TenantId tenantId, TRequest request, CancellationToken ct);
}

// e-recht24 Legal Text Service Implementation
public sealed class ERecht24LegalTextProxy : IPremiumServiceProxy<GenerateLegalTextRequest, LegalTextResponse>
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IPremiumServiceRepository _services;
    private readonly IMessageBus _bus;
    
    public async Task<LegalTextResponse> ExecuteAsync(
        TenantId tenantId, 
        GenerateLegalTextRequest request, 
        CancellationToken ct)
    {
        // 1. Check service activation
        var activation = await _services.GetActivationAsync(tenantId, PremiumServiceKey.ERecht24LegalTexts, ct);
        if (activation?.Status != PremiumServiceStatus.Active)
            throw new PremiumServiceNotActivatedException(PremiumServiceKey.ERecht24LegalTexts);
        
        // 2. Get credentials (from Key Vault)
        var credentials = await _services.GetCredentialsAsync(activation.Id, ct);
        
        // 3. Call external API
        var client = _httpClientFactory.CreateClient("ERecht24");
        client.DefaultRequestHeaders.Authorization = new("Bearer", credentials.ApiKey);
        
        var response = await client.PostAsJsonAsync("/api/v1/texts/generate", request, ct);
        var result = await response.Content.ReadFromJsonAsync<LegalTextResponse>(ct);
        
        // 4. Record usage for billing
        await _bus.PublishAsync(new RecordPremiumUsageEvent(
            tenantId,
            PremiumServiceKey.ERecht24LegalTexts,
            request.DocumentType,
            ExternalCostCents: 1500, // €15 from provider
            BilledAmountCents: 4000  // €40 to customer
        ));
        
        return result!;
    }
}

// Figma API Sync Service
public sealed class FigmaDesignSyncProxy : IPremiumServiceProxy<SyncFigmaRequest, FigmaDesignTokens>
{
    public async Task<FigmaDesignTokens> ExecuteAsync(
        TenantId tenantId, 
        SyncFigmaRequest request, 
        CancellationToken ct)
    {
        // Check activation, get tenant's Figma token (BYOK)
        // Call Figma API: GET /v1/files/{file_key}/variables/local
        // Transform to design tokens
        // Record metered usage
        // Return design tokens for tenant theming
    }
}
```

---

## Consequences

### Positive
- **Flexible monetization**: Support multiple pricing models
- **Performance**: Cached entitlements, async metering
- **Auditability**: Full trail of billing events
- **Scalability**: TimescaleDB handles high-volume metering
- **Integration**: Stripe handles payment complexity
- **BYOK Support**: Tenants can use their own API keys for cost control
- **Margin Tracking**: Clear visibility into external costs vs. revenue

### Negative
- **Complexity**: Multiple systems to maintain
- **External dependency**: Reliance on Stripe + third-party APIs
- **Data sync**: Must keep Stripe and local DB in sync
- **Credential management**: Secure storage of tenant API keys

### Risks
- **Webhook failures**: Implement retry + dead letter queue
- **Cache staleness**: Short TTL + invalidation on subscription changes
- **Metering accuracy**: Eventual consistency acceptable for billing
- **Third-party API changes**: Version and monitor external APIs
- **Cost overruns**: Implement spending limits per tenant

---

## Implementation Plan

### Phase 1: Foundation (Sprint 1-2)
- [ ] Database schema migration
- [ ] Subscription domain model
- [ ] Basic entitlement service

### Phase 2: Integration (Sprint 3-4)
- [ ] Stripe integration + webhooks
- [ ] Usage metering service
- [ ] Entitlement middleware

### Phase 3: Core Features (Sprint 5-6)
- [ ] Billing portal (tenant-facing)
- [ ] Admin dashboard
- [ ] Usage alerts + notifications

### Phase 4: Premium Services - Design (Sprint 7-8)
- [ ] Figma API integration ([ADR-041])
- [ ] Image resizing service (imgproxy)
- [ ] Extended blob storage

### Phase 5: Premium Services - AI (Sprint 9-10)
- [ ] Custom AI provider (BYOK)
- [ ] AI product descriptions
- [ ] AI translation (DeepL)

### Phase 6: Premium Services - Legal (Sprint 11-12)
- [ ] e-recht24 integration
- [ ] Imprint generator
- [ ] Privacy policy generator
- [ ] T&C generator

### Phase 7: Premium Services - Business APIs (Sprint 13-14)
- [ ] Company verification (Creditreform)
- [ ] VAT validation (VIES)
- [ ] Address validation
- [ ] Bank verification (IBAN)

### Phase 8: Premium Services - Communication (Sprint 15+)
- [ ] Enhanced email (SendGrid)
- [ ] SMS notifications (Twilio)
- [ ] WhatsApp Business

---

## Related Decisions

- [ADR-004] PostgreSQL Multitenancy
- [ADR-025] Gateway-Service Communication
- [ADR-034] Multi-ERP Connector Architecture
- [ADR-041] Figma-based Tenant Design Integration

---

## References

- [Stripe Billing Documentation](https://stripe.com/docs/billing)
- [TimescaleDB Hypertables](https://docs.timescale.com/use-timescale/latest/hypertables/)
- [Feature Flag Best Practices](https://martinfowler.com/articles/feature-toggles.html)
- [e-recht24 API Documentation](https://api-docs.e-recht24.de)
- [Figma API Reference](https://www.figma.com/developers/api)
- [Azure Key Vault for Secrets](https://learn.microsoft.com/en-us/azure/key-vault/)

---

**Approval Required**: @Architect, @TechLead, @ProductOwner

