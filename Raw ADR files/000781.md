---
docid: ADR-067
title: ADR 028 Erp Bidirectional Integration
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ERP Bidirectional Integration Architecture

**Status:** Proposed  
**Date:** January 3, 2026  
**Context:** enventa Trade ERP needs API access to B2X for customer updates, access management, usage stats, and product data synchronization  
**Decision Authors:** @Architect, @Backend

---

## Problem

enventa Trade ERP currently uses RESTier.NET over OData to access B2X, but this creates security and architectural challenges:

- **Security Gap**: ERP can access B2X APIs without proper authentication boundaries
- **Tight Coupling**: Direct OData exposure creates tight coupling between systems
- **No Tenant Isolation**: ERP operations aren't properly scoped to tenants
- **Legacy Technology**: RESTier.NET/OData may not align with modern .NET 10 architecture

## Solution: Secure Bidirectional API Gateway

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        enventa Trade ERP                            │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    ERP Service Account                         │  │
│  │  - API Key: "erp-service.tenant1.XXXX"                        │  │
│  │  - Permissions: ERP operations only                          │  │
│  │  - Encrypted credentials stored in ERP Connector             │  │
│  └────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │ HTTPS + API Key
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      B2X API Gateway                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   ERP Gateway   │    │  Auth Service   │    │  CQRS Bus       │  │
│  │   (/api/erp/*)  │◄───┤  (JWT/API Key)  │◄───┤  (Wolverine)    │  │
│  │                 │    │                 │    │                 │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│  │                                                                  │
│  ├─ /api/erp/customers/sync ──────────────────────────────────────┐  │
│  ├─ /api/erp/products/update ────────────────────────────────────┐  │
│  ├─ /api/erp/access/validate ───────────────────────────────────┐  │
│  └─ /api/erp/usage/stats ──────────────────────────────────────┐  │
│                                                               │  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │  ERP Commands   │    │  ERP Queries    │    │  ERP Events     │  │
│  │  (Write Ops)    │    │  (Read Ops)     │    │  (Async)        │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Security Model

#### 1. ERP Service Accounts
- **Dedicated API Keys**: `erp-service.{tenant}.{suffix}` format
- **Limited Permissions**: ERP operations only (no admin/customer access)
- **Tenant-Scoped**: Each tenant gets separate ERP service account
- **Zero-Trust**: Credentials encrypted in ERP Connector with DPAPI

#### 2. API Gateway Isolation
- **Dedicated Route**: `/api/erp/*` prefix for ERP operations
- **Authentication Required**: API key validation on all ERP endpoints
- **Authorization**: Role-based access (`ErpService` role)
- **Rate Limiting**: Prevent abuse from ERP side

### Implementation Plan

#### Phase 1: ERP Service Account Infrastructure
```csharp
// Models/ErpServiceAccount.cs
public class ErpServiceAccount
{
    public string TenantId { get; set; }
    public string ApiKey { get; set; } // Encrypted with DPAPI
    public HashSet<string> AllowedOperations { get; set; }
    public DateTime CreatedAt { get; set; }
    public bool IsActive { get; set; }
}
```

#### Phase 2: ERP Gateway API
```csharp
// Controllers/ErpGatewayController.cs
[ApiController]
[Route("api/erp")]
[Authorize(Roles = "ErpService")]
public class ErpGatewayController : ControllerBase
{
    [HttpPost("customers/sync")]
    public async Task<IActionResult> SyncCustomers([FromBody] CustomerSyncRequest request)
    {
        // CQRS command for customer sync
    }

    [HttpPut("products/{productId}")]
    public async Task<IActionResult> UpdateProduct(string productId, [FromBody] ProductUpdateRequest request)
    {
        // CQRS command for product update
    }

    [HttpPost("access/validate")]
    public async Task<IActionResult> ValidateAccess([FromBody] AccessValidationRequest request)
    {
        // Query for access validation
    }
}
```

#### Phase 3: CQRS Integration
```csharp
// Commands/ErpSyncCustomersCommand.cs
public record ErpSyncCustomersCommand(string TenantId, CustomerSyncRequest Request)
    : ICommand<CustomerSyncResponse>;

// Handlers/ErpSyncCustomersHandler.cs
public class ErpSyncCustomersHandler
{
    public async Task<CustomerSyncResponse> Handle(ErpSyncCustomersCommand command)
    {
        // Business logic for customer sync
        // Publish events for side effects
    }
}
```

### Migration Strategy

#### Option A: Maintain RESTier.NET (Recommended for Compatibility)
```csharp
// Keep existing OData endpoints but add authentication
[ODataRoute("Customers")]
[Authorize(Roles = "ErpService")]
public IQueryable<Customer> GetCustomers()
{
    // Existing RESTier logic with auth
}
```

#### Option B: Migrate to CQRS API
```csharp
// New CQRS-based endpoints
[HttpPost("customers/query")]
[Authorize(Roles = "ErpService")]
public async Task<IActionResult> QueryCustomers([FromBody] CustomerQuery query)
{
    var result = await _bus.InvokeAsync<CustomerQueryResponse>(query);
    return Ok(result);
}
```

### Benefits

#### ✅ Security
- **Zero-Trust**: ERP credentials never leave encrypted storage
- **Least Privilege**: ERP service accounts have minimal permissions
- **Audit Trail**: All ERP operations logged and traceable

#### ✅ Architecture
- **Loose Coupling**: Event-driven integration between systems
- **Scalability**: CQRS pattern handles high-volume operations
- **Maintainability**: Clear separation of concerns

#### ✅ Operations
- **Monitoring**: Built-in metrics and health checks
- **Rate Limiting**: Prevent ERP from overwhelming B2X
- **Circuit Breaker**: Fail gracefully if ERP is unavailable

### Implementation Steps

1. **Create ERP Service Account Infrastructure**
   - Extend ApiKeyManager for ERP service accounts
   - Add DPAPI encryption for ERP credentials
   - Create admin endpoints for ERP account management

2. **Build ERP Gateway API**
   - New controller with `/api/erp/*` routes
   - Authentication middleware for ERP service accounts
   - CQRS command/query handlers

3. **Migrate Existing OData Endpoints**
   - Add authentication to existing RESTier endpoints
   - Gradually migrate to CQRS pattern
   - Maintain backward compatibility

4. **Testing & Deployment**
   - Unit tests for all ERP operations
   - Integration tests with ERP connector
   - Production deployment with monitoring

---

## Alternatives Considered

### Alternative 1: Direct Database Access
**Rejected**: Violates microservices principles, creates tight coupling

### Alternative 2: Shared Message Queue
**Deferred**: Could be added later for event-driven integration

### Alternative 3: Webhook-Only Integration
**Insufficient**: ERP needs synchronous operations for customer/product updates

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| ERP Service Account Compromise | Short-lived tokens, regular rotation, audit logging |
| Performance Impact | Rate limiting, circuit breakers, async processing |
| Data Consistency | Eventual consistency with compensating actions |
| Backward Compatibility | Gradual migration, feature flags |

---

**Recommendation**: Implement the Secure Bidirectional API Gateway with ERP service accounts. This maintains your existing RESTier.NET investment while adding proper security boundaries and modern CQRS architecture.

**Next Steps**:
1. Create ADR for ERP service account pattern
2. Implement ERP gateway infrastructure
3. Add authentication to existing OData endpoints
4. Test with enventa Trade ERP integration</content>
<parameter name="filePath">c:\Users\Holge\repos\B2X\.ai\decisions\ADR-028-erp-bidirectional-integration.md