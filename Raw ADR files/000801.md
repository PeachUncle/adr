---
docid: ADR-092
title: ADR 048 Tenant Level Include Exclude
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

---
docid: ADR-048
title: Tenant-Level Include/Exclude Rules for Shared Catalogs
owner: @SARAH
status: Proposed
---

## Context

Shared catalogs allow one tenant to publish a catalog that other tenants can consume. Consumers often need to tailor a shared catalog by including or excluding subsets of categories, brands, or individual products without copying the entire catalog.

## Decision

Introduce a dedicated architecture decision capturing tenant-level include/exclude rules as a first-class feature. These rules are stored on the `CatalogShare` object and enforced at query/indexing time so that search results and aggregations reflect the consuming tenant's effective assortment.

## Rationale

- Splitting this concern into its own ADR keeps the sharing model, security, and query semantics focused and reviewable.
- Enforcing rules at query time (rather than copying/duplicating data) keeps storage minimal and supports immediate changes.

## Model

Extend `CatalogShare` with optional parameters scoped to a specific consumer tenant:

- `IncludedCategorySlugs: string[]?`
- `ExcludedCategorySlugs: string[]?`
- `IncludedBrandIds: Guid[]?`
- `ExcludedBrandIds: Guid[]?`
- `IncludedProductIds: Guid[]?`
- `ExcludedProductIds: Guid[]?`
- `ApplyToAggregations: bool` (default true)

### Scope: Tenant and Customer-level Rules

The rules feature must support more granular targets than just the consuming tenant. In B2B scenarios customers (accounts) or customer groups can have custom assortments. To support this, rules are modelled with a target scope and identifier.

- `TargetType: enum { Tenant, Customer, CustomerGroup }`
- `TargetId: Guid` (the id of the tenant, customer or group)

Rules are stored as a collection of scoped rule-sets on `CatalogShare` (or in a dedicated `CatalogShareRule` table depending on normalization preferences). Each rule-set includes the include/exclude lists and a `Priority` and `Active` flag.

Example storage options:
- Inline (JSON arrays) on `CatalogShare` with an array of `{ TargetType, TargetId, IncludedCategorySlugs, ExcludedCategorySlugs, ... }`
- Normalized table `CatalogShareRule` with FK to `CatalogShare` and columns for scope, lists (JSON), priority and metadata.

Additionally maintain `permissions` on `CatalogShare` to control whether the consumer may request exceptions or overrides.

## Query & Indexing Semantics

1. Resolve `sharedCatalogIds` for the consuming tenant.
2. Merge include/exclude lists (owner defaults, plus share-level overrides, plus consumer-specific exceptions if permitted).
3. Build an ES bool query:
   - Must: `(tenantId == currentTenant) OR (sourceCatalogId IN sharedCatalogIds)`
   - MustNot: `excludedProductIds` OR `categories.keyword IN excludedCategorySlugs` OR `brandId IN excludedBrandIds`
   - If `includedCategorySlugs` present: add Must: `categories.keyword IN includedCategorySlugs`

   ### Rule Resolution & Precedence

   When multiple rule-sets apply for a request (e.g., tenant defaults, customer group, specific customer), resolve precedence as follows:

   1. Customer-specific rules (TargetType=Customer, TargetId=currentCustomer)
   2. CustomerGroup rules (TargetType=CustomerGroup, groups that the customer belongs to; higher priority wins)
   3. Tenant-level rules (TargetType=Tenant)
   4. Catalog-owner defaults

   Higher-priority rules may override includes/excludes from lower-priority rules. By convention `Excluded` always wins over `Included` unless an explicit `AllowOverride` flag is present on the higher-priority rule.

   ### Request-time Inputs

   Search API will receive the current context (tenantId, optional customerId) and must:

   1. Resolve applicable `sharedCatalogIds` for the tenant
   2. Fetch all `CatalogShareRule` entries that match `sharedCatalogIds` and the requesting context (tenant, customer groups, customer)
   3. Merge rule-sets by precedence into a single effective include/exclude filter
   4. Apply the effective filter to both hits and aggregations

   ### Caching & Performance

   - Cache keys must include `tenantId`, `customerId` (if present), `catalogShareIds`, and a fingerprint of the resolved rule-set.
   - For customers with high-volume rulesets, precompute effective filters and store as indexed filter aliases in Elasticsearch to avoid repeated large bool queries.


For variant-oriented indexes, apply the final filters before performing aggregations; use `cardinality` on `originProductId` to deduplicate product counts.

## UI and Admin

- Owner UI: define default include/exclude lists per share and permissions.
- Consumer UI: view effective rules and request exceptions.
- Admin: audit logs for rule changes and appeals.

## Security & Performance

- All queries must enforce tenant isolation.
- Include/exclude lists must be size-limited (configurable, e.g., 500 entries) and large lists handled via precomputed filters or temporary index aliases to avoid query bloat.
- Cache keys must include share id and serialized include/exclude fingerprint.

## Migration

- Add new nullable columns to `CatalogShare` for the lists (JSON arrays) via a migration.
- Backfill not required; new shares will populate fields as needed.

## Consequences

- Aggregation and search results will reflect consumer-specific visibility.
- Slightly more complex query composition in `SearchIndexService` and controllers.

## See Also

- ADR-047: Multishop / Shared Catalogs
