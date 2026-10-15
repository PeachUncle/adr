---
docid: ADR-056
title: ADR 022 Multi Tenant Domain Management
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-022: Multi-Tenant Domain Management Strategy

**Status**: Proposed  
**Date**: 2025-01-02  
**Deciders**: @Architect, @Backend, @DevOps, @Security  
**DocID**: `ADR-022`

---

## Context

B2X ist eine Multi-Tenant SaaS E-Commerce Plattform. Aktuell existiert grundlegende Tenant-Isolation (TenantId in Entities, Middleware für Context), aber es fehlt:

1. **Dynamische Tenant-Erstellung** über Management UI
2. **Domain-Management** (Custom Domains für Tenants)
3. **Self-Service** für Tenant-Administratoren

### Aktueller Stand

| Komponente | Status |
|------------|--------|
| Tenant Entity | ✅ Vorhanden (Name, Slug, Status) |
| TenantContext Middleware | ✅ JWT + Header + Host-Lookup |
| Domain-zu-Tenant Mapping | ❌ Fehlt (hardcoded/config-based) |
| Management API | ❌ Fehlt |
| Management UI | ❌ Fehlt |

### Anforderungen

- Tenants sollen über Management-Frontend erstellt werden können
- Jeder Tenant benötigt mindestens eine Domain (Subdomain oder Custom)
- Custom Domains müssen verifiziert werden (DNS-Check)
- SSL-Zertifikate müssen automatisch verwaltet werden
- Domain-Lookup muss performant sein (<50ms)

---

## Decision

Wir implementieren eine **Hybrid Domain Strategy** mit folgenden Komponenten:

### 1. Domain-Typen

| Typ | Format | SSL | Verifizierung |
|-----|--------|-----|---------------|
| **Subdomain** (automatisch) | `{slug}.B2X.de` | Wildcard-Cert | Keine (automatisch) |
| **Custom Domain** (optional) | `shop.kundendomain.de` | Let's Encrypt | DNS TXT Record |

### 2. Datenmodell

```
┌─────────────────────────────────────────────────────────────┐
│                        Tenant                                │
├─────────────────────────────────────────────────────────────┤
│ Id: Guid (PK)                                               │
│ Name: string                                                │
│ Slug: string (unique) → generiert Subdomain                 │
│ Status: TenantStatus                                        │
│ ...                                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 1:n
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      TenantDomain                           │
├─────────────────────────────────────────────────────────────┤
│ Id: Guid (PK)                                               │
│ TenantId: Guid (FK)                                         │
│ DomainName: string (unique) z.B. "shop.example.com"         │
│ Type: DomainType (Subdomain | CustomDomain)                 │
│ IsPrimary: bool                                             │
│ VerificationStatus: Pending | Verified | Failed             │
│ VerificationToken: string? (für DNS TXT)                    │
│ VerificationExpiresAt: DateTime?                            │
│ VerifiedAt: DateTime?                                       │
│ SslStatus: None | Provisioning | Active | Expired           │
│ SslExpiresAt: DateTime?                                     │
│ CreatedAt: DateTime                                         │
│ UpdatedAt: DateTime                                         │
└─────────────────────────────────────────────────────────────┘
```

### 3. Domain Resolution Flow

```
                    Incoming Request
                          │
                          ▼
               ┌──────────────────┐
               │  Extract Host    │
               │  Header          │
               └────────┬─────────┘
                        │
                        ▼
               ┌──────────────────┐
               │  Cache Lookup    │◄──── Redis/Memory Cache
               │  (TenantId)      │      TTL: 5 min
               └────────┬─────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
         Cache Hit           Cache Miss
              │                   │
              ▼                   ▼
       Return TenantId    ┌──────────────────┐
                          │  DB Lookup       │
                          │  TenantDomains   │
                          └────────┬─────────┘
                                   │
                          ┌────────┴────────┐
                          │                 │
                       Found            Not Found
                          │                 │
                          ▼                 ▼
                   Cache & Return      404 / Redirect
                      TenantId         to Landing Page
```

### 4. Custom Domain Verification Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   Custom Domain Verification                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. User adds custom domain "shop.example.com"                  │
│     └─► System generates verification token                     │
│         Token: "b2c-verify-{random-256bit-hex}"                 │
│                                                                 │
│  2. User configures DNS:                                        │
│     └─► TXT Record: _B2X.shop.example.com                 │
│         Value: "b2c-verify-abc123..."                           │
│     └─► CNAME Record: shop.example.com                          │
│         Target: proxy.B2X.de                              │
│                                                                 │
│  3. User clicks "Verify Domain"                                 │
│     └─► System checks DNS TXT record                            │
│     └─► If match: VerificationStatus = Verified                 │
│     └─► If fail: VerificationStatus = Failed + Retry allowed    │
│                                                                 │
│  4. After verification:                                         │
│     └─► Trigger SSL provisioning (Let's Encrypt)                │
│     └─► Domain becomes active when SSL ready                    │
│                                                                 │
│  Timeout: 72 hours from token generation                        │
│  Retries: Unlimited within timeout                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5. API Endpoints

#### Tenant Management (Admin Gateway)

```
POST   /api/admin/tenants
       → CreateTenantCommand { Name, Slug, AdminEmail }
       ← { TenantId, Subdomain }

GET    /api/admin/tenants
       → GetTenantsQuery { Page, PageSize, Status?, Search? }
       ← { Items[], TotalCount }

GET    /api/admin/tenants/{id}
       → GetTenantQuery { Id }
       ← TenantDetailDto

PUT    /api/admin/tenants/{id}
       → UpdateTenantCommand { Name, Status, Settings }
       ← TenantDetailDto

DELETE /api/admin/tenants/{id}
       → ArchiveTenantCommand { Id }
       ← { Success }
```

#### Domain Management

```
GET    /api/admin/tenants/{tenantId}/domains
       → GetDomainsQuery { TenantId }
       ← DomainDto[]

POST   /api/admin/tenants/{tenantId}/domains
       → AddDomainCommand { TenantId, DomainName, SetAsPrimary? }
       ← { DomainId, VerificationToken, DnsInstructions }

DELETE /api/admin/tenants/{tenantId}/domains/{domainId}
       → RemoveDomainCommand { TenantId, DomainId }
       ← { Success }

POST   /api/admin/domains/{domainId}/verify
       → VerifyDomainCommand { DomainId }
       ← { Status, ErrorMessage? }

POST   /api/admin/domains/{domainId}/set-primary
       → SetPrimaryDomainCommand { DomainId }
       ← { Success }
```

### 6. Infrastructure Architecture

```
                                 Internet
                                    │
                                    ▼
                         ┌──────────────────┐
                         │   Cloudflare     │
                         │   (DNS + CDN)    │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
           *.B2X.de              Custom Domains
           (Wildcard Cert)             (Let's Encrypt)
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Traefik      │
                         │  (Ingress/LB)    │
                         │                  │
                         │  - Dynamic Host  │
                         │    Routing       │
                         │  - TLS Term.     │
                         │  - Auto HTTPS    │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
           ┌──────────────┐            ┌──────────────┐
           │ Store API    │            │ Admin API    │
           │ (B2C/B2B)    │            │ (Management) │
           └──────────────┘            └──────────────┘
```

### 7. Caching Strategy

| Cache Layer | TTL | Invalidation |
|-------------|-----|--------------|
| Traefik Route Cache | 30s | On domain change event |
| Application Memory Cache | 5 min | On domain CRUD |
| Redis Distributed Cache | 10 min | On domain CRUD + TTL expiry |

**Cache Key Pattern**: `tenant:domain:{normalized-domain-name}`

**Cache Value**: `{ TenantId, Status, IsPrimary }`

---

## Alternatives Considered

### Alternative 1: Database-per-Tenant

**Beschreibung**: Jeder Tenant erhält eigene Datenbank.

| Pro | Contra |
|-----|--------|
| Maximale Isolation | Hohe Infrastrukturkosten |
| Einfaches Backup/Restore pro Tenant | Connection Pool Explosion |
| Unabhängige Skalierung | Komplexes Migrations-Management |

**Entscheidung**: Abgelehnt — zu kostspielig für 100+ Tenants.

### Alternative 2: Schema-per-Tenant

**Beschreibung**: Ein Schema pro Tenant in shared Database.

| Pro | Contra |
|-----|--------|
| Gute Isolation | Dynamische Schema-Erstellung komplex |
| Einfacheres Tenant-Backup | EF Core Schema-Switching aufwändig |

**Entscheidung**: Abgelehnt — Row-Level Security ist flexibler.

### Alternative 3: Nur Subdomains (kein Custom Domain Support)

**Beschreibung**: Nur `{slug}.B2X.de` erlauben.

| Pro | Contra |
|-----|--------|
| Sehr einfach | Kunden wollen eigene Domains |
| Ein Wildcard-Cert reicht | Weniger professionell |

**Entscheidung**: Abgelehnt — Custom Domains sind wichtig für Enterprise-Kunden.

---

## Consequences

### Positive

1. **Flexibilität**: Kunden können Subdomain oder Custom Domain wählen
2. **Self-Service**: Tenant-Erstellung automatisiert, kein manueller Eingriff
3. **Skalierbarkeit**: Domain-Lookup via Cache performant (<10ms)
4. **Security**: DNS-Verifizierung verhindert Domain-Hijacking
5. **Operations**: SSL automatisch via Let's Encrypt

### Negative

1. **Komplexität**: DNS-Verifizierung und SSL-Management hinzugefügt
2. **Infrastructure**: Traefik/Ingress muss dynamisch konfigurierbar sein
3. **Support**: Kunden benötigen ggf. Hilfe bei DNS-Konfiguration

### Neutral

1. Zusätzliche Dokumentation für Kunden (DNS Setup Guide)
2. Monitoring für SSL-Expiry erforderlich

---

## Implementation Plan

### Phase 1: Backend Foundation (Sprint 1)

- [ ] TenantDomain Entity + EF Migration
- [ ] ITenantDomainRepository
- [ ] Domain-Lookup Service (+ Caching)
- [ ] Tenant CRUD Wolverine Handlers
- [ ] Domain Management Wolverine Handlers
- [ ] Unit Tests

### Phase 2: DNS & SSL (Sprint 2)

- [ ] DNS Verification Service (TXT Record Check)
- [ ] Let's Encrypt Integration (ACME Client)
- [ ] Background Job: SSL Provisioning
- [ ] Background Job: SSL Renewal Check
- [ ] Integration Tests

### Phase 3: Management UI (Sprint 3)

- [ ] Tenant List Page
- [ ] Tenant Create Wizard
- [ ] Tenant Detail Page
- [ ] Domain Manager Component
- [ ] DNS Instructions Component
- [ ] E2E Tests

### Phase 4: Infrastructure (Sprint 4)

- [ ] Traefik IngressRoute CRDs (K8s)
- [ ] Cert-Manager Integration
- [ ] Cloudflare DNS API (optional)
- [ ] Monitoring & Alerts

---

## Security Considerations

| Threat | Mitigation |
|--------|------------|
| Domain Hijacking | DNS TXT verification required |
| Tenant Spoofing | JWT tenant claim validation |
| DNS Rebinding | Strict domain validation regex |
| SSL Downgrade | HSTS headers, force HTTPS |
| Token Guessing | 256-bit random tokens |
| Brute Force Verify | Rate limiting (5 req/min) |

---

## References

- [ADR-001: Event-Driven Architecture](./ADR-001-event-driven-architecture.md)
- [Tenant Isolation Documentation](../../backend/docs/tenant-isolation.md)
- [Let's Encrypt ACME Protocol](https://letsencrypt.org/docs/client-options/)
- [Traefik IngressRoute](https://doc.traefik.io/traefik/routing/providers/kubernetes-crd/)

---

## Decision Outcome

**Gewählt: Hybrid Domain Strategy** (Subdomain + Custom Domain Support)

Diese Lösung bietet die beste Balance zwischen:
- Einfachheit für neue Tenants (automatische Subdomain)
- Flexibilität für Enterprise-Kunden (Custom Domains)
- Sicherheit (DNS-Verifizierung)
- Skalierbarkeit (Caching, verteilte Architektur)

---

**Approved by**:
- [ ] @Architect
- [ ] @TechLead  
- [ ] @Security
- [ ] @DevOps

**Date**: ___________
