---
docid: ADR-091
title: ADR 047 Multishop Shared Catalog
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

---
docid: ADR-047
title: Multishop / Shared Catalogs Architecture
status: Proposed
owner: @Backend, @ProductOwner
created: 2026-01-06
---

# ADR-047: Multishop / Shared Catalogs Architecture

## Context

Some customers operate a central product catalog consumed by multiple shop tenants (multishop). They require central data maintenance with the ability to publish/share catalogs to downstream tenants while allowing limited tenant-specific overrides (pricing, availability, localized content).

This ADR documents the recommended architecture, data model, indexing and operational implications to support shared catalogs while respecting tenant isolation, performance and search consistency.

## Decision

Adopt a hybrid architecture that:

- Treats `Catalog` as a first-class entity (master catalog owned by a tenant)
- Allows explicit `CatalogShare` records to grant read/override permissions to target tenants
- Denormalizes category slugs and catalog identifiers into language-specific search indexes
- Supports both centralized indexing (central owner) and local indexing options for consuming tenants
- Provides configuration to present either product- or variant-oriented search results per-tenant

## Data Model (summary)

- `Catalog` (Id, OwnerTenantId, Name, DefaultLanguage, Metadata...)
- `CatalogShare` (CatalogId, TargetTenantId, Permissions {read, override}, AcceptedFlag, SharedAt)
- `Product` extended with `SourceCatalogId`, `SourceTenantId`, `OverridesSourceId` (nullable)
- Search index documents include `sourceCatalogId`, `sourceTenantId`, `isShared`, `originProductId` (for dedup/cardinality)

## Indexing & Search

- Continue language-specific indexes (e.g., `products_de`, `products_en`). Each document contains `sourceCatalogId` and `sourceTenantId`.
- Aggregations run against the effective index for the tenant: documents where `tenantId == currentTenant` OR `sourceCatalogId IN sharedCatalogsForTenant`.
- For shared catalogs, product counts and availability must be computed over the effective product set; use cardinality on `originProductId` for unique product counts when documents represent variants.
- Provide filters `sourceCatalogId` and `includeShared=true|false` in search API.
- Indexing options:
  - Central indexing: catalog owner pushes language-specific documents to shared indexes (preferred for single source of truth)
  - Local indexing: consumer tenant pulls and indexes a local copy (optional, for offline resilience/performance)

## Sharing Model & Overrides

- Default: shared catalog content is read-only for consumers.
- If `CatalogShare.permissions` allows `override`, consumers can create local overrides; overrides stored as separate product records with `overridesSourceId` linking to master product.
- Search/aggregation semantics combine local products and shared products (deduplicated by origin id) to form the effective result set.

## Tenant-level Inclusion / Exclusion Rules

Customers must be able to include or exclude specific categories, brands or products when consuming a shared catalog. This enables downstream shops to tailor the visible assortment without copying the whole catalog.

See also ADR-048 for a dedicated specification of Tenant-Level Include/Exclude Rules.

### Requirements
- Allow catalog owners or consuming tenants (depending on `CatalogShare.permissions`) to specify:
  - `includedCategorySlugs`: list of category slugs to include (whitelist)
  - `excludedCategorySlugs`: list of category slugs to exclude (blacklist)
  - `includedBrandIds` / `excludedBrandIds`
  - `includedProductIds` / `excludedProductIds`
- Inclusion/exclusion may apply at catalog-level or share-level (per target tenant)
- Exclusions should be enforced at query time and in aggregations
- Overrides of shared catalog must respect exclusion rules (local override cannot re-enable an excluded product unless permitted)

### Data Model Additions
- Extend `CatalogShare` with optional fields:
  - `IncludedCategorySlugs: string[]?`
  - `ExcludedCategorySlugs: string[]?`
  - `IncludedBrandIds: Guid[]?`
  - `ExcludedProductIds: Guid[]?`
  - `ApplyToAggregations: bool` (whether aggregation counts respect exclusion)

### Indexing & Query Semantics
- Index documents already contain `categories`, `brandId`, `productId`, `sourceCatalogId`, `sourceTenantId`.
- Search API will accept `includeCategories` / `excludeCategories`, `includeBrands` / `excludeProducts` parameters for tenant-scoped queries.
- Aggregations must apply the same filters as result queries so counts reflect the effective assortment. For variant-oriented indexes, use cardinality on `originProductId` after applying include/exclude filters.
- Example query pipeline for a consuming tenant:
  1. Resolve `sharedCatalogIds` for tenant
  2. Resolve effective include/exclude lists from `CatalogShare` records
  3. Build ES bool query:
     - Must: `(tenantId == currentTenant) OR (sourceCatalogId IN sharedCatalogIds)`
     - MustNot: `excludedProductIds` OR `categories.keyword IN excludedCategorySlugs` OR `brandId IN excludedBrandIds`
     - If `includedCategorySlugs` present: add Must: `categories.keyword IN includedCategorySlugs`

### UI Behaviour
- In owner UI: configure default inclusion/exclusion per catalog share
- In consumer UI: view effective include/exclude rules; request exceptions
- In Admin: audit trails for share rule changes

### Edge Cases & Rules
- If both included and excluded lists present, `excluded` takes precedence.
- Excluding a parent category excludes its descendant slugs unless a descendant is explicitly included.
- Performance: include/exclude lists should be limited (e.g., max 500 entries); large lists must be handled with temporary lists or precomputed filters.

### Caching
- Cache keys must incorporate include/exclude rules to avoid serving stale or unauthorized data across tenants.


## Security & Tenant Isolation

- All queries and aggregation endpoints must enforce tenant filtering and validate `CatalogShare` membership server-side.
- Catalog sharing UI and management restricted to owner and platform admins.
- Audit all share/grant/revoke events.

## API Surface (examples)

- `POST /api/catalogs/{catalogId}/share` — grant share to target tenant
- `GET  /api/catalogs/shared` — list catalogs shared with current tenant
- `GET  /api/catalogs/{id}/products?includeShared=true` — search products including shared catalogs
- `GET  /api/catalogs/{id}/metadata` — fetch catalog-level metadata (localized)

## UI / Admin

- Catalog owner UI: share/unshare, set permissions, view accepted consumers
- Consumer UI: accept/decline shared catalogs, manage overrides (if permitted)

## Migration & Operational Notes

- Introduce `sourceCatalogId` field to `ProductIndexDocument` and the DB schema; deploy in a backward-compatible way.
- Reindex strategy: central reindex by owner (alias switchover), or incremental reindex when a catalog is shared.
- Cache keys must include `tenantId` and `sourceCatalogId` (and language) to avoid cross-tenant leakage.
- Consider billing and quota for shared-catalog storage and indexing costs.

## Monitoring & Alerts

- Track number of shared catalogs, per-tenant shared-product counts
- Monitor aggregation latency for shared queries (p95 target < 200ms)
- Alert on unauthorized access attempts to shared content

## Consequences

- Pros: enables centralized data maintenance, reduces duplication of editorial work, supports multishop scenarios
- Cons: added complexity in search queries, indexing, and permission handling; potential storage and indexing cost increase

## Alternatives Considered

- Replicate-only: fully replicate central catalog into each tenant only (simpler but increases storage and complexity)
- Proxy queries to owner tenant: consumer tenants proxy queries to owner (simple but couples availability and latency)

---



